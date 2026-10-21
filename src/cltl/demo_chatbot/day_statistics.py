"""Basic statistics of a day file, such as the example days in data/example_days or the days collected by the
DayInterviewer: the number of events, the number of filled roles, the coreference chains and the values of what and
with_what with their frequencies. The statistics are saved next to the day file as <name>_meta.json.

Run it from the root of the project with one or more day files or folders with day files:

    python -m src.cltl.demo_chatbot.day_statistics data/example_days data/collected_days/day_fred_20261020_1518.json
"""
import argparse
import glob
import json
import os
from collections import Counter

# The roles of an event that describe the situation, as in the example days
ROLES = ["who", "what", "with_what", "with_whom", "where", "when", "how_long"]
META_SUFFIX = "_meta"
# The files next to the days that are not days: the statistics and the results of the evaluation
NOT_DAY_SUFFIXES = (META_SUFFIX, "_evaluation", "_effectiveness")
# In the example days, a role that is shown on a photo has this placeholder, its value is in the gold of the photo
PHOTO_PLACEHOLDER = "<PHOTO>"


def get_events(day):
    return {key: event for key, event in day.items() if key.startswith("event")}

## TURNS
def make_turn(turn_id, utterance):
    """A turn in agent_turn or human_turn: the utterance with the number of the turn in the conversation."""
    return {"turn_id": turn_id, "utterance": utterance}

def get_turns(event, field="human_turn"):
    """The turns of an event in agent_turn or human_turn as a list of {"turn_id": ..., "utterance": ...}.
    Older files have a list of utterances or a single string, these turns get their position in the list as id."""
    turns = event.get(field, [])
    turns = [turns] if isinstance(turns, str) else turns
    return [turn if isinstance(turn, dict) else make_turn(i + 1, turn) for i, turn in enumerate(turns)]

def get_utterances(event, field="human_turn"):
    """The utterances of the turns of an event in agent_turn or human_turn, see get_turns."""
    return [turn["utterance"] for turn in get_turns(event, field)]

def is_from_photo(event, role):
    return event.get(role) == PHOTO_PLACEHOLDER

def get_role_value(event, role):
    """The value of a role, taken from the gold of the photo if the role is shown on a photo."""
    if is_from_photo(event, role):
        return event.get("photo", {}).get("gold", {}).get(role)
    return event.get(role)

def get_role_values(event, role):
    """The values of a role as a list, a single value such as a string is a list with one value."""
    value = get_role_value(event, role)
    if value is None or value == "" or value == []:
        return []
    return value if isinstance(value, list) else [value]

def get_value_frequencies(events, role):
    """The unique values of a role with the number of events in which they are mentioned, most frequent first."""
    counts = Counter(value for event in events.values() for value in get_role_values(event, role))
    return dict(counts.most_common())

def get_day_statistics(day):
    events = get_events(day)
    role_counts = {role: sum(1 for event in events.values() if get_role_values(event, role)) for role in ROLES}
    photo_counts = {role: sum(1 for event in events.values() if is_from_photo(event, role)) for role in ROLES}
    chains = day.get("coreference_chains", [])
    nr_of_mentions = [len(chain.get("mentions", [])) for chain in chains]
    what = get_value_frequencies(events, "what")
    with_what = get_value_frequencies(events, "with_what")
    return {
        "nr_of_events": len(events),
        # the number of filled roles over all events and per role
        "nr_of_roles": sum(role_counts.values()),
        "nr_of_roles_per_role": role_counts,
        # roles of which the value is shown on a photo, these are included in the counts above
        "nr_of_roles_from_photos": sum(photo_counts.values()),
        "nr_of_coreference_chains": len(chains),
        "average_nr_of_mentions_per_chain": round(sum(nr_of_mentions) / len(chains), 2) if chains else 0,
        "nr_of_mentions_per_chain": {chain.get("entity_id", ""): count for chain, count in zip(chains, nr_of_mentions)},
        "nr_of_unique_what": len(what),
        "what": what,
        "nr_of_unique_with_what": len(with_what),
        "with_what": with_what,
    }

def get_meta_path(day_file):
    name, extension = os.path.splitext(day_file)
    return name + META_SUFFIX + extension

def save_day_statistics(day_file):
    """Computes the statistics of a day file and saves them as <name>_meta.json next to it."""
    with open(day_file) as json_file:
        day = json.load(json_file)
    statistics = get_day_statistics(day)
    meta_file = get_meta_path(day_file)
    with open(meta_file, "w") as json_file:
        json.dump(statistics, json_file, indent=2, ensure_ascii=False)
    return meta_file, statistics

def get_day_files(paths):
    """The day files in the given files and folders, skipping the files with statistics and evaluation results."""
    day_files = []
    for path in paths:
        files = sorted(glob.glob(os.path.join(path, "*.json"))) if os.path.isdir(path) else [path]
        day_files.extend(file for file in files if not os.path.splitext(file)[0].endswith(NOT_DAY_SUFFIXES))
    return day_files

def print_statistics(day_file, statistics):
    print(day_file)
    print(f"  events: {statistics['nr_of_events']}")
    print(f"  roles: {statistics['nr_of_roles']} {statistics['nr_of_roles_per_role']}")
    print(f"  coreference chains: {statistics['nr_of_coreference_chains']}, "
          f"average mentions per chain: {statistics['average_nr_of_mentions_per_chain']}")
    print(f"  unique what: {statistics['nr_of_unique_what']} {statistics['what']}")
    print(f"  unique with_what: {statistics['nr_of_unique_with_what']} {statistics['with_what']}")


def main():
    parser = argparse.ArgumentParser(description="Basic statistics of day files, saved as <name>_meta.json")
    parser.add_argument("paths", nargs="+", help="Day files or folders with day files")
    args = parser.parse_args()

    day_files = get_day_files(args.paths)
    if not day_files:
        print("No day files found in", args.paths)
    for day_file in day_files:
        meta_file, statistics = save_day_statistics(day_file)
        print_statistics(day_file, statistics)
        print("  saved to", meta_file)


if __name__ == "__main__":
    main()
