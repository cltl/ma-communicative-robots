# Tae's group Combots 2021, Vrije Universiteit Amsterdam

This year we work on a "A Machine With Human-Like Memory Systems"

## Prerequisites

1. A unix or unix-like x86 machine
1. python 3.7 or higher. Running in a virtual environment (e.g., conda, virtualenv, etc.) is highly recommended so that you don't mess up with the system python.
1. `pip install -r requirements.txt`

## Data

The generated data is saved at `./data/`.

Take a look at the example jupyter notebook `./notebooks/how-to-data.ipynb` and `./notebooks/prompt.ipynb`, to have a rough idea.

## [`run_prompts.py`](./run_prompts.py)

This script runs a prompt with a specified model. You should run it with the below command

```sh
python run_prompts.py --model_name MODEL_NAME --prompt PROMPT
```

where `MODEL_NAME` and `PROMPT` is your desired model and prompt, respectively.

For example, if you run `python run_prompts.py --model_name t5.1.1.lm100k.base --prompt baseline`, the script will run the `t5.1.1.lm100k.base` model with the `baseline` prompt. This script also supports `t0pp` as a model, but you'll need to have at least 90GB of CPU memory. Tae'll run it on his server.

The prompt is something you (Fajjaaz, Nicole, and Hidde) have to engineer. You use your imagination to come up with a better prompt template than the baseline. Once you are sure with your prompt after running it on the validation split with the `t5.1.1.lm100k.base` model, Tae'll run your prompt in the server with `t0pp`.

The most important thing here is that we have a common structure so that the scripts can run smoothly. More specifically, you have to make your own prompt class by subclassing the class `PromptTemplate`. This class is really simple:

```python
class PromptTemplate:
    """Prompt template class. The students have to subclass this class, and make their
    own template."""

    def __init__(self) -> None:
        raise NotImplementedError

    def generate_prompt(self, sample: dict) -> str:
        """Generate a prompt given a sample.

        Args
        ----
        sample: a dictionary with the following key: value pairs
            'episodic_memory_system': episodic memory system at time t.
            'semantic_memory_system': semantic memory system at time t.
            'question': question to be answered at time t.
            'prediction_hand_crafted': prediction by the hand-crafted heuristics.
            'correct_answer': correrct answer.

        """
        raise NotImplementedError
```

You just to inherit this class and make your own with by overriding the `__init__()` method and `generate_prompt()` method. Let's take a look at how Tae created his baseline prompt class:

```python
class Baseline(PromptTemplate):
    """Baseline prompt.

    This is the simplest prompt.

    """

    def __init__(self) -> None:
        logging.info("baseline prompt is initialized!")

    def generate_prompt(self, sample: dict) -> str:
        sample["episodic_memory_system"] = sorted(
            sample["episodic_memory_system"], key=lambda x: x[-1]
        )
        for idx, mem in enumerate(sample["episodic_memory_system"]):
            max_len = len(sample["episodic_memory_system"])
            days = len(sample["episodic_memory_system"]) - idx - 1
            if days == 0:
                timestamp = "today"
            else:
                timestamp = f"{days} days ago"
            sample["episodic_memory_system"][idx][-1] = timestamp

        prompt = []

        for mem in sample["episodic_memory_system"]:
            prompt.append(f"{mem[0]} was at {mem[2]}, {mem[3]}.")

        for mem in sample["semantic_memory_system"]:
            prompt.append(f"{mem[-1]} {mem[0]} were found at {mem[2]}.")

        prompt.append(f"Where is {sample['question'][0]}?")

        prompt = " ".join(prompt)

        return prompt
```

It's pretty simple.

Once you made your own prompt template, then you can run `run_prompts.py` with your own flag. But before this, you also have to modify the `PromptWrapper` class. You have to add your prompt to the line 271:

```python
if prompt.lower() == "baseline":
    self.prompt = Baseline()
```

Here you have to write something like:

```python
else prompt.lower() == "foo":
    self.prompt = Foo()
```

`run_prompts.py` will save the results in the directory `./results/` with a directory named `MODEL_PROMPT`. For example, at the moment you'll find two directories there: `t0pp_baseline` and `t5.1.1.lm100k.base_baseline`. These are running `t0pp` and `t5.1.1.lm100k.base` with the `baseline` prompt.

Good luck. As always, contact Tae if you have further questions.

## [`evaluation.py`](./evaluation.py)

This is mainly Nihed's job, but others can also run `evaluation.py` to see how well your prompt performs. You should run this script with the below command:

```sh
python evaluation.py --results_path RESULTS_PATH
```

`RESULTS_PATH` should be a directory path in the `results` directory. It will look something like this `results/t5.1.1.lm100k.base_baseline`. Here we want to evaluate the results of the model `t5.1.1.lm100k.base` with the prompt `baseline`.

At the moment, the evaluation metric is only simple global_accuracy. Nihed will implement other metrics and then modify the `evaluation_wrapper` method. Its argument `metrics` is currently by default `metrics: list = ["global_accuracy"]`. More metrics sholud be added to this list.

Nihed should also change the line 50:

```python
if metric.lower() == "global_accuracy":
    global_accuracy = evaluate(
        predictions, correct_answers, metric=metric.lower()
    )
    evaluation[item][split] = global_accuracy
```

by adding something like:

```python
elif metric.lower() == "bleu":
    bleu_score = evaluate(
        predictions, correct_answers, metric=metric.lower()
    )
    evaluation[item][split] = bleu_score
```

She should also modify the `evaluate()` method which currently looks like this:

```python
def evaluate(
    predictions: list, correct_answers: list, metric: str = "global_accuracy"
) -> float:
    """Evaluate the predictions using the metric.

    Args
    ----
    predictions: A list of predictions. Every element is an output of LM.
    correct_answers: A list of correct answers. Every element is the correct location
        of the query object.

    """
    if metric.lower() == "global_accuracy":

        T = 0
        F = 0
        for answer, pred in zip(correct_answers, predictions):
            if answer in pred:
                T += 1
            else:
                F += 1

        global_acc = T / (T + F)
        logging.info(f"T: {T}, F: {F}")
        logging.info(f"global accuracy is {global_acc}")

        return global_acc

    elif metric.lower() == "bleu":
        # TODO: Nihed's job
        raise NotImplementedError
    elif metric.lower() == "rouge":
        # TODO: Nihed's job
        raise NotImplementedError
    elif metric.lower() == "f1":
        # TODO: Nihed's job
        raise NotImplementedError
    else:
        # TODO: Nihed's job
        raise ValueError
```

## Running the best prompt on our own data

Once we are more confident with our prompts, we'll run it on our data that we've collected.
Tae is currently working on converting our google spreadsheet data into jsons so that they are compatiable with our classes and functions.

Using the various metrics, we'll choose about 3 different prompts, and run them our own data with `t0pp`. It'll give us a good insight how our prompts can generalize to unseen data that we've collected ourselves.

## Authors

- [Taewoon Kim](https://taewoonkim.com/)
- Fajjaaz Chandoe
- Nihed Harrak
- Nicole van de Weijer
- Hidde van Oijen
