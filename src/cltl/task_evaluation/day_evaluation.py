"""Evaluates a day description collected by an agent, such as the DayInterviewer, against a GOLD day description,
such as the example days in data/example_days. Both are JSON files with event1, event2, ... and coreference_chains.

The evaluation is done on three levels, each with a contingency table (true positives, false positives,
false negatives and true negatives) and the precision, recall and f1:

* events: the events of the collected day are aligned one-to-one with the GOLD events, using the start time and
  the overlap in time, the event type and the event label. An event without a clock time, e.g. with only
  'morning' in when, gets half the time similarity if the other event starts in that part of the day. Aligned events are true positives, collected
  events without a GOLD event are false positives and GOLD events without a collected event are false negatives.
* roles: for each role (who, what, with_what, with_whom, where, when, how_long) of an event: is the role filled?
  A role filled in both events is a true positive, a role filled in the collected event only a false positive,
  a role filled in the GOLD event only a false negative and a role that is empty in both a true negative.
* role-fillers: the values of the roles. The values of aligned events are matched one-to-one, matched values are
  true positives, collected values without a match are false positives and GOLD values without a match are
  false negatives. With a partial match, e.g. a Jaccard score of 0.5, half a value counts as true positive and
  half as false positive and false negative.

The roles and role-fillers of events that are not aligned count as false positives or false negatives.
True negatives are only defined for roles: there is no fixed set of events or values that could have been
collected, so for events and role-fillers they are reported as n/a.

The values are compared in two modes:

* exact: the labels are the same, ignoring case and spaces
* jaccard: the overlap of the words of the labels (Jaccard), ignoring words such as 'the', 'of' and 'his', so that
  a label that is a substring of the other also partly matches, e.g. 'alarm' and 'phone alarm' score 0.5

In both modes:

* where and when are lists from the most specific to the most general value, e.g. ['kitchen', 'her flat',
  'Amsterdam', 'Netherlands', 'Europe'] or ['07:30', 'half past seven', "7 o'clock", 'early in the morning',
  'morning']. They are weighted by the specificity of the match: matching the GOLD value at position i of n
  scores (n - i) / n, so the most specific value scores 1 and 'Europe' only 1/n. The best match counts.
* who and with_whom are matched through the coreference chains: two mentions match if their entities are aligned,
  e.g. 'his wife Gerda' and 'Gerda'. The entities are aligned on their names and mentions. Mentions without
  an entity are compared as labels.
* how_long matches exactly in exact mode and by the ratio of the shortest to the longest duration in jaccard mode.

Run it from the root of the project:

    python -m src.cltl.task_evaluation.day_evaluation --key data/example_days/day1_emma_student.json \
        --collected data/collected_days/day_emma_20261021_1100.json

The results are printed and saved as <collected>_vs_<gold>_evaluation.json next to the collected day.
With max_gold_events (--max-gold-events), only the first events of the GOLD day are evaluated, e.g. when the
conversation stopped early: a number of events, or "collected" for as many GOLD events as the collected day has.

Each aligned event in event_alignment has a comment that explains its similarity (time, type and label) and the
roles of which the values do not fully match the GOLD, with their score.
The evaluation per turn of the user is saved as <collected>_vs_<gold>_turn_evaluation.csv, in the same format as the
evaluation files of the EMISSOR scenarios, so that it can be plotted with the plots module (see save_turn_evaluation).
"""
import argparse
import csv
import json
import os
import re

import numpy as np
from scipy.optimize import linear_sum_assignment

from src.cltl.demo_chatbot.day_statistics import get_events, get_role_values, get_turns, get_utterances

ROLES = ["who", "what", "with_what", "with_whom", "where", "when", "how_long"]
COREFERENCE_ROLES = ["who", "with_whom"]
SPECIFICITY_ROLES = ["where", "when"]
MODES = ["exact", "jaccard"]

# Words that are ignored in the Jaccard match
STOPWORDS = {"a", "an", "the", "of", "in", "at", "on", "to", "from", "with", "and", "for", "by",
             "his", "her", "their", "my", "its", "our", "your", "o'clock"}

# Minimal similarity of two events to align them, see get_event_similarity
EVENT_THRESHOLD = 0.55
# The hours (from, to) of the parts of the day in when, for events without a clock time
PART_OF_DAY_HOURS = {"night": (0, 5), "morning": (5, 12), "midday": (12, 13), "afternoon": (12, 18),
                     "evening": (18, 24)}
# The time similarity of an event without a clock time and an event that starts in its part of the day
PART_OF_DAY_SIMILARITY = 0.5
# Minimal similarity of the names and mentions of two entities to align them, per mode
ENTITY_THRESHOLDS = {"exact": 1.0, "jaccard": 0.5}


