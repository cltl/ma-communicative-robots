import argparse
import logging
import os
from glob import glob
import nltk
from rouge import Rouge

from run_prompts import read_json, write_json
from tqdm import tqdm
import numpy as np

logging.basicConfig(
    level=os.environ.get("LOGLEVEL", "INFO").upper(),
    format="%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


def evaluate_wrapper(results_path: str, metrics: list = ["rouge"]) -> None:
    """Evaluate wrapper.
    Args
    ----
    results_path: directory path where the json results files are located.
    metrics: a list of evaluation metrics. At the moment there is only one
        (e.g., "global_accuracy")
    """
    paths = glob(os.path.join(results_path, "*.json"))
    from run_prompts import natural_keys

    paths.sort(key=natural_keys)
    logging.info(f"Running evaluation on {paths} ...")
    save_path_dir = results_path.replace("results", "evaluation")
    os.makedirs(save_path_dir, exist_ok=True)

    for metric in tqdm(metrics):
        logging.info(f"Running {metric} metric on {paths} ...")
        evaluation = {}
        for path in tqdm(paths):

            item = os.path.basename(path).split(".json")[0]
            evaluation[item] = {}
            data = read_json(path)

            for split in ["val", "test"]:
                predictions = [sample["prediction"] for sample in data[split]]
                correct_answers = [sample["correct_answer"] for sample in data[split]]
                prompt = [sample["prompt_text"] for sample in data[split]]

                if metric.lower() == "global_accuracy":
                    global_accuracy = evaluate(
                        predictions, correct_answers, metric=metric.lower()
                    )
                    evaluation[item][split] = round(global_accuracy, 4)

                elif metric.lower() == "bleu":
                    bleu_score = evaluate(
                        predictions, correct_answers, metric=metric.lower()
                    )
                    evaluation[item][split] = bleu_score

                elif metric.lower() == "rouge":
                    rouge_score = evaluate(
                        predictions, correct_answers, metric=metric.lower()
                    )
                    evaluation[item][split] = rouge_score

                elif metric.lower() == "f1":
                    f1_score = evaluate(
                        predictions, correct_answers, metric=metric.lower()
                    )
                    evaluation[item][split] = f1_score

                elif metric.lower() == "nihed":
                    nihed_score = evaluate(
                        predictions, correct_answers, prompt, metric=metric.lower()
                    )
                    evaluation[item][split] = nihed_score

        val_mean = float(np.mean([item["val"] for item in evaluation.values()]))
        val_std = float(np.std([item["val"] for item in evaluation.values()]))
        test_mean = float(np.mean([item["test"] for item in evaluation.values()]))
        test_std = float(np.std([item["test"] for item in evaluation.values()]))

        evaluation["val_mean"] = round(val_mean, 4)
        evaluation["val_std"] = round(val_std, 4)
        evaluation["test_mean"] = round(test_mean, 4)
        evaluation["test_std"] = round(test_std, 4)

        write_json(evaluation, os.path.join(save_path_dir, f"{metric}.json"))


def evaluate(
    predictions: list, correct_answers: list, prompt_text: list, metric: str = "global_accuracy"
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

        #should this be commented
        return global_acc

    if metric.lower() == "bleu":
        # TODO: Nihed's job
        blue = nltk.translate.bleu_score.sentence_bleu(correct_answers, predictions)
        print(blue)
        # raise NotImplementedError
    if metric.lower() == "rouge":
        # TODO: Nihed's job
        for i,j in zip(predictions, correct_answers):
            # hypothesis = predictions
            # reference = correct_answers
            # breakpoint()
            rouge = Rouge()
            scores = rouge.get_scores(i, j)
            print(scores)
        # raise NotImplementedError
    if metric.lower() == "f1":
        # TODO: Nihed's job
        blue = nltk.translate.bleu_score.sentence_bleu(correct_answers, predictions)
        rouge = Rouge()
        rouge.get_scores(predictions, correct_answers, avg=True)
        F1 = 2 * (blue * rouge) / (blue + rouge)
        print(F1)
        # raise NotImplementedError
    if metric.lower() == "nihed":
        # TODO: Nihed's job\
        scores = []
        for answer, pred, prompt in zip(correct_answers, predictions, prompt_text):
            score = 0
            if answer in pred:
                score += 0.33
            if (prompt[-2] in pred) and (answer in pred):
                score += 0.33
            if (prompt[-2] in pred) and (prompt[-1] in pred) and (answer in pred):
                score += 0.33
            if "where" in pred:
                score -= 0.33
            if ("?" in pred) or ("not sure" in pred):
                score = 0
            else:
                score = 0
            scores.append(score)
            #I also have to calculate the average, right?
            print(scores)



        # raise ValueError


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate the experiment results.")
    parser.add_argument(
        "--results_path",
        type=str,
        help="directory path where the json results files are located.",
    )

    args = vars(parser.parse_args())

    assert "ours" in args["results_path"] or "original" in args["results_path"]

    logging.info(f"args: {args}")
    evaluate_wrapper(**args)
