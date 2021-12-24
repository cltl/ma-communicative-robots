# Project Think Aloud

## Overview

This repository contains the code base of the *Think Aloud* project for the *Communicative Robots* Course at the Vrije Universiteit (VU), Amsterdam.

In this repository, we provide alternatives to the random thought selection mechanism used by Leolani V2, allowing the robot to decide which of her thoughts to verbalize in order to maximize dialogue coherence and optimally attain new knowledge about her environment. In brief, the methods proposed include:

| Method        | Description | By |
|---------------|-------------|----|
| Semantic Search with Sentence Similarity| In this approach verbalizations of thoughts are embedded into thought vectors using SentenceBERT (SBERT) which are then compared to the paragraph embedding of the dialogue history; responses with maximal cosine similarity to the paragraph embedding are then selected. | Fina |
| Prior Word Frequency                    | Entities and predicates mentioned in each thought are scored according to their frequency in some text corpus. Thoughts within some pre-defined frequency interval are then selected randomly. Three different strategies were examined based on low, medium and high frequency intervals | Imme |
| Reinforcement learning                  | Thought selection is learnt in an online manner through interaction with the user. To select a thought, a score in computed for each candidate based on the utility of the thought type and entities/predicates it mentions; the thought with the highest total utility is then selected. To reward the selection algorithm for its choices, we use an intrinsic reward function based on the number of learned facts as a result of selecting a thought. | Thomas |
| Next sentence prediction                | Thought selection is framed as a prediction problem in which responses by the replier are scored based on their likelihood of being valid responses to the user input. In this approach we repurpose a pretrained BERT-based SequenceClassifier and fine-tune it to judge the validity of responses. | Thomas |

The implementations, and instructions of how to run them, can be found in their respective folders.

## Prerequisites

1. An x86 machine running Windows 10 or a Unix-based OS
1. Python 3.7 or higher. Running in a virtual environment (e.g., conda, virtualenv, etc.) is highly recommended so that you don't mess up the system Python.
1. `pip install -r requirements.txt`

## Evaluation

Evaluation of the systems is performed in two steps; a manual evaluation based on various response criteria, such as *engagement*, *semantic appropriateness* and *relevance*, and an automatic evaluation using [USR](https://github.com/Shikib/usr). You can find a re-implementation of USR and the evaluation dataset in the `evaluation` folder.

## Authors

Supervisor: Piek Vossen

- Student 1: Thomas Bellucci
- Student 2: Imme Glaudé
- Student 3: Fina Yilmaz Polat