## MATCHING LABELS
def normalize(text):
    return re.sub(r"\s+", " ", str(text).lower()).strip(" .,;:!?")

def get_words(text):
    # times without a leading zero, so that 7:30 and 07:30 are the same word
    words = {re.sub(r"^0(\d:)", r"\1", word) for word in re.findall(r"[a-z0-9:']+", normalize(text))}
    return words - STOPWORDS

def exact_match(gold, system):
    return 1.0 if normalize(gold) == normalize(system) else 0.0

def jaccard_match(gold, system):
    if exact_match(gold, system):
        return 1.0
    gold_words, system_words = get_words(gold), get_words(system)
    if not gold_words or not system_words:
        return 0.0
    return len(gold_words & system_words) / len(gold_words | system_words)

MATCHES = {"exact": exact_match, "jaccard": jaccard_match}

def specificity_match(gold_values, system_values, match):
    """Matches a list from the most specific to the most general value: the best match of a GOLD value with any of
    the collected values, weighted by its specificity (n - i) / n for position i of n GOLD values."""
    n = len(gold_values)
    return max((n - i) / n * max(match(gold, system) for system in system_values)
               for i, gold in enumerate(gold_values))

def duration_match(gold, system, mode):
    if not isinstance(gold, (int, float)) or not isinstance(system, (int, float)):
        return exact_match(gold, system)
    if mode == "exact":
        return 1.0 if gold == system else 0.0
    return min(gold, system) / max(gold, system) if gold > 0 and system > 0 else 0.0

def assign(nr_of_gold, nr_of_system, score):
    """The one-to-one assignment of GOLD and collected items with the highest total score.
    score(i, j) gives the score of GOLD item i and collected item j. Returns (i, j, score) for pairs above 0."""
    if not nr_of_gold or not nr_of_system:
        return []
    matrix = np.array([[score(i, j) for j in range(nr_of_system)] for i in range(nr_of_gold)])
    rows, columns = linear_sum_assignment(matrix, maximize=True)
    return [(i, j, float(matrix[i, j])) for i, j in zip(rows, columns) if matrix[i, j] > 0]


## CONTINGENCY TABLE
class Contingency():
    def __init__(self, with_true_negatives=True):
        self.tp = 0.0
        self.fp = 0.0
        self.fn = 0.0
        # true negatives are only defined for roles
        self.tn = 0.0 if with_true_negatives else None

    def add(self, other):
        self.tp += other.tp
        self.fp += other.fp
        self.fn += other.fn
        if self.tn is not None and other.tn is not None:
            self.tn += other.tn

    @property
    def precision(self):
        return self.tp / (self.tp + self.fp) if self.tp + self.fp else 0.0

    @property
    def recall(self):
        return self.tp / (self.tp + self.fn) if self.tp + self.fn else 0.0

    @property
    def f1(self):
        return 2 * self.precision * self.recall / (self.precision + self.recall) if self.precision + self.recall else 0.0

    def to_dict(self):
        return {"tp": round(self.tp, 3), "fp": round(self.fp, 3), "fn": round(self.fn, 3),
                "tn": None if self.tn is None else round(self.tn, 3),
                "precision": round(self.precision, 3), "recall": round(self.recall, 3), "f1": round(self.f1, 3)}


## EVENTS
def get_start_and_end(event):
    """The start and end of an event in minutes since midnight, from the first value of when and how_long."""
    when = get_role_values(event, "when")
    match = re.match(r"(\d{1,2}):(\d{2})", str(when[0])) if when else None
    if not match:
        return None
    start = int(match.group(1)) * 60 + int(match.group(2))
    how_long = get_role_values(event, "how_long")
    duration = how_long[0] if how_long and isinstance(how_long[0], (int, float)) else 0
    return start, start + duration

def get_parts_of_day(event):
    return [value for value in get_role_values(event, "when") if value in PART_OF_DAY_HOURS]

def in_part_of_day(event, time):
    """Whether the start of the time interval is in a part of the day in when of the event."""
    return any(PART_OF_DAY_HOURS[part][0] * 60 <= time[0] < PART_OF_DAY_HOURS[part][1] * 60
               for part in get_parts_of_day(event))

