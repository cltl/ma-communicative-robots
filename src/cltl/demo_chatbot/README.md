# demo_chatbot: the day interviewer

This module has a scripted conversational agent, the **day interviewer**, that asks a user about their day and stores the answers as a structured description of the events of that day. The collected day can be evaluated against a GOLD day with the [```task_evaluation```](../task_evaluation/README.md) module.

The day interviewer is a simple baseline: the dialogue is scripted and always asks the same questions in the same order. Try it out, find out where it goes wrong and build a better agent.

| File | Contents |
| --- | --- |
| ```day_interviewer.py``` | The ```DayInterviewer``` agent and a command line interface |
| ```day_interviewer.ipynb``` | Notebook that runs the agent in a chat window, with both strategies, and compares the collected days |
| ```chat_window.py``` | A chat window for Jupyter notebooks with ```ipywidgets``` |
| ```day_statistics.py``` | Statistics of a day file |

## The day descriptions

A day is a JSON file with the events ```event1```, ```event2```, ... and the ```coreference_chains``` of the people in the events, as in the examples in ```data/example_days```. Each event has the following fields:

* ```event_type``` (e.g. ```meal```, ```travel```, ```work```), ```event_label``` and ```description```
* ```human_turn```: a list with the turns of the user about the event, each turn with its number in the conversation and the utterance, e.g. ```{"turn_id": 10, "utterance": "I woke up to my phone alarm."}```
* ```agent_turn```: only in the collected days, a list with the questions of the agent about the event in the same structure, e.g. ```{"turn_id": 9, "utterance": "What did you do at 7 o'clock?"}```. ```human_turn[i]``` is the answer to ```agent_turn[i]``` (with an empty utterance if the question was skipped). The example days have no conversation with an agent, their turns are numbered in the order of the events
* the roles of the event: ```who```, ```what```, ```with_what``` and ```with_whom``` (lists of values), ```where``` (a list of places from the most specific to the most general, e.g. ```["kitchen", "her flat", "Amsterdam", "Netherlands", "Europe"]```), ```when``` (a list from the most specific to the most general time, e.g. ```["07:30", "half past seven", "7 o'clock", "early in the morning", "morning"]```) and ```how_long``` (minutes)

In some of the example days, a role has the value ```<PHOTO>```: the value is shown on a photo in ```data/example_days/photos``` and the GOLD value is given in the ```photo``` field of the event.

Each coreference chain is an entity (a person, group or animal) with the mentions of that entity in the ```who``` and ```with_whom``` roles of the events.

## How the day interviewer works

The agent first asks for the name of the user, the pronoun to use and the town and country where the user lives, and then asks about the day with one of two strategies.

**Hour by hour** (the default): the agent asks at what hour the day started and then what the user did at each hour. After the answer, it asks follow-up questions for the details that the user did not mention yet: with whom, what, with what, where, when exactly and for how long. An LLM decides which details were already mentioned and fills the roles of the event from all the answers, with events from the example days as examples. After each event, the agent moves on to the hour after the end of the event, until the user stops or the day is over. With ```ask_all=True``` (or ```--ask-all```), the agent asks every follow-up question, also when the user already mentioned the detail.

**Part of the day** (```part_of_day=True``` or ```--part-of-day```): the agent only asks what the user did in the morning, in the afternoon and in the evening. The LLM extracts all the activities from each answer as events in temporal order, using only what the user said. Without follow-up questions, a start time or duration that is not given is left out: ```when``` only has the part of the day and ```how_long``` is ```null```. This minimises the number of turns, but fewer roles are filled.

**Photos**: when the user says to have a photo of an activity, the agent asks what is on it. As in the example days, the roles that the photo shows get the value ```<PHOTO>``` and their values are kept in the ```photo``` of the event (```note```, ```fills```, ```gold``` and ```people_in_photo```).

The day is saved after each event in ```data/collected_days/day_<name>_<strategy>_<date>.json```, where ```<strategy>``` is ```hour_by_hour``` or ```part_of_day```. The coreference chains are added when the conversation is stopped.

## Running the day interviewer

The agent needs a running llama.cpp server, see the [installation in the main README](../../../README.md#3-install-llamacpp):

```bash
llama-server -hf Qwen/Qwen2.5-7B-Instruct-GGUF:Q4_K_M --port 8080 -c 4096
```

### In a notebook

Open ```day_interviewer.ipynb```. It connects to the server, shows the conversation in a chat window with an adjustable font size and shows the collected day as a table. The settings at the top of the notebook are:

* ```LLAMA_CPP_URL```: the address of the llama.cpp server, ```http://localhost:8080/v1``` by default
* ```ASK_ALL```: ask every follow-up question
* ```PART_OF_DAY```: ask per part of the day instead of hour by hour

The notebook also compares a day collected hour by hour with a day collected per part of the day, event by event and role by role.

Click **Stop** in the chat window or type ```stop```, ```bye``` or ```done``` to end the conversation.

### From the command line

From the root of the repository:

```bash
python -m src.cltl.demo_chatbot.day_interviewer
python -m src.cltl.demo_chatbot.day_interviewer --part-of-day
```

| Option | Meaning |
| --- | --- |
| ```--url``` | the address of the llama.cpp server, ```http://localhost:8080/v1``` by default |
| ```--examples``` | the folder with the example days, ```data/example_days``` by default |
| ```--output``` | the folder in which the day is saved, ```data/collected_days``` by default |
| ```--ask-all``` | ask every follow-up question |
| ```--part-of-day``` | ask per part of the day instead of hour by hour |

### Using the agent in your own code

```python
from openai import OpenAI
from src.cltl.demo_chatbot.day_interviewer import DayInterviewer

client = OpenAI(base_url="http://localhost:8080/v1", api_key="sk-no-key-required")
model = client.models.list().data[0].id
agent = DayInterviewer(client, model)

print(agent.start())
while not agent.done:
    print(agent.respond(input("You: ")))
```

Any agent with a ```start()``` method that returns the first utterance, a ```respond(utterance)``` method that returns the next utterance and a ```done``` property can be shown in the ```ChatWindow``` and interviewed by the [simulated user](../simulated_user/README.md).

## The chat window

```chat_window.py``` has the ```ChatWindow``` for Jupyter notebooks, in which the questions of the agent and the answers of the user are shown together:

```python
from src.cltl.demo_chatbot.chat_window import ChatWindow

ChatWindow(agent, font_size=16).show()
```

## Statistics of a day

```day_statistics.py``` gives the number of events, the number of filled roles, the number of coreference chains, the average number of mentions per chain and the unique values of ```what``` and ```with_what``` with their frequencies. The statistics are saved next to the day as ```<name>_meta.json```. Pass one or more day files or folders with day files:

```bash
python -m src.cltl.demo_chatbot.day_statistics data/example_days data/collected_days
```
