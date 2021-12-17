import argparse
import json
import logging
import os
import re
from glob import glob
from typing import Tuple

from tqdm import tqdm

logging.basicConfig(
    level=os.environ.get("LOGLEVEL", "INFO").upper(),
    format="%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


def read_json(path: str) -> dict:
    """Read json file.

    Args
    ----
    path: path to the json

    Returns
    -------
    loaded: loaded dict

    """
    with open(path, "r") as stream:
        loaded = json.load(stream)
    logging.info(f"{path} loaded")

    return loaded


def write_json(content: dict, path: str) -> None:
    """Write to json

    Args
    ----
    content: what to write
    path: where to write

    """
    logging.debug(f"writing json {path} ...")
    with open(path, "w") as stream:
        json.dump(content, stream, indent=4, sort_keys=False)


def atoi(text: str):
    return int(text) if text.isdigit() else text


def natural_keys(text: str) -> list:
    """
    copied from https://stackoverflow.com/questions/5967500/how-to-correctly-sort-a-string-with-a-number-inside
    alist.sort(key=natural_keys) sorts in human order
    http://nedbatchelder.com/blog/200712/human_sorting.html
    (See Toothy's implementation in the comments)


    Args
    ----
    text

    """
    logging.info(f"Sorting {text} ...")

    return [atoi(c) for c in re.split(r"(\d+)", text)]


def load_data_paths(path: str = "./data") -> list:
    """Load the data paths.

    Args
    ----
    path: directory path to the data.

    """
    paths = glob(os.path.join(path, "*.json"))

    # Sort the list naturally.
    paths.sort(key=natural_keys)

    logging.info(f"{paths} are sorted.")

    return paths


def load_model(model_name: str = "t5.1.1.lm100k.base") -> Tuple:
    """Load a huggingface model.

    Args
    ----
    model_name: This should be either "t5.1.1.lm100k.base" or
        "T0pp". The t0pp is a big model. You need at least 90GB CPU memory
        to load this model.

    Returns
    -------
    tokenizer: transformer tokenizer
    model: transformer model

    """
    assert model_name in ["t5.1.1.lm100k.base", "T0pp", "t0pp"]

    if model_name == "t5.1.1.lm100k.base":
        model_name = f"tscholak/{model_name}"
        from transformers import T5ForConditionalGeneration, T5Tokenizer

        tokenizer = T5Tokenizer.from_pretrained(model_name)
        model = T5ForConditionalGeneration.from_pretrained(model_name)

    else:
        model_name = f"bigscience/T0pp"

        from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

    logging.info(f"tokenizer and model for {model_name} are loaded!")

    return tokenizer, model


def load_data(path: str) -> dict:
    """Load all of the data.

    Args
    ----
    path: directory path to the data.

    Returns
    -------
    data_all: all data in a dictionary format. It looks like this.
        key: a path to the original data json file. It is one of './data/128_1.json',
            './data/128_2.json', './data/128_4.json', './data/128_8.json',
            './data/128_16.json', './data/128_32.json', './data/128_64.json'.
        value: dictionary with the following key : value pairs
            'val': validation data split
            'test': test data split
            'max_history': maximum history from the data generator.
            'capacity': capactiy PER memory system (e.g., If this value is 32, it means
                that episodic and semantic systems have 32 memory capacity,
                respectively.)
            'rewards': total rewards in one episode using the hand-crafted heuristics
            'accuracy': global accuracy in one episode using the hand-crafted heuristics

    """
    data_all = {}
    paths = load_data_paths(path)
    max_capacity = []
    for path in tqdm(paths):
        data = read_json(path)

        logging.info(f"{path}, {list(data.keys())}")
        data_all[path] = data

        maximum_history = os.path.basename(path).split("_")[0]
        memory_capacity = os.path.basename(path).split("_")[1].split(".json")[0]
        max_capacity.append(memory_capacity)

        logging.info(f"maximum_history: {maximum_history}")
        logging.info(f"memory_capacity per system: {memory_capacity}")

    logging.info(f"{paths} all loaded!")

    return data_all, max_capacity


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

class SemanticOnly(PromptTemplate):
    """Semantic only prompt.

    This prompt only uses semantic memories.

    """
    
    def __init__(self) -> None:
        logging.info("semantic only prompt is initialized!")
        
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
        
        for mem in sample["semantic_memory_system"]:
            prompt.append(f"{mem[-1]} {mem[0]} were found at {mem[2]}.")
            
        prompt.append(f"Where is {sample['question'][0]}?")

        prompt = " ".join(prompt)

        return prompt
    
class EpisodicToSemantic(PromptTemplate):
    """Episodic to semantic prompt.

    This prompt converts all episodic to semantic memories 
    and add semantic memories to the prompt based on the question.

    """
    cols = None
    lss = None
    
    def __init__(self) -> None:
        logging.info("episodic to semantic prompt is initialized!")
        self.cols = ["object", "location"]
        self.lss = []
        
    def generate_prompt(self, sample: dict) -> str:
        import pandas as pd
        
        sample["episodic_memory_system"] = sorted(
            sample["episodic_memory_system"], key=lambda x: x[-1]
        )
        
        for mem in sample["episodic_memory_system"]:
            self.lss.append(["".join(mem[0].split()[1:2]), "".join(mem[2].split()[1:2])])
        observations = pd.DataFrame(self.lss, columns = self.cols)
        
        obs = observations.groupby(observations.columns.tolist()).size().reset_index().rename(columns={0:'ranking'})
        obs_rank_sorted = obs.sort_values('ranking', ascending = False).reset_index(drop=True)
        
        for idx, mem in enumerate(sample["episodic_memory_system"]):
            max_len = len(sample["episodic_memory_system"])
            days = len(sample["episodic_memory_system"]) - idx - 1
            if days == 0:
                timestamp = "today"
            else:
                timestamp = f"{days} days ago"
            sample["episodic_memory_system"][idx][-1] = timestamp

        prompt = []
        
        episodic_object = obs_rank_sorted.loc[obs_rank_sorted['object'] == "".join(sample['question'][0].split()[1:2])].reset_index()

        for mem in sample["episodic_memory_system"]:
            prompt.append(f"{mem[0]} was at {mem[2]}, {mem[3]}.")

        if len(episodic_object) >= int(PromptWrapper.maxcap):
            for i in range(int(PromptWrapper.maxcap)):
                prompt.append(str(episodic_object["ranking"][i]) +" " +str(episodic_object["object"][i]) + " were found at "+str(episodic_object["location"][i])+".")
        else:
            for i in range(len(episodic_object)):
                prompt.append(str(episodic_object["ranking"][i]) +" " +str(episodic_object["object"][i]) + " were found at "+str(episodic_object["location"][i])+".")

        prompt.append(f"Where is {sample['question'][0]}?")
        
        prompt = " ".join(prompt)

        return prompt

class PromptWrapper:
    """A prompt wrapper class.

    This does everything, from loading data to running prompts. You just have to
    instantiate this class and run the `run()` method.

    E.g.,

    pw = PromptWrapper(**args)
    pw.run()

    """

    def __init__(
        self,
        data_type: str = "original",
        model_name: str = "t5.1.1.lm100k.base",
        prompt: str = "baseline",
    ) -> None:
        """Init

        Args
        ----
        data_type: "either 'original' our 'ours'"
        model_name: This should be either "t5.1.1.lm100k.base" or
            "T0pp". The t0pp is a big model. You need at least 90GB CPU
            memory to load this model.
        prompt: currently this can only be "baseline" but you should create your own
            prompts!

        """
        self.save_path_dir = f"./results/{data_type}/{model_name}_{prompt}"
        os.makedirs(self.save_path_dir, exist_ok=True)

        self.data_all, self.max_capacity = load_data(path=os.path.join("data", data_type))
        self.tokenizer, self.model = load_model(model_name)

        if prompt.lower() == "baseline":
            self.prompt = Baseline()
        elif prompt.lower() == "semantic_only":
            self.prompt = SemanticOnly()
        elif prompt.lower() == "episodic_to_semantic":
            self.prompt = EpisodicToSemantic()

        logging.info(
            "PromptWrapper is successfully instantiated with the arguments: "
            f"data_type: {data_type}, model_name: {model_name}, prompt: {prompt}! "
        )

    def run(self):
        logging.info("Running the model on all data. This might take some time ...")
        self.results = {}
        i = 0
        for data_path, data in tqdm(self.data_all.items()):
            save_path = os.path.join(self.save_path_dir, os.path.basename(data_path))
            self.results = {}
            PromptWrapper.maxcap = self.max_capacity[i]
            for split in tqdm(["val", "test"]):
                self.results[split] = []
                for sample in tqdm(data[split]):
                    prompt_text = self.prompt.generate_prompt(sample)
                    correct_answer = sample["correct_answer"]
                    input_ids = self.tokenizer(
                        prompt_text, return_tensors="pt"
                    ).input_ids
                    outputs = self.model.generate(input_ids)
                    prediction = self.tokenizer.decode(
                        outputs[0], skip_special_tokens=True
                    )

                    to_save = {
                        "prompt_text": prompt_text,
                        "correct_answer": correct_answer,
                        "prediction": prediction,
                    }
                    self.results[split].append(to_save)

            write_json(self.results, save_path)
            logging.info(f"results for {data_path} saved at {save_path}")
            i += 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="run memory experiments with prompts.")
    parser.add_argument(
        "--data_type",
        type=str,
        default="original",
        help="either 'original' our 'ours'",
    )
    parser.add_argument(
        "--model_name",
        type=str,
        default="t5.1.1.lm100k.base",
        help="Should be 't5.1.1.lm100k.base' or 't0pp'",
    )

    parser.add_argument(
        "--prompt", type=str, default="baseline", help="prompt template name."
    )

    args = vars(parser.parse_args())

    assert args["data_type"] in ["original", "ours"]

    logging.info(f"args: {args}")
    pw = PromptWrapper(**args)
    pw.run()