def get_time_similarity(gold_event, system_event):
    """The overlap of the two time intervals (intersection over union), or the closeness of the start times
    if that is higher: 1 for the same start time, 0 for an hour or more apart. If one of the events has no clock
    time, only a part of the day such as 'morning', it is PART_OF_DAY_SIMILARITY if the other event starts in that
    part of the day or has the same part, and 0 otherwise."""
    gold_time, system_time = get_start_and_end(gold_event), get_start_and_end(system_event)
    if not gold_time or not system_time:
        if gold_time:
            same_part = in_part_of_day(system_event, gold_time)
        elif system_time:
            same_part = in_part_of_day(gold_event, system_time)
        else:
            same_part = bool(set(get_parts_of_day(gold_event)) & set(get_parts_of_day(system_event)))
        return PART_OF_DAY_SIMILARITY if same_part else 0.0
    overlap = max(0, min(gold_time[1], system_time[1]) - max(gold_time[0], system_time[0]))
    union = max(gold_time[1], system_time[1]) - min(gold_time[0], system_time[0])
    closeness = max(0.0, 1 - abs(gold_time[0] - system_time[0]) / 60)
    return max(overlap / union if union else 0.0, closeness)

def get_event_similarity(gold_event, system_event, mode):
    """Half the time similarity, a quarter the event type and a quarter the event label.
    Time alone is not enough to align two events, the type or the label has to match as well. The description is
    not compared: it is a free sentence, not a label of the event."""
    match = MATCHES[mode]
    type_similarity = exact_match(gold_event.get("event_type", ""), system_event.get("event_type", ""))
    label_similarity = match(gold_event.get("event_label", ""), system_event.get("event_label", ""))
    return (0.5 * get_time_similarity(gold_event, system_event) + 0.25 * type_similarity
            + 0.25 * label_similarity)

def align_events(gold_events, system_events, mode, threshold=EVENT_THRESHOLD):
    """Aligns the events one-to-one with the highest total similarity. Returns (gold key, system key, similarity)."""
    gold_keys, system_keys = list(gold_events), list(system_events)
    pairs = assign(len(gold_keys), len(system_keys), lambda i, j: get_event_similarity(
        gold_events[gold_keys[i]], system_events[system_keys[j]], mode))
    return sorted([(gold_keys[i], system_keys[j], score) for i, j, score in pairs if score >= threshold],
                  key=lambda pair: int(pair[0].replace("event", "")))


## COREFERENCE
class Entities():
    def __init__(self, day):
        """The entities of the coreference chains of a day, with the entity of each mention in an event."""
        self.chains = {chain["entity_id"]: chain for chain in day.get("coreference_chains", [])}
        self.mention_entities = {}
        for entity_id, chain in self.chains.items():
            for mention in chain.get("mentions", []):
                # the role is the last part of the field, e.g. with_whom in photo.gold.with_whom
                role = mention["field"].split(".")[-1]
                self.mention_entities[(mention["event"], role, normalize(mention["mention"]))] = entity_id

    def get_entity(self, event_key, role, mention):
        return self.mention_entities.get((event_key, role, normalize(mention)))

    def get_labels(self, entity_id):
        chain = self.chains[entity_id]
        return [chain.get("name", "")] + [mention["mention"] for mention in chain.get("mentions", [])]

def align_entities(gold_entities, system_entities, mode):
    """Aligns the entities of the GOLD and collected chains on the best match of their names and mentions.
    Returns a dictionary from GOLD entity to collected entity."""
    match = MATCHES[mode]
    gold_ids, system_ids = list(gold_entities.chains), list(system_entities.chains)
    gold_labels = [set(gold_entities.get_labels(entity_id)) for entity_id in gold_ids]
    system_labels = [set(system_entities.get_labels(entity_id)) for entity_id in system_ids]
    pairs = assign(len(gold_ids), len(system_ids), lambda i, j: max(
        match(gold, system) for gold in gold_labels[i] for system in system_labels[j]))
    return {gold_ids[i]: system_ids[j] for i, j, score in pairs if score >= ENTITY_THRESHOLDS[mode]}


## EVALUATION
def get_nr_of_fillers(event, role):
    """Lists of values count each value, except where and when that describe a single place or time."""
    values = get_role_values(event, role)
    if role in SPECIFICITY_ROLES or role == "how_long":
        return 1 if values else 0
    return len(values)

