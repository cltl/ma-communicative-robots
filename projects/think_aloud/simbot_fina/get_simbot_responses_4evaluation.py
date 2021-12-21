import glob
import json
import os
import re
from random import choice

from cltl.brain.utils.helper_functions import brain_response_to_json
from cltl.reply_generation.data.sentences import ELOQUENCE
from replier import SimReplier
from semantic_search import get_the_most_similar
from sentence_transformers import SentenceTransformer

#### Evaluation Script for Simbots. Written by Fina Polat ####


def get_num(x):
    num = re.findall("\d+", x)[0]
    return float(num)


replier = SimReplier()

utterance = ""
context = ""
reply = ""

# Change language model accordingly for different versions of Simbot.
model = SentenceTransformer(r"multi-qa-mpnet-base-cos-v1")
model.save(r"sbert_models\multi-qa-mpnet-base-cos-v1")
print("Language model loaded.")

# Change output file name accordingly for different versions of Simbot output.
eval_folder_path = r"evaluation_dataset\brain_responses"
context_file = r"evaluation_dataset\eval_contexts.txt"

with open(context_file, "r") as cf:
    lines = cf.readlines()

for filepath, line in zip(
    sorted(
        glob.glob(os.path.join(eval_folder_path, "br_*.json")), key=lambda x: get_num(x)
    ),
    lines,
):
    # print(filepath)
    with open(filepath) as f:
        brain_response = json.load(f)
        brain_response = brain_response_to_json(brain_response)
        print(brain_response)
        brain_keys = list(brain_response.keys())
        print(brain_keys)
        input_type = str(brain_keys[1])
        print(input_type)
        line = line.split("-")
        context = line[0] + line[1] + line[2]
        print(f"CTXT: {context}")
        if input_type == "statement":

            # print(brain_response['statement'])
            cand_list = replier.get_candidates(brain_response)

            print(f"cand_list: {cand_list}")
            print("Context: " + context)
            reply, explanation = get_the_most_similar(context, cand_list, model=model)

            print(f"Explanation: {explanation}")
            print(f"Leolani2: {reply}")

        elif input_type == "question":

            reply = replier.reply_to_question(brain_response)

            print(f"Leolani2: {reply}")

        else:
            reply = choice(ELOQUENCE)

        print("---------------------------------------------")

    with open("simbot1_responses.txt", "a") as of:
        of.write(reply)
        of.write("\n")
