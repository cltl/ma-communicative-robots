"""A scripted conversational agent that asks a user about their day, hour by hour.

For each hour, the agent asks what the user did and then asks follow-up questions for the slots that are still
unknown: with whom, what, with what, where, when and for how long. An LLM served by a llama.cpp server fills the slots
of the event from the answers of the user. The day is saved as a JSON file with the same structure as the examples
in data/example_days: an object with event1, event2, ... and the coreference_chains of the people in the events.

Start the llama.cpp server before running the agent, e.g.:

    llama-server -hf Qwen/Qwen2.5-7B-Instruct-GGUF:Q4_K_M --port 8080 -c 4096

and run the agent from the root of the project:

    python -m src.cltl.demo_chatbot.day_interviewer

Type 'stop' at any moment to end the conversation and save the day.
"""
import argparse
import glob
import json
import os
import re
from datetime import datetime

from openai import OpenAI

from src.cltl.demo_chatbot.day_statistics import make_turn, get_utterances

LLAMA_CPP_URL = "http://localhost:8080/v1"
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
EXAMPLE_DAYS = os.path.join(PROJECT_ROOT, "data", "example_days")
OUTPUT_FOLDER = os.path.join(PROJECT_ROOT, "data", "collected_days")

STOP_WORDS = {"stop", "quit", "exit", "bye", "goodbye", "done", "end", "finish", "finished", "the end",
              "that's all", "that is all", "enough", "stop please", "please stop", "i want to stop"}

# The slots the agent asks for when the user did not mention them, in the order of asking
SLOT_ORDER = ["with_whom", "what", "with_what", "where", "start_time", "how_long"]
LIST_SLOTS = ["what", "with_what", "with_whom", "where"]
NOT_OTHERS = {"alone", "nobody", "no one", "none", "myself", "herself", "himself", "themselves", "themself", "self"}
QUESTIONS = {
    "with_whom": "Who were you with?",
    "what": "What did it involve? For example, what did you eat, make, read or talk about?",
    "with_what": "What did you use for it, such as tools, devices or a vehicle?",
    "where": "Where were you?",
    "start_time": "At what time exactly did you start?",
    "how_long": "How long did it take?",
}

NUMBER_WORDS = ["twelve", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "eleven"]
MINUTE_WORDS = {5: "five", 10: "ten", 15: "quarter", 20: "twenty", 25: "twenty-five", 30: "half"}
# (hour before which the part applies, phrase, part of the day), as used in the example days
PARTS_OF_DAY = [(5, "in the middle of the night", "night"),
                (9, "early in the morning", "morning"),
                (11, "in the morning", "morning"),
                (12, "late in the morning", "morning"),
                (13, "around noon", "midday"),
                (15, "early in the afternoon", "afternoon"),
                (17, "late in the afternoon", "afternoon"),
                (19, "early in the evening", "evening"),
                (21, "in the evening", "evening"),
                (24, "late in the evening", "evening")]


## TIME
def spoken_time(hour, minute):
    """The time as it is spoken, e.g. 'quarter to six', or None on the hour."""
    if minute == 0:
        return None
    if minute <= 30:
        words = MINUTE_WORDS.get(minute, f"{minute} minute{'s' if minute > 1 else ''}")
        return f"{words} past {NUMBER_WORDS[hour % 12]}"
    words = MINUTE_WORDS.get(60 - minute, f"{60 - minute} minute{'s' if 60 - minute > 1 else ''}")
    return f"{words} to {NUMBER_WORDS[(hour + 1) % 12]}"

def nearest_hour(hour, minute):
    """The nearest hour on a 12 hour clock, half past rounds down as in the example days."""
    return (hour + (1 if minute > 30 else 0)) % 12 or 12