def evaluate_role(gold_event, system_event, gold_key, system_key, role, mode, entities):
    """Returns the contingency tables of the role and of its fillers for two aligned events."""
    match = MATCHES[mode]
    gold_values, system_values = get_role_values(gold_event, role), get_role_values(system_event, role)
    role_table, filler_table = Contingency(), Contingency(with_true_negatives=False)
    if gold_values and system_values:
        role_table.tp += 1
    elif system_values:
        role_table.fp += 1
    elif gold_values:
        role_table.fn += 1
    else:
        role_table.tn += 1

    if not gold_values or not system_values:
        filler_table.fp += get_nr_of_fillers(system_event, role)
        filler_table.fn += get_nr_of_fillers(gold_event, role)
        return role_table, filler_table

    if role in SPECIFICITY_ROLES or role == "how_long":
        # a single value with a score between 0 and 1
        if role == "how_long":
            score = duration_match(gold_values[0], system_values[0], mode)
        else:
            score = specificity_match(gold_values, system_values, match)
        filler_table.tp += score
        filler_table.fp += 1 - score
        filler_table.fn += 1 - score
        return role_table, filler_table

    if role in COREFERENCE_ROLES:
        gold_entities, system_entities, entity_alignment = entities

        def score(i, j):
            gold_entity = gold_entities.get_entity(gold_key, role, gold_values[i])
            system_entity = system_entities.get_entity(system_key, role, system_values[j])
            if gold_entity and system_entity:
                return 1.0 if entity_alignment.get(gold_entity) == system_entity else 0.0
            return match(gold_values[i], system_values[j])
    else:
        def score(i, j):
            return match(gold_values[i], system_values[j])

    matched = sum(pair_score for _, _, pair_score in assign(len(gold_values), len(system_values), score))
    filler_table.tp += matched
    filler_table.fp += len(system_values) - matched
    filler_table.fn += len(gold_values) - matched
    return role_table, filler_table

## DESCRIBING THE MISMATCHES OF ALIGNED EVENTS
def format_minutes(minutes):
    return f"{minutes // 60:02d}:{minutes % 60:02d}"

def describe_time(event):
    time = get_start_and_end(event)
    if not time:
        return "no clock time" + (f" ({', '.join(get_role_values(event, 'when'))})" if get_role_values(event, "when") else "")
    duration = time[1] - time[0]
    return format_minutes(time[0]) + (f" for {duration} minutes" if duration else "")

def describe_event_similarity(gold_event, system_event, mode):
    """Explains the similarity of two aligned events from its parts: time, event type and event label."""
    time = get_time_similarity(gold_event, system_event)
    type_similarity = exact_match(gold_event.get("event_type", ""), system_event.get("event_type", ""))
    label = MATCHES[mode](gold_event.get("event_label", ""), system_event.get("event_label", ""))
    parts = [f"similarity = 0.5 * time {time:.2f} + 0.25 * type {type_similarity:.2f} + 0.25 * label {label:.2f}"]
    if time < 1:
        parts.append(f"time: {describe_time(system_event)} instead of {describe_time(gold_event)}")
    if type_similarity < 1:
        parts.append(f"type: '{system_event.get('event_type', '')}' instead of '{gold_event.get('event_type', '')}'")
    if label < 1:
        parts.append(f"label: '{system_event.get('event_label', '')}' instead of '{gold_event.get('event_label', '')}'")
    return parts

def describe_role_mismatch(gold_event, system_event, role, filler_table, mode):
    """Explains why the fillers of a role of two aligned events do not fully match, or None if they do."""
    if filler_table.fp < 1e-6 and filler_table.fn < 1e-6:
        return None
    gold_values, system_values = get_role_values(gold_event, role), get_role_values(system_event, role)
    if not gold_values:
        return f"{role}: {system_values} is not in the GOLD"
    if not system_values:
        return f"{role}: missing, GOLD {gold_values}"
    if role == "how_long":
        return f"{role} {filler_table.tp:.2f}: {system_values[0]} instead of {gold_values[0]} minutes"
    if role in SPECIFICITY_ROLES:
        # the GOLD value that gives the best score, weighted by its position in the GOLD list
        match = MATCHES[mode]
        n = len(gold_values)
        i, gold, system = max(((i, gold, system) for i, gold in enumerate(gold_values) for system in system_values),
                              key=lambda item: (n - item[0]) / n * match(item[1], item[2]))
        best = f"'{system}'" if normalize(system) == normalize(gold) else f"'{system}' with '{gold}'"
        return (f"{role} {filler_table.tp:.2f}: the best match is {best}, GOLD value {i + 1} of {n}, which scores "
                f"{n - i}/{n}, the most specific GOLD value is '{gold_values[0]}'")
    return (f"{role} {filler_table.tp:.2f} of {len(gold_values)} GOLD values matched: "
            f"collected {system_values}, GOLD {gold_values}")

## LIMITING THE GOLD EVENTS
# max_gold_events for as many GOLD events as the collected day has
AS_COLLECTED = "collected"

def get_nr_of_gold_events(gold_day, system_day, max_gold_events=None):
    """The number of GOLD events to evaluate: all with None, the number of collected events with "collected",
    otherwise max_gold_events, but never more than the GOLD day has."""
    nr_of_gold_events = len(get_events(gold_day))
    if max_gold_events is None:
        return nr_of_gold_events
    if max_gold_events == AS_COLLECTED:
        max_gold_events = len(get_events(system_day))
    return min(int(max_gold_events), nr_of_gold_events)

