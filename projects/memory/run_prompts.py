import json
from glob import glob
from tqdm import tqdm
import os
import random
import re
import logging
import argparse
from typing import Tuple, List

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
    """Write json"""
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

    """
    logging.info(f"Sorting {text} ...")

    return [atoi(c) for c in re.split(r"(\d+)", text)]


def load_data_paths(path: str = "./data") -> list:
    paths = glob(os.path.join(path, "*.json"))
    paths.sort(key=natural_keys)

    logging.info(f"{paths} are sorted.")

    return paths


def load_model(model_name: str = "tscholak/t5.1.1.lm100k.base") -> Tuple:
    assert model_name in ["tscholak/t5.1.1.lm100k.base", "bigscience/T0pp"]

    if model_name == "tscholak/t5.1.1.lm100k.base":
        from transformers import T5Tokenizer, T5ForConditionalGeneration

        tokenizer = T5Tokenizer.from_pretrained(model_name)
        model = T5ForConditionalGeneration.from_pretrained(model_name)

    else:
        from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

    logging.info(f"tokenizer and model for {model_name} are loaded!")

    return tokenizer, model


def load_data(path: str = "./data") -> dict:
    data_all = {}
    paths = load_data_paths(path)
    for path in tqdm(paths):
        data = read_json(path)

        logging.info(f"{path}, {list(data.keys())}")
        data_all[path] = data

        maximum_history = os.path.basename(path).split("_")[0]
        memory_capacity = os.path.basename(path).split("_")[1].split(".json")[0]

        logging.info(f"maximum_history: {maximum_history}")
        logging.info(f"memory_capacity per system: {memory_capacity}")

    logging.info(f"{paths} all loaded!")

    return data_all


class Baseline:
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


class PromptWrapper:
    def __init__(
        self,
        data_path="./data",
        model_name="tscholak/t5.1.1.lm100k.base",
        prompt="baseline",
        save_path="./results",
    ) -> None:
        os.makedirs(save_path, exist_ok=True)
        self.save_path = os.path.join(save_path, f"{model_name}_{prompt}.json")

        self.data_all = load_data(path=data_path)
        self.tokenizer, self.model = load_model(model_name)

        if prompt.lower() == "baseline":
            self.prompt = Baseline()

    def run(self):
        logging.info("Running the model on all data. This might take some time ...")
        self.results = {}
        for data_path, data in tqdm(self.data_all.items()):
            self.results[data_path] = {}
            for split in tqdm(["val", "test"]):
                self.results[data_path][split] = []
                for sample in data[split]:
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
                    self.results[data_path][split].append(to_save)

        write_json(self.results, self.save_path)
        logging.info(f"results saved at {self.save_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="run memory experiments with prompts.")
    parser.add_argument(
        "--data_path", type=str, default="./data", help="path to data directory."
    )
    parser.add_argument(
        "--model_name",
        type=str,
        default="tscholak/t5.1.1.lm100k.base",
        help="transformer string name",
    )
    parser.add_argument(
        "--save_path", type=str, default="./results", help="where to save data."
    )

    args = vars(parser.parse_args())
    pw = PromptWrapper(**args)
    pw.run()
