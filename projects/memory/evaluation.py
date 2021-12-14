import logging
import os
import argparse
from run_prompts import read_json, write_json

logging.basicConfig(
    level=os.environ.get("LOGLEVEL", "INFO").upper(),
    format="%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


def evaluate_wrapper(results: dict):
    for data_path, data in results.items():
        for split in ["val", "test"]:
            predictions = [sample["prediction"] for sample in data[split]]
            correct_answers = [sample["correct_answer"] for sample in data[split]]

            global_accuracy = evaluate(
                predictions, correct_answers, metric="global_accuracy"
            )


def evaluate(predictions, correct_answers, metric="global_accuracy") -> None:
    if metric.lower() == "global_accuracy":

        T = 0
        F = 0

        for answer, pred in zip(correct_answers, predictions):
            if answer in pred:
                T += 1
            else:
                F += 1

        logging.info(f"T: {T}, F: {F}")
        logging.info(f"global accuracy is {T / (T + F)}")

    elif metric.lower() == "bleu":
        raise NotImplementedError
    elif metric.lower() == "rouge":
        raise NotImplementedError
    elif metric.lower() == "f1":
        raise NotImplementedError


def main(results: dict) -> None:
    """This will write in place."""

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate the experiment results.")
    parser.add_argument("--results_path", type=str, help="json path.")
    args = parser.parse_args()
    
    results = read_json(args.results_path)

    main(results)