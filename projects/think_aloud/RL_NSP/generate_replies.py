""" Filename:     generate_replies.py
    Author(s):    Thomas Bellucci
    Description:  This file is used to generate responses of each replier 
                  given a path to a folder of brain responses.
    Date created: Dec. 4th, 2021
"""

import argparse
import glob
import json
import re

from repliers import LenkaReplier, NSPReplier, RLReplier
from tqdm import tqdm


def atoi(string):
    """Returns integer id of replier"""
    id_ = re.findall("\d+", string)[0]
    return int(id_)


def reply_to_brain_responses(args):
    """Collects brain responses used for the evaluation."""
    # Set up replier (no need for brain)
    if args.mode == "RL":
        replier = RLReplier(None, args.savefile)
    elif args.mode == "NSP":
        replier = NSPReplier(None, args.savefile)
    elif args.mode == "Lenka":
        replier = LenkaReplier(None, None)
    else:
        raise Exception("%s not implemented (select RL, NSP or Lenka)" % args.mode)

    # Get sorted list of brain responses
    br_files = sorted(glob.glob(args.br_dir + "/br_*.json"), key=lambda x: atoi(x))

    # Reply to each brain response with replier
    replies = []
    for br_file in tqdm(br_files):

        brain_response = None
        with open(br_file, "r") as file:
            brain_response = json.load(file)

        reply = "none"
        if brain_response is not None:
            if "question" in brain_response.keys():
                reply = replier.reply_to_question(brain_response)
            else:
                reply = replier.reply_to_statement(brain_response)
        replies.append(reply)

    # Write replies to disk
    with open("eval_responses_{}.txt".format(args.mode), "w") as file:
        file.write("\n".join(replies))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--br_dir",
        default="brain_responses",
        type=str,
        help="Folder containing brain_responses to respond to.",
    )
    parser.add_argument(
        "--mode",
        default="NSP",
        type=str,
        choices=["RL", "NSP", "Lenka"],
        help="Thought selection method: {'RL', 'NSP', 'Lenka'}",
    )
    parser.add_argument(
        "--savefile",
        default="../next_sentence_prediction/model",
        type=str,
        help="Path to BERT for NSP (--method=NSP) or RL JSON (--method=RL)",
    )
    args = parser.parse_args()
    print(
        "\nEvaluating brain responses from {} with mode={} and {}".format(
            args.br_dir, args.mode, args.savefile
        )
    )

    reply_to_brain_responses(args)