def make_when(start_time):
    """The 'when' slot: e.g. ['05:45', 'quarter to six', "6 o'clock", 'early in the morning', 'morning']."""
    hour, minute = [int(part) for part in start_time.split(":")]
    when = [start_time]
    if spoken_time(hour, minute):
        when.append(spoken_time(hour, minute))
    when.append(f"{nearest_hour(hour, minute)} o'clock")
    for before, phrase, part in PARTS_OF_DAY:
        if hour < before:
            when.extend([phrase, part])
            break
    return when

def parse_hour(text):
    """The hour in a text such as '7', '7:30', '7 am' or '9pm', or None."""
    match = re.search(r"\b(\d{1,2})(?:[:.](\d{2}))?\s*(am|pm|a\.m\.|p\.m\.)?", text.lower())
    if not match:
        return None
    hour = int(match.group(1))
    if match.group(3) and match.group(3).startswith("p") and hour < 12:
        hour += 12
    return hour if hour < 24 else None

# A name after e.g. 'my name is', anywhere in the answer: the phrase is matched in any case, the name has capitals
NAME_PATTERN = re.compile(r"\b(?i:my name is|i am|i'm|this is|call me|it's|it is)\s+([A-Z][\w'-]*(?:\s+[A-Z][\w'-]*)?)")

def parse_name(text):
    """The name in an answer such as 'Henk', 'My name is Henk' or 'Hi! I'm Henk, nice to meet you.'. Without such a
    phrase, the first words of the answer are taken."""
    match = NAME_PATTERN.search(text)
    if match:
        return match.group(1)
    return " ".join(re.findall(r"[\w'-]+", text)[:3]) or "the user"

def say_hour(hour):
    return f"{hour % 12 or 12} o'clock" + (" in the afternoon" if 12 < hour < 18 else " in the evening" if hour >= 18 else "")


## EXAMPLES
def load_example_days(folder):
    days = []
    for file in sorted(glob.glob(os.path.join(folder, "*.json"))):
        with open(file) as json_file:
            days.append(json.load(json_file))
    return days

def get_events(day):
    return [event for key, event in day.items() if key.startswith("event")]

def get_human_turns(event):
    """The utterances of the user about an event, without the empty answers to skipped questions."""
    return [utterance for utterance in get_utterances(event, "human_turn") if utterance]

def get_event_types(days):
    return sorted({event["event_type"] for day in days for event in get_events(day)})

def get_example_prompts(days, nr_of_examples=3):
    """Events from the example days as examples of the slots the LLM should fill: the human turn and the slots.
    Events with a person, an object and a tool are taken from different days, events with a photo are skipped."""
    examples = []
    for day in days:
        for event in get_events(day):
            if "photo" not in event and event["what"] and event["with_what"] and event["with_whom"]:
                slots = {"event_type": event["event_type"], "event_label": event["event_label"],
                         "description": event["description"], "what": event["what"],
                         "with_what": event["with_what"], "with_whom": event["with_whom"], "where": event["where"],
                         "start_time": event["when"][0], "how_long": event["how_long"]}
                turns = "\n".join(f"User: {turn}" for turn in get_human_turns(event))
                examples.append(f"{turns}\nJSON: {json.dumps(slots)}")
                break
        if len(examples) == nr_of_examples:
            break
    return examples


## LLM
def get_slot_schema(event_types):
    """JSON schema for the answer of the LLM, null means that the user did not say anything about the slot."""
    string_list = {"anyOf": [{"type": "array", "items": {"type": "string"}}, {"type": "null"}]}
    properties = {"event_type": {"type": "string", "enum": event_types},
                  "event_label": {"type": "string"},
                  "description": {"type": "string"},
                  "what": string_list, "with_what": string_list, "with_whom": string_list, "where": string_list,
                  "start_time": {"anyOf": [{"type": "string", "pattern": "^[0-2][0-9]:[0-5][0-9]$"}, {"type": "null"}]},
                  "how_long": {"anyOf": [{"type": "integer"}, {"type": "null"}]}}
    return {"type": "object", "properties": properties, "required": list(properties)}