def limit_gold_events(gold_day, system_day, max_gold_events=None):
    """A copy of the GOLD day with only its first events (see get_nr_of_gold_events), e.g. to evaluate a conversation
    that stopped early only against the part of the day it got to. The coreference chains only keep the mentions in
    these events."""
    if max_gold_events is None:
        return gold_day
    keys = list(get_events(gold_day))[:get_nr_of_gold_events(gold_day, system_day, max_gold_events)]
    day = {key: value for key, value in gold_day.items() if not key.startswith("event") or key in keys}
    chains = []
    for chain in gold_day.get("coreference_chains", []):
        mentions = [mention for mention in chain.get("mentions", []) if mention.get("event") in keys]
        if mentions:
            chains.append({**chain, "mentions": mentions})
    if "coreference_chains" in gold_day:
        day["coreference_chains"] = chains
    return day

def evaluate_day(gold_day, system_day, mode, event_threshold=EVENT_THRESHOLD, max_gold_events=None):
    """Evaluates a collected day against a GOLD day in the given mode (exact or jaccard). With max_gold_events, only
    the first GOLD events are evaluated, see limit_gold_events."""
    gold_day = limit_gold_events(gold_day, system_day, max_gold_events)
    gold_events, system_events = get_events(gold_day), get_events(system_day)
    alignment = align_events(gold_events, system_events, mode, event_threshold)
    gold_entities, system_entities = Entities(gold_day), Entities(system_day)
    entities = (gold_entities, system_entities, align_entities(gold_entities, system_entities, mode))

    events = Contingency(with_true_negatives=False)
    roles = {role: Contingency() for role in ROLES}
    fillers = {role: Contingency(with_true_negatives=False) for role in ROLES}
    # for each aligned pair, a comment that explains the similarity and the roles that do not fully match
    comments = {}
    for gold_key, system_key, _ in alignment:
        events.tp += 1
        gold_event, system_event = gold_events[gold_key], system_events[system_key]
        comment = describe_event_similarity(gold_event, system_event, mode)
        for role in ROLES:
            role_table, filler_table = evaluate_role(gold_event, system_event,
                                                     gold_key, system_key, role, mode, entities)
            roles[role].add(role_table)
            fillers[role].add(filler_table)
            mismatch = describe_role_mismatch(gold_event, system_event, role, filler_table, mode)
            if mismatch:
                comment.append(mismatch)
        comments[(gold_key, system_key)] = "; ".join(comment)

    # events that are not aligned: their roles and fillers are missed or wrong
    aligned_gold = {gold_key for gold_key, _, _ in alignment}
    aligned_system = {system_key for _, system_key, _ in alignment}
    for key, event in gold_events.items():
        if key not in aligned_gold:
            events.fn += 1
            for role in ROLES:
                roles[role].fn += 1 if get_role_values(event, role) else 0
                fillers[role].fn += get_nr_of_fillers(event, role)
    for key, event in system_events.items():
        if key not in aligned_system:
            events.fp += 1
            for role in ROLES:
                roles[role].fp += 1 if get_role_values(event, role) else 0
                fillers[role].fp += get_nr_of_fillers(event, role)

    return {"events": events, "roles": with_total(roles), "role_fillers": with_total(fillers),
            "event_alignment": [{"gold": gold_key, "system": system_key, "similarity": round(similarity, 3),
                                 "gold_label": gold_events[gold_key].get("event_label", ""),
                                 "system_label": system_events[system_key].get("event_label", ""),
                                 "comment": comments[(gold_key, system_key)]}
                                for gold_key, system_key, similarity in alignment],
            "entity_alignment": entities[2]}

def with_total(tables):
    total = Contingency(with_true_negatives=all(table.tn is not None for table in tables.values()))
    for table in tables.values():
        total.add(table)
    return {"total": total, **tables}


## TURN EVALUATION
# Columns of the turn evaluation, in the format of the evaluation CSV files of the EMISSOR scenarios
TURN_COLUMNS = ["Turn", "Turn nr.", "Speaker", "Response", "Event", "nr_of_events", "nr_of_roles"]
# The speaker of the questions of the agent in the turn evaluation
AGENT_SPEAKER = "AGENT"

def get_human_turns(event):
    """The utterances of the user about an event, see get_utterances. Skipped questions have an empty utterance,
    which is kept so that human_turn[i] stays the answer to agent_turn[i]."""
    return get_utterances(event, "human_turn")

def get_mention_score(value, turn):
    """The part of the words of a value that occur in a turn, e.g. 1.0 if the turn mentions all words."""
    words = get_words(value)
    return len(words & get_words(turn)) / len(words) if words else 0.0

