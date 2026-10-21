"""A simulated user that answers the questions of an agent, such as the DayInterviewer, with the knowledge of an
example day.

The simulated user plays the person of an example day in data/example_days: an LLM served by a llama.cpp server gets
the facts of all the events of that day from the GOLD JSON and answers the questions of the agent naturally, as that
person, in the first person. The words of the person in human_turn are not used, so the LLM has to put the facts in
its own words. The simulated user knows nothing about the strategy of the agent and uses no techniques to interpret
the questions: the LLM answers each question with the knowledge of the day and the conversation so far.
The collected day can then be evaluated against the example day as GOLD, see
src/cltl/task_evaluation/day_evaluation.py.

Run an interview from the root of the project, with the llama.cpp server running:

    python -m src.cltl.simulated_user.simulated_user --day data/example_days/day1_emma_student.json
"""
import argparse
import csv
import json
import os
import re
from collections import Counter

from openai import OpenAI

from src.cltl.demo_chatbot.day_interviewer import DayInterviewer, LLAMA_CPP_URL, PROJECT_ROOT
from src.cltl.demo_chatbot.day_statistics import get_events, get_role_values

OUTPUT_FOLDER = os.path.join(PROJECT_ROOT, "data", "simulated_days")
STOP_UTTERANCE = "stop"
MAX_EVENTS = 20
MAX_TURNS = 400
# The conversation is stopped when the agent says the same thing this number of times in a row
MAX_REPEATS = 3
# The number of earlier turns of the conversation that the LLM gets with the question, the whole conversation
# does not fit in the context of the LLM together with the facts of the day
NR_OF_HISTORY_TURNS = 12

ROLES = ["who", "with_whom", "what", "with_what", "where", "how_long"]


## THE PERSON OF THE DAY
def get_minutes(time):
    hour, minute = str(time).split(":")[:2]
    return int(hour) * 60 + int(minute)

def get_name(day):
    """The name of the narrator: the entity of the coreference chains that is mentioned in who, or the first who."""
    for chain in day.get("coreference_chains", []):
        if any(mention.get("field") == "who" for mention in chain.get("mentions", [])):
            return chain.get("name")
    events = list(get_events(day).values())
    return (get_role_values(events[0], "who") or ["the user"])[0] if events else "the user"

def get_pronoun(events):
    """The pronoun of the narrator, from the possessive pronouns in the descriptions and places of the events,
    e.g. 'her student flat'. They if the day does not tell."""
    words = Counter(word for event in events
                    for text in [event.get("description", "")] + get_role_values(event, "where")
                    for word in re.findall(r"[a-z]+", str(text).lower()))
    if words["her"] > words["his"]:
        return "she"
    if words["his"] > words["her"]:
        return "he"
    return "they"

def get_home(events):
    """The town and country where the narrator lives: the most frequent town and country in the places of the events,
    which end with the town, the country and the continent."""
    places = Counter(tuple(where[-3:-1]) for event in events
                     for where in [get_role_values(event, "where")] if len(where) >= 3)
    return ", ".join(places.most_common(1)[0][0]) if places else "unknown"

def to_first_person(text):
    """The facts of the example days are about the narrator in the third person, e.g. 'her student flat'.
    The LLM gets them in the first person, 'my student flat', so that it can use them as they are in its answers."""
    text = re.sub(r"\b(she|he|they)\b", "I", str(text))
    return re.sub(r"\b(her|his|their)\b", "my", text)

def get_end(event):
    end = get_minutes(event["when"][0]) + event["how_long"]
    return f"{end // 60 % 24:02d}:{end % 60:02d}"

def describe_event(event):
    """The facts of an event for the LLM in the first person, from the GOLD values (also the values on a photo).
    The words of the person in human_turn are not used."""
    lines = [f"From {event['when'][0]} to {get_end(event)} ({event['how_long']} minutes): "
             f"{event['event_label']}, I {to_first_person(event['description'])}"]
    for role in ROLES:
        values = get_role_values(event, role)
        if role == "with_whom" and not values:
            values = ["nobody, I was alone"]
        if values:
            values = ", ".join(to_first_person(value) for value in values)
            lines.append(f"  {role.replace('_', ' ')}: {values}")
    return "\n".join(lines)


