#  Conversational AI & Robots, 2026

Conversational AI & Robots is a master's course taught at the Vrije Universiteit Amsterdam.
We use the LEOLANI platform for interacting with agents and robots (Baier et al 2025). 
Interactions through LEOLANI are captured in the EMISSOR format (Baez et al 2022). 
[EMISSOR](https://github.com/leolani/cltl-combot/blob/main/src/cltl/combot/event/emissor.py) is a frequently used JSON structure in which interactions are stored on disk as ```scenarios``` in separate folders.
EMISSOR stores incoming streams of signals (audio, text, image) as separate data points that are aligned through a temporal ruler that is shared by the scenario.

This project shows how interactions saved in EMISSOR can be analysed and evaluated in different way:

* scoring the likelihood of turns based on the previous context using a transformer model and masked token predictions
* scoring the coherence of turns based on the previous context using a generative LLM as a judge
* scoring dialogue acts as positive, negative or neutral moves in the interaction
* scoring the emotions expressed in each turn as positive, negative or neutral moves in the interaction
* evaluating the properties of knowledge added to a knowledge graph on a positive/negative axis
* human assessment of each turn on a likert scale

For each of the above analysis, a notebook is provided that shows how one or more EMISSOR scenarios can be loaded and scored according to the method.
The result of the scoring is saved in a CSV file in an ```evaluation``` folder, where each row contains the ```turn id```, the ```speaker```, the ```utterance``` and additional values for the analysis and the scores.

The ```plots``` module has two notebooks for reading the CSV files and generating plots for each interaction that show the conversation on the X-axis as a sequence of turns and the scored analysis on the Y-axis.
Each turn is shown on the X-axis with its number, speaker and utterance, and each data point is labelled with its score. An additional label can be added to the data points with ```label_column```, e.g. the dialogue act (```dialogue_act```) or the emotion (```go_emotion```).

In addition, the project has a task-based evaluation: an agent collects a description of a day in somebody's life and the collected description is evaluated against a GOLD description of that day (see [Task-based evaluation: describing a day](#task-based-evaluation-describing-a-day)).

The ```data``` folder contains:

* ```emissor```: the interaction data for a few scenarios to demonstrate the notebooks. Replace the path to your own emissor data to apply the analysis on your interactions.
* ```example_days```: five GOLD descriptions of a day in somebody's life, with 20 events each, and a ```photos``` folder with photos of some of the events.
* ```collected_days```: the days collected by the day interviewer agent. This folder is created when you save your first day.
* ```simulated_days```: the days collected by the day interviewer agent from a simulated user.

## How to proceed

1. Apply any of the analyses (likelihood, coherence, dialogue act, emotion) to the scenario of your choice by adapting the path to your emissor folder and the name of your scenario to the corresponding notebook. The output is saved in a CSV file in the ```evaluation``` folder. 
2. Create a plot for any of the saved CSV file or combine CSV files in a single plot. You can use ```metrics_plotting.ipynb``` or ```plot_analysis_from_csv.ipynb``` for plotting.

You could also create your own code to create a CSV file following the same format and plot the result.

In addition to plotting the interactions with the result of the analysis, the notebooks also provide other results in each analysis notebook.

## Task-based evaluation: describing a day

In this task, an agent asks a user about their day and stores the answers as a structured description of the events of that day. The quality of the conversation is then measured by how well the collected description matches a GOLD description of the same day.

### The day descriptions

A day is a JSON file with the events ```event1```, ```event2```, ... and the ```coreference_chains``` of the people in the events, as in the examples in ```data/example_days```. Each event has the following fields:

* ```event_type``` (e.g. ```meal```, ```travel```, ```work```), ```event_label``` and ```description```
* ```human_turn```: a list with the turns of the user about the event, each turn with its number in the conversation and the utterance, e.g. ```{"turn_id": 10, "utterance": "I woke up to my phone alarm."}```
* ```agent_turn```: only in the collected days, a list with the questions of the agent about the event in the same structure, e.g. ```{"turn_id": 9, "utterance": "What did you do at 7 o'clock?"}```. ```human_turn[i]``` is the answer to ```agent_turn[i]``` (with an empty utterance if the question was skipped). The example days have no conversation with an agent, their turns are numbered in the order of the events
* the roles of the event: ```who```, ```what```, ```with_what``` and ```with_whom``` (lists of values), ```where``` (a list of places from the most specific to the most general, e.g. ```["kitchen", "her flat", "Amsterdam", "Netherlands", "Europe"]```), ```when``` (a list from the most specific to the most general time, e.g. ```["07:30", "half past seven", "7 o'clock", "early in the morning", "morning"]```) and ```how_long``` (minutes)

In some of the example days, a role has the value ```<PHOTO>```: the value is shown on a photo in ```data/example_days/photos``` and the GOLD value is given in the ```photo``` field of the event.

Each coreference chain is an entity (a person, group or animal) with the mentions of that entity in the ```who``` and ```with_whom``` roles of the events.

### 1. Collecting a day with the day interviewer

The day interviewer in ```src/cltl/demo_chatbot``` is a scripted agent that asks the user about their day, hour by hour: what did you do at hour X, with whom, what, with what, where, when and for how long. It only asks the follow-up questions for the details that the user did not mention yet. An LLM served by a local [llama.cpp](https://github.com/ggml-org/llama.cpp) server interprets the answers and fills the roles of the event. After each event, the agent moves on to the next hour after the event, until the user stops or the day is over. When the user says to have a photo of an activity, the agent asks what is on it: as in the example days, the roles that the photo shows get the value ```<PHOTO>``` and their values are kept in the ```photo``` of the event (```note```, ```fills```, ```gold``` and ```people_in_photo```).

With ```--part-of-day``` (or ```PART_OF_DAY = True``` in the notebooks), the agent only asks what the user did in the morning, in the afternoon and in the evening. The LLM extracts all the activities from each answer as events in temporal order, using only what the user said: without follow-up questions, a start time or duration that is not given is left out (```when``` only has the part of the day, ```how_long``` is ```null```). This minimises the number of turns, but the coverage of the roles is poor. In the evaluation, an event without a clock time can be aligned with a GOLD event in the same part of the day.

Start the llama.cpp server with a model before running the agent, e.g.:

```bash
llama-server -hf Qwen/Qwen2.5-7B-Instruct-GGUF:Q4_K_M --port 8080 -c 4096
```

Then open the notebook ```src/cltl/demo_chatbot/day_interviewer.ipynb```, which shows the conversation in a chat window with an adjustable font size, or run the agent from a terminal in the root of the project:

```bash
python -m src.cltl.demo_chatbot.day_interviewer
```

Click **Stop** in the chat window or type ```stop```, ```bye``` or ```done``` to end the conversation. The day is saved after each event in ```data/collected_days/day_<name>_<strategy>_<date>.json``` (```<strategy>``` is ```hour_by_hour``` or ```part_of_day```), and the coreference chains are added when the conversation is stopped. Note that ```data``` is in ```.gitignore```, so your collected days are not committed.

### 2. Statistics of a day

```src/cltl/demo_chatbot/day_statistics.py``` gives the number of events, the number of filled roles, the number of coreference chains, the average number of mentions per chain and the unique values of ```what``` and ```with_what``` with their frequencies. The statistics are saved next to the day as ```<name>_meta.json```:

```bash
python -m src.cltl.demo_chatbot.day_statistics data/example_days data/collected_days
```

### 3. Evaluating a collected day against a GOLD day

```src/cltl/task_evaluation/day_evaluation.py``` evaluates a collected day against a GOLD day on three levels:

* **events**: the collected events are aligned one-to-one with the GOLD events on their time, event type and label (not the description, which is a free sentence)
* **roles**: are the roles of the aligned events filled in both days?
* **role-fillers**: do the values of the roles match?

For each level, it gives a contingency table with the true positives, false positives, false negatives and true negatives (only defined for roles) and the precision, recall and f1. The values are compared in two modes: an **exact** match of the labels and a **jaccard** match of the words of the labels, which gives partial credit to partial matches. In both modes, ```where``` and ```when``` are weighted by the specificity of the match and ```who``` and ```with_whom``` are matched through the coreference chains.

```bash
python -m src.cltl.task_evaluation.day_evaluation --key data/example_days/day1_emma_student.json --collected data/collected_days/<your day>.json
```

The results are saved next to the collected day as ```<collected>_vs_<key>_evaluation.json```.
If the conversation stopped early, add ```--max-gold-events 4``` to evaluate only the first 4 events of the GOLD day, or ```--max-gold-events collected``` for as many GOLD events as were collected (```MAX_GOLD_EVENTS``` in the notebooks). The GOLD events that are left out do not count as missed.
The evaluation per turn of the user is saved as ```<collected>_vs_<key>_turn_evaluation.csv```, in the same format as the CSV files of the EMISSOR analyses, with a row for each question of the agent and each answer of the user (```turn<turn_id>```), the number of events and roles extracted from each turn and the number of correct events and roles in both modes. The effectiveness of the communication is reported and saved as ```<collected>_vs_<key>_turn_effectiveness.json```: for the events, the roles and the correct events and roles, the total, the average per turn of the user and the ratio of the total to all turns of the conversation (the questions of the agent included). An agent that gets more correct roles with fewer turns communicates more effectively. The turn evaluation can be plotted with the ```plots``` module, e.g. with ```create_timeline_image_from_csv_columns(csv_file, ["nr_of_events", "nr_of_roles"], settings)```. The notebook ```src/cltl/task_evaluation/day_evaluation.ipynb``` runs the statistics and the evaluation for two days and shows the results as tables, including the aligned and missed events.

To evaluate the agent, pick one of the example days, tell the agent about the day of that person as if it were your own day, and evaluate the collected day against the example day.

### 4. Simulating the user

Instead of telling the agent about an example day yourself, a simulated user can do it. ```src/cltl/simulated_user/simulated_user.py``` plays the person of an example day: an LLM gets the facts of all the events of that day from the GOLD JSON, but not the words of the person in ```human_turn``` and, by default, not the ```description``` of the events, and answers the questions of the agent naturally as that person. The simulated user is not optimised to match the GOLD: like a real user, it describes the day in its own words and the agent has to match what it extracts with a GOLD it does not know. Use ```--use-description``` (or ```USE_DESCRIPTION = True``` in the notebook) to also give it the descriptions, which makes the answers closer to the GOLD. It knows nothing about the strategy of the agent and uses no techniques to interpret the questions. The conversation stops when the agent is done, when the agent has collected 20 events, when the agent repeats itself or after a maximum number of turns.

The notebook ```src/cltl/simulated_user/simulated_day_interview.ipynb``` lets you select an example day, shows the conversation between the agent and the simulated user in a chat window, saves the collected day and the conversation in ```data/simulated_days```, computes the statistics, evaluates the collected day against the example day and converts the conversation to an EMISSOR CSV file that is plotted and reports the effectiveness of the communication. A simulated interview can also be run from a terminal:

```bash
python -m src.cltl.simulated_user.simulated_user --day data/example_days/day1_emma_student.json
```

## Requirements

Clone this repository to prepare for the course:

```bash
   >git clone git@github.com:cltl/ma-communicative-robots.git
   >cd ma-communicative-robots
```

Create a virtual environment for running the code.

Using venv:
   ```bash
    python3.11 -m venv evaluate
    source evaluate/bin/activate
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    python -m ipykernel install --user --name=evaluate
   ```

Using Conda:
```bash
    conda create -n evaluate python=3.11
    conda activate evaluate
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    python -m ipykernel install --user --name=evaluate
```

With the environment active, launch Jupyter lab from the CLI and open the notebooks.

The LLM as a judge notebook and the day interviewer also need a local installation of [llama.cpp](https://github.com/ggml-org/llama.cpp) (e.g. ```brew install llama.cpp``` on macOS) and a model in GGUF format, e.g. from [huggingface.co](https://huggingface.co/models?library=gguf).

## References
Feel free to use our work but cite us:
* Baez Santamaria, S., Baier, T., Kim, T., Krause, L., Kruijt, J., & Vossen, P. (2021). EMISSOR: A platform for capturing multimodal interactions as episodic memories and interpretations with situated scenario-based ontological references. In Proceedings of the First workshop Beyond Language: Multimodal Semantic Representations in conjunction with IWCS 2022
* T. Baier, S. Báez Santamaría, P. Vossen: A modular architecture for creating multimodal embodied agents with an episodic Knowledge Graph as an explainable and controllable long-term memory, in: Dialogue & Discourse Volume 14, ed. 3, pages 25-59

## Troubleshooting

The best way to find and solve your problems is to see in the github issue tab. If you can't find what you want, feel free to raise an issue. We are pretty responsive.

## Contributing

Contributions are what make the open source community such an amazing place to be learn, inspire, and create. Any contributions you make are **greatly appreciated**.

1. Fork the Project
1. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
1. Run `make style && make quality` in the root repo directory, to ensure code quality.
1. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
1. Push to the Branch (`git push origin feature/AmazingFeature`)
1. Open a Pull Request

## Authors

- Piek Vossen (piek.vossen@vu.nl)
- Thomas Baier (t.baier@vu.nl)
