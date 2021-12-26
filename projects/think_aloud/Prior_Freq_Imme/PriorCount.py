import random

import numpy as np
from wordfreq import word_frequency


def PriorCount(thoughts, frequency_group):
    scores = []
    for thought in thoughts:
        score = []
        if thought.split()[0] not in ["subject_gap", "object_gap"]:
            scores.append((thought, random.uniform(0, 1)))
        else:
            for complement in thoughts[thought][1]["_complement"]:
                word = complement["_predicate"]["_label"]
                word_freq = word_frequency(
                    word, lang="en", wordlist="large", minimum=0.0
                )
                score.append(word_freq)
                score = np.mean(score)
                scores.append((thought, score))
    _, values = zip(*scores)
    thres = np.percentile(np.array(values), 33)
    low = []
    medium = []
    high = []
    for thought, score in scores:
        if score <= thres:
            low.append(thought)
        if score > thres and score < 2 * thres:
            medium.append(thought)
        else:
            high.append(thought)
    if frequency_group == "low":
        return random.choice(low)
    if frequency_group == "medium":
        return random.choice(low)
    else:
        return random.choice(high)