class SimulatedUser():
    def __init__(self, client: OpenAI, model, day):
        """Creates a simulated user that answers with the knowledge of a day.
        params
        client: OpenAI client for the llama.cpp server
        model: the model served by llama.cpp
        day: the example day as a dictionary, as loaded from the JSON file
        """
        self.client = client
        self.model = model
        events = sorted(get_events(day).values(), key=lambda event: get_minutes(event["when"][0]))
        self.name = get_name(day)
        self.pronoun = get_pronoun(events)
        self.home = get_home(events)
        facts = "\n\n".join(describe_event(event) for event in events)
        self.instruction = f"""
            You are {self.name}. You live in {self.home} and people refer to you as {self.pronoun}. Someone asks you
            about your day. Answer naturally, as {self.name} would answer in a conversation, in the first person.
            Use what you know about your day below and do not make up anything else. You are a person being
            interviewed, not an assistant: keep your answers short and do not ask questions back or offer help.

            Your day:
            {facts}
            """
        self.history = []

    def respond(self, agent_utterance):
        """The answer of the LLM to an utterance of the agent, with the knowledge of the day."""
        messages = ([{"role": "system", "content": self.instruction}]
                    + self.history[-NR_OF_HISTORY_TURNS:] + [{"role": "user", "content": agent_utterance}])
        response = self.client.chat.completions.create(model=self.model, messages=messages, temperature=0,
                                                       max_tokens=150)
        answer = response.choices[0].message.content.strip()
        self.history += [{"role": "user", "content": agent_utterance}, {"role": "assistant", "content": answer}]
        return answer


## THE INTERVIEW
def run_interview(agent, user, max_events=MAX_EVENTS, max_turns=MAX_TURNS, on_turn=None):
    """Lets the simulated user answer the agent until the agent is done, e.g. when the day is over or when the
    simulated user ends the conversation itself. So that the conversation cannot go on forever, the interview says
    'stop' instead of the simulated user when the agent collected max_events events, when the agent says the same
    thing MAX_REPEATS times in a row or after max_turns turns.
    on_turn(speaker, text) is called for every turn, e.g. to show the conversation. Returns the conversation as a
    list of (speaker, text)."""
    conversation = []

    def add_turn(speaker, text):
        conversation.append((speaker, text))
        if on_turn:
            on_turn(speaker, text)

    question = agent.start()
    add_turn("Agent", question)
    repeats = 1
    try:
        while not agent.done:
            if len(agent.day) >= max_events or len(conversation) >= max_turns or repeats >= MAX_REPEATS:
                answer = STOP_UTTERANCE
            else:
                answer = user.respond(question)
            add_turn(user.name, answer)
            next_question = agent.respond(answer)
            repeats = repeats + 1 if next_question == question else 1
            question = next_question
            add_turn("Agent", question)
    except KeyboardInterrupt:
        # stopping the kernel or pressing ctrl-c ends the conversation, the day is saved with the events so far
        if not agent.done:
            add_turn("Agent", agent.finish())
    return conversation

def save_conversation(conversation, day_file):
    """Saves the conversation next to the collected day as <day>_conversation.csv, with the columns Turn, Speaker and
    Response of the evaluation files of the EMISSOR scenarios."""
    path = os.path.splitext(day_file)[0] + "_conversation.csv"
    with open(path, "w", newline="") as csv_file:
        writer = csv.writer(csv_file, delimiter=";")
        writer.writerow(["Turn", "Turn nr.", "Speaker", "Response"])
        for i, (speaker, text) in enumerate(conversation):
            writer.writerow([f"turn{i + 1}", i, "AGENT" if speaker == "Agent" else speaker, text])
    return path

def simulate_day(client, model, day_file, output_folder=OUTPUT_FOLDER, max_events=MAX_EVENTS, max_turns=MAX_TURNS,
                 on_turn=None):
    """Runs an interview of the DayInterviewer with a simulated user of the example day in day_file. The collected day
    and the conversation are saved in output_folder. Returns the agent, the simulated user and the conversation."""
    with open(day_file) as json_file:
        day = json.load(json_file)
    agent = DayInterviewer(client, model, output_folder=output_folder)
    user = SimulatedUser(client, model, day)
    conversation = run_interview(agent, user, max_events, max_turns, on_turn)
    if agent.path:
        save_conversation(conversation, agent.path)
    return agent, user, conversation


def main():
    parser = argparse.ArgumentParser(description="Interview a simulated user of an example day with the day interviewer")
    parser.add_argument("--day", required=True, help="JSON file with the example day")
    parser.add_argument("--url", default=LLAMA_CPP_URL, help="URL of the llama.cpp server")
    parser.add_argument("--output", default=OUTPUT_FOLDER, help="Folder in which the collected day is saved")
    parser.add_argument("--max-events", type=int, default=MAX_EVENTS, help="Stop after this number of events")
    args = parser.parse_args()

    client = OpenAI(base_url=args.url, api_key="sk-no-key-required")
    model = client.models.list().data[0].id
    agent, _, _ = simulate_day(client, model, args.day, args.output, args.max_events,
                               on_turn=lambda speaker, text: print(f"{speaker}: {text}"))
    print("Saved the collected day to", agent.path)


if __name__ == "__main__":
    main()