def get_role_turns(event, turns):
    """Attributes each filled role of an event to the turn of the user that mentions its values best.
    The roles are filled by the LLM from all the turns about the event at once, so this is an estimate.
    If several turns mention a role equally well, the latest turn is taken: the agent only asks a follow-up question
    for a role it could not get from the earlier turns. Roles that are not mentioned in any turn, e.g. inferred by
    the LLM, are attributed to the first turn."""
    role_turns = {}
    for role in ROLES:
        values = get_role_values(event, role)
        if not values or not turns:
            continue
        scores = [max(get_mention_score(value, turn) for value in values) for turn in turns]
        best_turn = max(range(len(turns)), key=lambda i: (scores[i], i))
        role_turns[role] = best_turn if scores[best_turn] > 0 else 0
    return role_turns

def get_correct_roles(gold_day, system_day, mode, event_threshold=EVENT_THRESHOLD):
    """For each aligned collected event, the correctness of each filled role: the part of its values that match
    the GOLD event (the precision of the role-fillers), e.g. 0.5 if one of two values is correct."""
    gold_events, system_events = get_events(gold_day), get_events(system_day)
    gold_entities, system_entities = Entities(gold_day), Entities(system_day)
    entities = (gold_entities, system_entities, align_entities(gold_entities, system_entities, mode))
    correct_roles = {}
    for gold_key, system_key, _ in align_events(gold_events, system_events, mode, event_threshold):
        correct_roles[system_key] = {}
        for role in ROLES:
            if get_role_values(system_events[system_key], role):
                _, filler_table = evaluate_role(gold_events[gold_key], system_events[system_key],
                                                gold_key, system_key, role, mode, entities)
                correct_roles[system_key][role] = filler_table.precision
    return correct_roles

def get_turn_rows(gold_day, system_day, event_threshold=EVENT_THRESHOLD, max_gold_events=None):
    """A row for each turn in the collected day: the questions of the agent (agent_turn) and the answers of the user
    (human_turn), in the order of the conversation. The Turn of a row is turn<turn_id>, with the turn_id of the turn
    in the conversation, as in the conversation files of the simulated user. The rows of the user have the number of
    events and roles extracted from the turn and the number of correct events and roles in both modes. An event is
    counted at its first turn, a role at the turn that mentions it (see get_role_turns). The rows of the agent have
    no numbers, since the agent does not extract anything itself. Skipped questions have no row for the answer.
    A turn from which several events were extracted, e.g. an answer about the whole morning, has one row with the
    numbers of all these events. With max_gold_events, only the first GOLD events are evaluated (see
    limit_gold_events)."""
    gold_day = limit_gold_events(gold_day, system_day, max_gold_events)
    correct_roles = {mode: get_correct_roles(gold_day, system_day, mode, event_threshold) for mode in MODES}
    rows = []
    rows_by_turn = {}

    def add_row(row):
        """Adds the row, or adds its numbers to the row of the same turn of an earlier event."""
        if row["Turn"] not in rows_by_turn:
            row["Turn nr."] = len(rows)
            rows_by_turn[row["Turn"]] = row
            rows.append(row)
            return
        earlier = rows_by_turn[row["Turn"]]
        earlier["Event"] += "," + row["Event"]
        for key, value in row.items():
            if key.startswith("nr_of_"):
                earlier[key] = round(earlier[key] + value, 3)

    for event_key, event in get_events(system_day).items():
        # human_turn[i] is the answer to agent_turn[i], older files have no agent_turn
        agent_turns = get_turns(event, "agent_turn")
        human_turns = get_turns(event, "human_turn")
        turns = [turn["utterance"] for turn in human_turns]
        role_turns = get_role_turns(event, turns)
        speaker = (get_role_values(event, "who") or ["SPEAKER"])[0]
        for i in range(max(len(agent_turns), len(turns))):
            if i < len(agent_turns):
                add_row({"Turn": f"turn{agent_turns[i]['turn_id']}", "Speaker": AGENT_SPEAKER,
                         "Response": agent_turns[i]["utterance"], "Event": event_key})
            if i >= len(turns) or not turns[i]:
                continue
            roles = [role for role, role_turn in role_turns.items() if role_turn == i]
            row = {"Turn": f"turn{human_turns[i]['turn_id']}", "Speaker": speaker,
                   "Response": turns[i], "Event": event_key, "nr_of_events": 1 if i == 0 else 0, "nr_of_roles": len(roles)}
            for mode in MODES:
                aligned = event_key in correct_roles[mode]
                row[f"nr_of_correct_events_{mode}"] = 1 if i == 0 and aligned else 0
                row[f"nr_of_correct_roles_{mode}"] = round(sum(correct_roles[mode][event_key].get(role, 0.0)
                                                               for role in roles), 3) if aligned else 0
            add_row(row)
    return rows