def parse_json(text):
    """Parses the JSON in the answer of the LLM, also when there is text around it."""
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        return json.loads(match.group(0)) if match else {}

def slug(text):
    return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_") or "entity"


class DayInterviewer:
    def __init__(self, client: OpenAI, model, examples_folder=EXAMPLE_DAYS, output_folder=OUTPUT_FOLDER,
                 ask_all=False):
        """Creates the agent.
        params
        client: OpenAI client for the llama.cpp server
        model: the model served by llama.cpp
        examples_folder: folder with the example days, used for the event types and as examples for the LLM
        output_folder: folder in which the day is saved
        ask_all: ask every slot, also when the user already mentioned it
        """
        self.client = client
        self.model = model
        self.output_folder = output_folder
        self.ask_all = ask_all
        days = load_example_days(examples_folder)
        if not days:
            raise ValueError(f"No example days found in {examples_folder}")
        self.event_types = get_event_types(days)
        self.examples = get_example_prompts(days)
        self.schema = get_slot_schema(self.event_types)

        self.state = "name"
        self.name = ""
        self.pronoun = "their"
        self.home = ""
        self.hour = 7
        self.question = ""
        # the number of the last turn in the conversation, of the agent or the user, and of the current question
        self.turn_id = 0
        self.question_id = 0
        # the turns about the current event as (speaker, turn_id, utterance)
        self.turns = []
        self.pending_slots = []
        self.day = {}
        self.path = None

    @property
    def done(self):
        return self.state == "done"

    def start(self):
        self.turn_id = 1
        return "Hi! I would like to hear about your day, hour by hour. You can type 'stop' at any time. What is your name?"

    def respond(self, utterance):
        """Takes the answer of the user and returns the next question or the closing of the conversation."""
        utterance = utterance.strip()
        # the answer of the user is the next turn, the reply of the agent the turn after it
        self.turn_id += 1
        if utterance.lower().strip(".! ") in STOP_WORDS:
            reply = self.finish()
        else:
            reply = getattr(self, f"_on_{self.state}")(utterance)
        self.turn_id += 1
        return reply

    ## Getting to know the user
    def _on_name(self, utterance):
        self.name = parse_name(utterance)
        self.state = "pronoun"
        return f"Nice to meet you, {self.name}. Should I refer to you as he, she or they?"

    def _on_pronoun(self, utterance):
        words = set(re.findall(r"[a-z]+", utterance.lower()))
        self.pronoun = "her" if words & {"she", "her"} else "his" if words & {"he", "him", "his"} else "their"
        self.state = "home"
        return "Where do you live? Please give the town and the country."

    def _on_home(self, utterance):
        self.home = utterance.strip(" .") or "unknown"
        self.state = "start"
        return "At what hour did your day start? For example 7."

    def _on_start(self, utterance):
        hour = parse_hour(utterance)
        if hour is None:
            return "Sorry, could you give the hour as a number, for example 7?"
        self.hour = hour
        return self.ask_hour()

    ## Asking for the events
    def ask_hour(self):
        self.state = "event"
        self.turns = []
        self.question = f"What did you do at {say_hour(self.hour)}?"
        self.question_id = self.turn_id + 1
        return self.question

    def _on_event(self, utterance):
        if not utterance:
            # nothing to tell for this hour, move on to the next one
            return self.next_hour(self.hour + 1)
        self.turns = [("Agent", self.question_id, self.question), ("User", self.turn_id, utterance)]
        mentioned = {} if self.ask_all else self.get_mentioned_slots()
        self.pending_slots = [slot for slot in SLOT_ORDER if not mentioned.get(slot)]
        return self.ask_slot()

    def ask_slot(self):
        if not self.pending_slots:
            return self.save_event()
        self.state = "slot"
        self.question = QUESTIONS[self.pending_slots.pop(0)]
        self.question_id = self.turn_id + 1
        return self.question

    def _on_slot(self, utterance):
        self.turns.append(("Agent", self.question_id, self.question))
        self.turns.append(("User", self.turn_id, utterance))
        return self.ask_slot()

    def save_event(self):
        event = self.add_event()
        hour, minute = [int(part) for part in event["when"][0].split(":")]
        end = hour * 60 + minute + event["how_long"]
        noted = f"I noted: {event['event_label']} at {event['when'][0]} for {event['how_long']} minutes. "
        # continue with the hour closest to the end of the event, at least one hour later
        return noted + self.next_hour(max(self.hour + 1, round(end / 60)))

    def add_event(self):
        """Fills the slots of the event from the answers so far, adds it to the day and saves the day."""
        event = self.make_event(self.fill_slots())
        self.day[f"event{len(self.day) + 1}"] = event
        self.turns = []
        self.save()
        return event

    def next_hour(self, hour):
        if hour >= 24:
            return self.finish()
        self.hour = hour
        return self.ask_hour()

    ## Filling the slots with the LLM
    def get_conversation(self):
        return "\n".join(f"{speaker}: {text}" for speaker, _, text in self.turns)

    def get_mentioned_slots(self):
        """Asks the LLM which slots the user already answered, so that the agent only asks for the others.
        A yes/no question per slot is more reliable than checking which slots the LLM leaves empty,
        since the LLM tends to guess the slots that were not mentioned."""
        instruction = """
            Read what the user said about an activity and tell for each question whether the user already answered it.
            - with_whom: who took part in the activity, or that the user was alone
            - what: what the activity was about, e.g. the food, objects or topics
            - with_what: the tools, devices or vehicles that were used
            - where: the place where it happened
            - start_time: the clock time at which it started
            - how_long: how long it took
            Answer true only if the user said it, also when the answer is nobody or nothing.
            Answer false if you would have to guess.
            """
        schema = {"type": "object", "required": SLOT_ORDER,
                  "properties": {slot: {"type": "boolean"} for slot in SLOT_ORDER}}
        response = self.client.chat.completions.create(
            model=self.model, temperature=0,
            messages=[{"role": "system", "content": instruction},
                      {"role": "user", "content": self.get_conversation() + "\n\nJSON:"}],
            response_format={"type": "json_schema", "json_schema": {"name": "mentioned", "schema": schema}})
        return parse_json(response.choices[0].message.content)

    def get_slot_prompt(self):
        # the home of the user as the end of the example for where, e.g. ["Leiden", "the Netherlands", "Europe"]
        home = [part.strip() for part in self.home.split(",") if part.strip()] + ["Europe"]
        example_where = json.dumps([f"kitchen of {self.pronoun} house", "kitchen", f"{self.pronoun} house"] + home)
        instruction = f"""
            You fill the slots of an event in the day of {self.name} from an interview with {self.name}.
            {self.name} lives in {self.home}. Write about {self.name} in the third person, using "{self.pronoun}"
            as possessive pronoun, e.g. "bedroom of {self.pronoun} house".

            Return a JSON object with the slots:
            - event_type: one of {", ".join(self.event_types)}
            - event_label: a short label for the activity, e.g. "breakfast" or "cycling to work"
            - description: one short sentence about the activity without the subject, e.g. "made coffee and read the news"
            - what: the things the activity was about: food, objects, topics, e.g. ["coffee", "newspaper"]
            - with_what: the tools, devices or vehicles that were used, e.g. ["coffee machine", "bicycle"]
            - with_whom: the people or animals that took part, with their relation if known, e.g. ["his colleague Tom"]
            - where: the place from the most specific to the most general, ending with the town, country and continent,
              e.g. {example_where}
            - start_time: the time at which the activity started as "HH:MM" in 24 hours
            - how_long: the duration in minutes

            Only use what the user said: use an empty list if the user did not mention anything for a list,
            or said there was nothing or nobody, e.g. ["alone"] or ["herself"] is wrong, [] is right.
            Also use an empty list if the user does not remember or does not know, do not make things up.
            Give your best estimate for start_time and how_long if the user did not say them.
            """
        instruction += "\nExamples of events from other people:\n\n" + "\n\n".join(self.examples)
        return [{"role": "system", "content": instruction},
                {"role": "user", "content": f"The agent asked about {self.hour:02d}:00.\n\n{self.get_conversation()}\n\nJSON:"}]

    def fill_slots(self):
        response = self.client.chat.completions.create(
            model=self.model, messages=self.get_slot_prompt(), temperature=0,
            response_format={"type": "json_schema", "json_schema": {"name": "event", "schema": self.schema}})
        return parse_json(response.choices[0].message.content)

    def make_event(self, slots):
        """An event with the slots in the order of the example days."""
        start_time = slots.get("start_time")
        if not start_time or not re.fullmatch(r"([01][0-9]|2[0-3]):[0-5][0-9]", start_time):
            start_time = f"{self.hour:02d}:00"
        how_long = slots.get("how_long")
        if not isinstance(how_long, int) or how_long <= 0:
            how_long = 60
        lists = {slot: [str(value) for value in (slots.get(slot) or [])] for slot in LIST_SLOTS}
        # the LLM sometimes puts the narrator in with_whom when the user was alone
        not_others = NOT_OTHERS | {self.name.lower()}
        lists["with_whom"] = [person for person in lists["with_whom"] if person.lower() not in not_others]
        event_type = slots.get("event_type")
        return {"event_type": event_type if event_type in self.event_types else "special",
                "event_label": slots.get("event_label") or "",
                "who": [self.name],
                "what": lists["what"],
                "description": slots.get("description") or "",
                # the questions of the agent about this event and the answers of the user with the number of the
                # turn in the conversation: human_turn[i] is the answer to agent_turn[i], with the next turn_id,
                # and has an empty utterance if the question was skipped
                "agent_turn": [make_turn(turn_id, text) for speaker, turn_id, text in self.turns if speaker == "Agent"],
                "human_turn": [make_turn(turn_id, text) for speaker, turn_id, text in self.turns if speaker == "User"],
                "where": lists["where"],
                "when": make_when(start_time),
                "how_long": how_long,
                "with_what": lists["with_what"],
                "with_whom": lists["with_whom"]}

    ## Coreference chains
    def get_coreference_chains(self):
        """The narrator and the people in with_whom as entities with their mentions in the events.
        The LLM groups the mentions that refer to the same entity, e.g. 'his wife Gerda' and 'Gerda'."""
        narrator_id = slug(self.name)
        chains = [{"entity_id": narrator_id, "name": self.name, "type": "person", "description": "the narrator",
                   "mentions": [{"event": key, "field": "who", "mention": self.name} for key in self.day]}]
        mentions = list(dict.fromkeys(mention for event in self.day.values() for mention in event["with_whom"]))
        if not mentions:
            return chains

        entities = self.group_mentions(mentions)
        # mentions the LLM did not assign get an entity of their own
        assigned = {mention for entity in entities for mention in entity["mentions"]}
        entities += [{"name": mention, "type": "person", "description": "", "mentions": [mention]}
                     for mention in mentions if mention not in assigned]
        entity_ids = {narrator_id}
        for entity in entities:
            entity_id = slug(entity["name"])
            while entity_id in entity_ids:
                entity_id += "_2"
            entity_ids.add(entity_id)
            chains.append({"entity_id": entity_id, "name": entity["name"], "type": entity["type"],
                           "description": entity["description"],
                           "mentions": [{"event": key, "field": "with_whom", "mention": mention}
                                        for key, event in self.day.items() for mention in event["with_whom"]
                                        if mention in entity["mentions"]]})
        return chains

    def group_mentions(self, mentions):
        instruction = f"""
            These are mentions of people, groups or animals in the day of {self.name}.
            Group the mentions that refer to the same entity. Return a JSON object with a list of entities, each with
            a short name, a type (person, group or animal), a short description of the relation to {self.name},
            e.g. "{self.name}'s colleague", and the mentions exactly as given. Every mention belongs to one entity.
            """
        schema = {"type": "object", "required": ["entities"], "properties": {"entities": {"type": "array", "items": {
            "type": "object", "required": ["name", "type", "description", "mentions"],
            "properties": {"name": {"type": "string"}, "type": {"type": "string", "enum": ["person", "group", "animal"]},
                           "description": {"type": "string"},
                           "mentions": {"type": "array", "items": {"type": "string", "enum": mentions}}}}}}}
        try:
            response = self.client.chat.completions.create(
                model=self.model, temperature=0,
                messages=[{"role": "system", "content": instruction},
                          {"role": "user", "content": "Mentions:\n" + "\n".join(mentions)}],
                response_format={"type": "json_schema", "json_schema": {"name": "entities", "schema": schema}})
            entities = parse_json(response.choices[0].message.content).get("entities", [])
        except Exception as e:
            print("Could not group the mentions:", e)
            return []
        # a mention can only belong to one entity
        seen = set()
        for entity in entities:
            entity["mentions"] = [mention for mention in entity["mentions"] if mention not in seen]
            seen.update(entity["mentions"])
        return [entity for entity in entities if entity["mentions"]]

    ## Saving
    def save(self, with_chains=False):
        if not self.day:
            return
        if not self.path:
            os.makedirs(self.output_folder, exist_ok=True)
            file_name = f"day_{slug(self.name)[:40]}_{datetime.now():%Y%m%d_%H%M}.json"
            self.path = os.path.join(self.output_folder, file_name)
        day = dict(self.day)
        if with_chains:
            try:
                day["coreference_chains"] = self.get_coreference_chains()
            except Exception as e:
                # the events are always saved, also when the chains cannot be made
                print("Could not make the coreference chains:", e)
        with open(self.path, "w") as json_file:
            json.dump(day, json_file, indent=2, ensure_ascii=False)

    def finish(self):
        # an event of which the user answered only some of the follow-up questions is also kept
        if self.state == "slot" and self.turns:
            self.add_event()
        self.state = "done"
        if not self.day:
            return "Thank you! You did not tell me about any events, so there is nothing to save."
        self.save(with_chains=True)
        events = f"{len(self.day)} event{'s' if len(self.day) > 1 else ''}"
        return f"Thank you for telling me about your day! I saved {events} to {self.get_display_path()}"

    def get_display_path(self):
        """The path of the saved day relative to the root of the project, which is easier to find."""
        path = os.path.abspath(self.path)
        return os.path.relpath(path, PROJECT_ROOT) if path.startswith(PROJECT_ROOT + os.sep) else path


def main():
    parser = argparse.ArgumentParser(description="Scripted agent that asks a user about their day, hour by hour")
    parser.add_argument("--url", default=LLAMA_CPP_URL, help="URL of the llama.cpp server")
    parser.add_argument("--examples", default=EXAMPLE_DAYS, help="Folder with the example days")
    parser.add_argument("--output", default=OUTPUT_FOLDER, help="Folder in which the day is saved")
    parser.add_argument("--ask-all", action="store_true", help="Ask every slot, also when it was already mentioned")
    args = parser.parse_args()

    client = OpenAI(base_url=args.url, api_key="sk-no-key-required")
    try:
        model = client.models.list().data[0].id
    except Exception as e:
        raise SystemExit(f"Could not reach the llama.cpp server at {args.url}, is it running? ({e})")
    print("Model served by llama.cpp:", model)

    agent = DayInterviewer(client, model, args.examples, args.output, args.ask_all)
    print("Agent:", agent.start())
    while not agent.done:
        try:
            utterance = input("You: ")
        except (EOFError, KeyboardInterrupt):
            utterance = "stop"
        print("Agent:", agent.respond(utterance))


if __name__ == "__main__":
    main()
