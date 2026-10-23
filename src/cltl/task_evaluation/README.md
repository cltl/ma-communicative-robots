# task_evaluation: evaluating a collected day against a GOLD day

This module evaluates how well an agent did its task: a day collected by an agent, such as the [day interviewer](../demo_chatbot/README.md), is compared with a GOLD description of the same day, such as the example days in ```data/example_days```. Both are JSON files with the events ```event1```, ```event2```, ... and the ```coreference_chains```, as described in the [README of demo_chatbot](../demo_chatbot/README.md#the-day-descriptions).

| File | Contents |
| --- | --- |
| ```day_evaluation.py``` | The evaluation and a command line interface |
| ```day_evaluation.ipynb``` | Notebook that runs the statistics and the evaluation for two days and shows the results as tables |

To evaluate an agent, pick one of the example days, tell the agent about the day of that person as if it were your own day, and evaluate the collected day against the example day. Or let the [simulated user](../simulated_user/README.md) tell the agent about the day.

## The three levels of the evaluation

* **events**: the collected events are aligned one-to-one with the GOLD events on their start time and overlap in time, their event type and their label (not the description, which is a free sentence). An event without a clock time, e.g. with only ```morning``` in ```when```, gets half of the time similarity if the GOLD event starts in that part of the day. Aligned events are true positives, collected events without a GOLD event are false positives and GOLD events without a collected event are false negatives. Two events are only aligned if their similarity is above the ```EVENT_THRESHOLD``` of 0.55.
* **roles**: for each role (```who```, ```what```, ```with_what```, ```with_whom```, ```where```, ```when```, ```how_long```) of the aligned events: is the role filled in both days? A role filled in both is a true positive, a role filled in the collected event only a false positive, a role filled in the GOLD event only a false negative and a role empty in both a true negative.
* **role-fillers**: do the values of the roles match?

For each level, the evaluation gives a contingency table with the true positives, false positives, false negatives and true negatives, and the precision, recall and f1.

## Matching the values

The values are compared in two modes:

* **exact**: the labels must be the same, after normalising case and punctuation
* **jaccard**: the overlap of the words of the labels, which gives partial credit to partial matches, e.g. ```kitchen of her house``` and ```her kitchen```

In both modes:

* ```where``` and ```when``` are weighted by the specificity of the match: matching ```kitchen``` counts more than matching only ```Amsterdam```, and matching ```07:30``` more than matching only ```morning```
* ```how_long``` gets credit for durations that are close
* ```who``` and ```with_whom``` are matched through the coreference chains, so that ```Lotte```, ```my flatmate``` and ```her flatmate Lotte``` can match the same person
* values with ```<PHOTO>``` are compared with the ```gold``` values in the ```photo``` of the event

## Running the evaluation

From the root of the repository:

```bash
python -m src.cltl.task_evaluation.day_evaluation --key data/example_days/day1_emma_student.json --collected data/collected_days/<your day>.json
```

| Option | Meaning |
| --- | --- |
| ```--key``` | the JSON file with the GOLD day (required) |
| ```--collected``` | the JSON file with the collected day (required) |
| ```--output``` | the JSON file for the results, ```<collected>_vs_<key>_evaluation.json``` by default |
| ```--csv``` | the CSV file for the evaluation per turn, ```<collected>_vs_<key>_turn_evaluation.csv``` by default |
| ```--event-threshold``` | the minimal similarity to align two events, 0.55 by default |
| ```--max-gold-events``` | the number of GOLD events to evaluate against, or ```collected``` |

If the conversation stopped early, add ```--max-gold-events 4``` to evaluate only the first 4 events of the GOLD day, or ```--max-gold-events collected``` for as many GOLD events as were collected (```MAX_GOLD_EVENTS``` in the notebook). The GOLD events that are left out do not count as missed.

The notebook ```day_evaluation.ipynb``` runs the statistics and the evaluation for a collected day and a GOLD day and shows the results as tables, including the aligned and the missed events and the mismatches per role.

## Output

All files are saved next to the collected day:

* ```<collected>_vs_<key>_evaluation.json```: the contingency tables with precision, recall and f1 per level and per role, in both modes, and the aligned events
* ```<collected>_vs_<key>_turn_evaluation.csv```: the evaluation per turn, in the same format as the CSV files of the [EMISSOR analyses](../emissor_evaluation/README.md). It has a row for each question of the agent and each answer of the user (```turn<turn_id>```), the number of events and roles extracted from each turn and the number of correct events and roles in both modes.
* ```<collected>_vs_<key>_turn_effectiveness.json```: the effectiveness of the communication. For the events, the roles and the correct events and roles, it gives the total, the average per turn of the user and the ratio of the total to all turns of the conversation (the questions of the agent included). An agent that gets more correct roles with fewer turns communicates more effectively.

The turn evaluation can be plotted with the [plots](../emissor_evaluation/README.md#plotting-the-scores) of the ```emissor_evaluation``` module, e.g.:

```python
from src.cltl.emissor_evaluation.plots import plot_interaction as plot

settings = plot.PlotSettings()
plot.create_timeline_image_from_csv_columns(csv_file, ["nr_of_events", "nr_of_roles"], settings)
```