def get_turn_output_path(gold_file, system_file):
    gold_name = os.path.splitext(os.path.basename(gold_file))[0]
    system_name, _ = os.path.splitext(system_file)
    return f"{system_name}_vs_{gold_name}_turn_evaluation.csv"

# The numbers of the turn evaluation for which the effectiveness of the communication is reported
EFFECTIVENESS_COUNTS = (["nr_of_events", "nr_of_roles"]
                        + [f"nr_of_correct_{level}_{mode}" for level in ["events", "roles"] for mode in MODES])

def get_turn_effectiveness(rows):
    """The effectiveness of the communication: how much the agent gets out of the turns of the conversation.
    For each number of the turn evaluation (events, roles, correct events and correct roles), it gives:
    - total: the total over all turns
    - average_per_user_turn: the average per answer of the user, i.e. the total divided by the number of user turns
    - ratio_per_turn: the total divided by the number of all turns, the questions of the agent included, i.e. what
      each turn of the conversation yields
    The rows can be the rows of get_turn_rows or the rows of a saved turn evaluation CSV file."""
    user_rows = [row for row in rows if row["Speaker"] != AGENT_SPEAKER]
    effectiveness = {"nr_of_turns": len(rows), "nr_of_agent_turns": len(rows) - len(user_rows),
                     "nr_of_user_turns": len(user_rows), "counts": {}}
    for count in EFFECTIVENESS_COUNTS:
        # the numbers in a CSV file are strings, the agent rows have empty numbers
        total = sum(float(row.get(count) or 0) for row in user_rows)
        effectiveness["counts"][count] = {
            "total": round(total, 3),
            "average_per_user_turn": round(total / len(user_rows), 3) if user_rows else 0.0,
            "ratio_per_turn": round(total / len(rows), 3) if rows else 0.0}
    return effectiveness

def read_turn_effectiveness(turn_csv):
    """The effectiveness of the communication from a saved turn evaluation CSV file, see get_turn_effectiveness."""
    with open(turn_csv, newline="") as csv_file:
        return get_turn_effectiveness(list(csv.DictReader(csv_file, delimiter=";")))

def print_turn_effectiveness(effectiveness):
    print(f"\nEffectiveness of the communication: {effectiveness['nr_of_turns']} turns "
          f"({effectiveness['nr_of_agent_turns']} agent, {effectiveness['nr_of_user_turns']} user)")
    print(f"{'':<30}{'total':>8}{'per user turn':>15}{'per turn':>10}")
    for count, values in effectiveness["counts"].items():
        print(f"{count:<30}{values['total']:>8g}{values['average_per_user_turn']:>15.3f}"
              f"{values['ratio_per_turn']:>10.3f}")

def get_effectiveness_path(turn_csv):
    return os.path.splitext(turn_csv)[0].replace("_turn_evaluation", "") + "_turn_effectiveness.json"

def save_turn_evaluation(gold_file, system_file, output_file=None, event_threshold=EVENT_THRESHOLD, verbose=True,
                         max_gold_events=None):
    """Saves the evaluation per turn of the user as a CSV file with ';' as separator, in the same format as the
    evaluation files of the EMISSOR scenarios, so that it can be plotted with the plots module, e.g.:

        plot_interaction.create_timeline_image_from_csv(csv_file, "nr_of_correct_roles_jaccard", settings)

    The file is saved next to the collected day as <collected>_vs_<key>_turn_evaluation.csv by default.
    The effectiveness of the communication (see get_turn_effectiveness) is saved next to it as
    <collected>_vs_<key>_turn_effectiveness.json and printed unless verbose=False. With max_gold_events, only the
    first GOLD events are evaluated (see limit_gold_events). Returns the path of the CSV file."""
    with open(gold_file) as json_file:
        gold_day = json.load(json_file)
    with open(system_file) as json_file:
        system_day = json.load(json_file)
    rows = get_turn_rows(gold_day, system_day, event_threshold, max_gold_events)
    columns = TURN_COLUMNS + [f"nr_of_correct_{level}_{mode}" for level in ["events", "roles"] for mode in MODES]
    output_file = output_file or get_turn_output_path(gold_file, system_file)
    with open(output_file, "w", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=columns, delimiter=";")
        writer.writeheader()
        writer.writerows(rows)

    effectiveness = get_turn_effectiveness(rows)
    with open(get_effectiveness_path(output_file), "w") as json_file:
        json.dump({"gold": gold_file, "system": system_file, "max_gold_events": max_gold_events,
                   "nr_of_gold_events": get_nr_of_gold_events(gold_day, system_day, max_gold_events),
                   **effectiveness}, json_file, indent=2)
    if verbose:
        print_turn_effectiveness(effectiveness)
        print("Saved the effectiveness to", get_effectiveness_path(output_file))
    return output_file


