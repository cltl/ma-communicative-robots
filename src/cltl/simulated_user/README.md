# simulated_user: a simulated user for the day interviewer

Talking to an agent about a day takes a lot of time. This module has a **simulated user** that does it for you: an LLM that plays the person of one of the example days in ```data/example_days``` and answers the questions of the agent. It lets you test an agent, such as the [day interviewer](../demo_chatbot/README.md), on all example days and compare versions of the agent in the same way.

| File | Contents |
| --- | --- |
| ```simulated_user.py``` | The ```SimulatedUser```, the conversation loop and a command line interface |
| ```simulated_day_interview.ipynb``` | Notebook that runs a simulated interview, evaluates it and plots it |

## How the simulated user works

The simulated user gets the facts of all the events of the example day from the GOLD JSON: the event type and label, the time, the duration, the place and the people and objects involved. It does **not** get the words of the person in ```human_turn``` and, by default, not the ```description``` of the events, which are sentences written for the GOLD. The LLM answers each question of the agent in the first person, naturally, as that person, with the knowledge of the day and the conversation so far.

The simulated user is not optimised to match the GOLD: like a real user, it describes the day in its own words and the agent has to match what it extracts with a GOLD it does not know. It knows nothing about the strategy of the agent and uses no techniques to interpret the questions. Use ```use_description=True``` (or ```--use-description```) to also give it the descriptions of the events, which makes the answers closer to the GOLD.

The conversation stops when the agent is done, when the agent has collected 20 events (```MAX_EVENTS```), when the agent repeats itself or after 400 turns (```MAX_TURNS```).

Note that the simulated user is an LLM: it can give answers that a real person would not give, and the same LLM is often used by the agent to interpret those answers. Compare the results with conversations with real users.

## Running a simulated interview

Both the agent and the simulated user use the LLM of a running llama.cpp server, see the [installation in the main README](../../../README.md#3-install-llamacpp):

```bash
llama-server -hf Qwen/Qwen2.5-7B-Instruct-GGUF:Q4_K_M --port 8080 -c 4096
```

### In a notebook

```simulated_day_interview.ipynb``` lets you select an example day and then:

1. shows the conversation between the agent and the simulated user in a chat window
2. saves the collected day and the conversation in ```data/simulated_days```
3. computes the statistics of the collected day
4. evaluates the collected day against the example day with the [```task_evaluation```](../task_evaluation/README.md) module
5. converts the conversation to an EMISSOR-style CSV file, plots it and reports the effectiveness of the communication

The settings at the top of the notebook are ```LLAMA_CPP_URL```, ```MAX_EVENTS```, ```USE_DESCRIPTION``` and ```PART_OF_DAY```.

### From the command line

From the root of the repository:

```bash
python -m src.cltl.simulated_user.simulated_user --day data/example_days/day1_emma_student.json
```

| Option | Meaning |
| --- | --- |
| ```--day``` | the JSON file with the example day (required) |
| ```--url``` | the address of the llama.cpp server, ```http://localhost:8080/v1``` by default |
| ```--output``` | the folder in which the collected day is saved, ```data/simulated_days``` by default |
| ```--max-events``` | stop after this number of events, 20 by default |
| ```--use-description``` | also give the descriptions of the events to the simulated user |
| ```--part-of-day``` | let the agent ask per part of the day instead of hour by hour |

The collected day is saved as ```day_<name>_<strategy>_<date>.json``` and the conversation next to it as ```day_<name>_<strategy>_<date>_conversation.csv```, with the columns ```Turn```, ```Turn nr.```, ```Speaker``` and ```Response``` of the EMISSOR evaluation files. Evaluate it against the example day with:

```bash
python -m src.cltl.task_evaluation.day_evaluation --key data/example_days/day1_emma_student.json --collected data/simulated_days/<your day>.json
```

## Interviewing the simulated user with your own agent

```simulate_day``` always interviews the ```DayInterviewer```. To test your own agent, create the simulated user and call ```run_interview``` with your agent. It works with any agent with a ```start()``` method that returns the first utterance, a ```respond(utterance)``` method that returns the next utterance, a ```done``` property and a ```day``` dictionary with the collected events:

```python
import json
from src.cltl.simulated_user.simulated_user import SimulatedUser, run_interview, save_conversation

with open("data/example_days/day1_emma_student.json") as json_file:
    day = json.load(json_file)
user = SimulatedUser(client, model, day)
conversation = run_interview(my_agent, user, on_turn=lambda speaker, text: print(f"{speaker}: {text}"))
```
