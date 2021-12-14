""" Filename:     collect_brain_responses.py
    Author(s):    Thomas Bellucci
    Description:  This file contains the code used to collect brain responses from example contexts.
    Date created: Dec. 4th, 2021
"""

import json
import sys

sys.path.append("../../")

import argparse
import os

from chatbots import Chatbot
from tqdm import tqdm


def collect_brain_responses(args):
    """Collects brain responses used for the evaluation."""
    # Load in evaluation dataset
    with open(args.eval_data, "r") as file:
        contexts = [line.strip() for line in file]

    # Write responses and scores to file for manual evaluation!
    brain_response_file = (
        os.path.dirname(os.path.abspath(args.eval_data)) + "/brain_responses/br_{}.json"
    )

    # Sets up chatbot with the basic LenkaReplier and a new speaker
    chatbot = Chatbot("darrell", "Lenka", None)

    # Get brain response for each context in eval_data file
    error_lines = []
    for i, context in tqdm(enumerate(contexts)):

        brain_response = None
        try:  # Respond() can break when TypeReasoner yields pizza emoji
            last_utt = context.split(" - ")[-1]
            _, brain_response = chatbot.respond(last_utt, return_br=True)
        except:
            print("ERROR at line %s" % i)
            error_lines.append(i + 1)
            chatbot = Chatbot("darrell", "Lenka", None)  # To replace broken brain

        # Write brain_response out to file
        if brain_response is not None:
            with open(brain_response_file.format(i), "w") as file:
                json.dump(brain_response, file, indent=4)

    print("ERRORS at", error_lines)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--eval_data",
        default="eval_contexts.txt",
        type=str,
        help="Path to dataset containing the contexts ro respond to.",
    )
    args = parser.parse_args()
    print("\nCollecting brain responses from {}".format(args.eval_data))

    collect_brain_responses(args)
