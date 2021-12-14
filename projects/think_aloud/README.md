# Project Think Aloud

## Overview
This repository contains the code base of the _Think Aloud_ project for the _Communicative Robots_ Course at the Vrije Universiteit (VU).

In this repository, we provide alternatives to the random _thought_ selection mechanism implemented by Leolani V2, allowing the robot to learn which of her thoughts to verbalize in order to maximize dialogue coherence and optimally attain new knowledge about her environment. To choose between thoughts, several methods are proposed;

| Method        | Description | By |
|---------------|-------------|----|
| Paragraph similarity | In this approach possible verbalizations of thoughts are embedded into a thought vector which is compared to the paragraph embedding of the dialogue history (context); responses with maximal similarity to the paragraph embedding are then selected. Three different paragraph embedding models have been implemented based on ```...```, ```...``` and ```...```.| Fina |
| Corpus statistics    | Entities and predicates mentioned in each thought are scored according to their frequency in some text corpus. Thoughts within a frequency intervals are then selected randomly. Three different strategies were examined based on low (smaller than ? percentile), medium (between ? and ? percentile) and high frequency (exceeding ? percentile) | Imme |
| Reinforcement learning | In this approach thought selection is learnt in an online manner through interaction using an intrinsic reward function based on the number of learned facts as a result of selecting a thought. To select a thought, a score in computed for each thought based on the utility of entities/predicates it mentions; the thought with the highest utility is then selected. | Thomas |
| Next sentence prediction | Thought selection is framed as a prediction problem in which responses by the replier are scored based on the likelihood of them being good continuations of the dialogue. | Thomas |

The implementations can be found in their respective folders.

## Prerequisites

1. An x86 machine running Windows 10 or a Unix-based OS
2. Python 3.7 or higher. Running in a virtual environment (e.g., conda, virtualenv, etc.) is highly recommended so that you don't mess up with the system Python.
3. ```pip install -r requirements.txt```

## Evaluation

Evaluation of the proposed methods is performed in two steps; a manual evaluation based on response criteria, such as *engagement*, *semantic appropriateness* and *relevance*, and an automatic evaluation using [USR](https://github.com/Shikib/usr). You can find a re-implementation of USR and the evaluation dataset in ```/evaluation```.

## Authors
Piek Vossen
* Student 1: Thomas Bellucci
* Student 2: Imme Glaudé
* Student 3: Fina Yilmaz Polat