## OUTPUT
def results_to_dict(results):
    return {"events": results["events"].to_dict(),
            "roles": {role: table.to_dict() for role, table in results["roles"].items()},
            "role_fillers": {role: table.to_dict() for role, table in results["role_fillers"].items()},
            "event_alignment": results["event_alignment"],
            "entity_alignment": results["entity_alignment"]}

def format_row(name, table):
    tn = "n/a" if table.tn is None else f"{table.tn:g}"
    return (f"{name:<22}{table.tp:>8.2f}{table.fp:>8.2f}{table.fn:>8.2f}{tn:>8}"
            f"{table.precision:>11.3f}{table.recall:>8.3f}{table.f1:>8.3f}")

def print_results(mode, results):
    print(f"\nMode: {mode}, {len(results['event_alignment'])} aligned events")
    print(f"{'':<22}{'TP':>8}{'FP':>8}{'FN':>8}{'TN':>8}{'precision':>11}{'recall':>8}{'f1':>8}")
    print(format_row("events", results["events"]))
    for level in ["roles", "role_fillers"]:
        for role, table in results[level].items():
            print(format_row(f"{level.replace('_', '-')} {role}" if role != "total" else level.replace("_", "-"), table))

def get_output_path(gold_file, system_file):
    gold_name = os.path.splitext(os.path.basename(gold_file))[0]
    system_name, _ = os.path.splitext(system_file)
    return f"{system_name}_vs_{gold_name}_evaluation.json"

def evaluate_files(gold_file, system_file, output_file=None, event_threshold=EVENT_THRESHOLD, verbose=True,
                   max_gold_events=None):
    """Evaluates a collected day file against a GOLD day file in both modes, prints and saves the results.
    With verbose=False nothing is printed, e.g. when the results are shown as tables in a notebook.
    With max_gold_events, only the first GOLD events are evaluated: a number, or "collected" for as many GOLD events
    as the collected day has (see limit_gold_events)."""
    with open(gold_file) as json_file:
        gold_day = json.load(json_file)
    with open(system_file) as json_file:
        system_day = json.load(json_file)
    nr_of_gold_events = get_nr_of_gold_events(gold_day, system_day, max_gold_events)
    evaluation = {"gold": gold_file, "system": system_file, "event_threshold": event_threshold,
                  "max_gold_events": max_gold_events, "nr_of_gold_events": nr_of_gold_events, "modes": {}}
    if verbose and nr_of_gold_events < len(get_events(gold_day)):
        print(f"Evaluating the first {nr_of_gold_events} of the {len(get_events(gold_day))} GOLD events")
    for mode in MODES:
        results = evaluate_day(gold_day, system_day, mode, event_threshold, max_gold_events)
        if verbose:
            print_results(mode, results)
        evaluation["modes"][mode] = results_to_dict(results)

    output_file = output_file or get_output_path(gold_file, system_file)
    with open(output_file, "w") as json_file:
        json.dump(evaluation, json_file, indent=2, ensure_ascii=False)
    evaluation["output"] = output_file
    if verbose:
        print("\nSaved the evaluation to", output_file)
    return evaluation


def main():
    parser = argparse.ArgumentParser(description="Evaluate a collected day description against a GOLD day description")
    parser.add_argument("--key", required=True, help="JSON file with the GOLD day")
    parser.add_argument("--collected", required=True, help="JSON file with the collected day")
    parser.add_argument("--output", help="JSON file for the results, by default <collected>_vs_<key>_evaluation.json")
    parser.add_argument("--csv", help="CSV file for the evaluation per turn, "
                                      "by default <collected>_vs_<key>_turn_evaluation.csv")
    parser.add_argument("--event-threshold", type=float, default=EVENT_THRESHOLD,
                        help="Minimal similarity to align a collected event with a GOLD event")
    parser.add_argument("--max-gold-events",
                        help="Only evaluate the first GOLD events: a number, or 'collected' for as many as the "
                             "collected day has. By default all GOLD events are evaluated")
    args = parser.parse_args()
    max_gold_events = args.max_gold_events
    if max_gold_events and max_gold_events != AS_COLLECTED:
        max_gold_events = int(max_gold_events)
    evaluate_files(args.key, args.collected, args.output, args.event_threshold, max_gold_events=max_gold_events)
    print("Saved the evaluation per turn to", save_turn_evaluation(args.key, args.collected, args.csv,
                                                                    args.event_threshold,
                                                                    max_gold_events=max_gold_events))


if __name__ == "__main__":
    main()
