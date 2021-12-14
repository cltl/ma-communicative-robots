""" Filename:     generate_manual_evaluation_dataset.py
    Author(s):    Thomas Bellucci
    Description:  Generates a csv file with USR scores for the MCtx metric and empty columns for manual evaluation.
    Date created: Dec. 4th, 2021
"""

import json

import numpy as np
import pandas as pd
from tqdm import tqdm
from usr import USR


def main(context_file, replier_files, manual_criteria):
    """Takes the context and response files and generates a dataset with
    randomly selected responses which can be manually evaluated.

    params
    str context_file:     file with contexts
    list replier_files:   list of files with replies to contexts
    list manual_criteria: list of criteria which need to be evaluated manually.

    returns: None
    """
    # Read contexts
    with open(context_file, "r") as file:
        contexts = [line.strip().replace(",", "").split(" - ")[-1] for line in file]

    # Assign a random ID to response file
    ids = np.random.permutation(len(replier_files))
    replier_ids = {f: int(ids[i]) for i, f in enumerate(replier_files)}
    with open("results/replier_ids.json", "w") as file:
        json.dump(replier_ids, file, indent=4)

    # Read in each response file
    responses = {}
    for replier_file in replier_files:
        with open(replier_file, "r") as file:
            responses[replier_file] = [line.strip().replace(",", "") for line in file]

    print("Loading USR")
    usr = USR()

    # Generate csv for evaluation
    rows = []
    print("Generating USR scores")
    for i, context in tqdm(enumerate(contexts)):
        for replier_file in replier_files:
            id_ = replier_ids[replier_file]
            response = responses[replier_file][i]
            usr_score = usr.MCtx(context, response)
            rows.append([id_, context, response, usr_score])

    df = pd.DataFrame(rows, columns=["id", "context", "response", "MCtx"])
    df[manual_criteria] = None
    df.to_csv("results/evaluation_dataset.csv")


if __name__ == "__main__":
    context_file = "results/eval_contexts.txt"
    replier_files = [
        "results/eval_responses_Lenka.txt",
        "results/eval_responses_RL.txt",
        "results/eval_responses_NSP.txt",
        "results/eval_responses_Freq_low.txt",
        "results/eval_responses_Freq_mid.txt",
        "results/eval_responses_Freq_high.txt",
        "results/eval_responses_simbot1.txt",
        "results/eval_responses_simbot2.txt",
        "results/eval_responses_simbot3.txt",
    ]
    criteria = [
        "engaging",
        "specific",
        "relevant",
        "correct",
        "semantically appropriate",
        "diverse",
    ]

    main(context_file, replier_files, criteria)
