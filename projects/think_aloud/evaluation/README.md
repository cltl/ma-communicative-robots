## Overview

In this folder you will find the code used for the evaluation of the systems. 

We performed two separate evaluations; a human evaluation and an automatic evaluation with USR (Mehri et al., 2020). 

## Dataset
In order to perform the evaluation, an evaluation dataset was constructed from previous interactions with Leolani. This dataset, and the code used to generate it, can be found in the `data_generator` folder.

## Human Evaluation

For the human evaluation, the following files were used:

| Files                      | Description |
| -------------------------- |-------------|
| brain_responses.zip        | Zip file containing precomputed brain responses in JSON format. These brain responses were generated from the contexts in the evaluation dataset and are used as input to the repliers. |
| generate_evaluation_csv.py | Generates a csv file with empty columns for a variety of evaluation metrics (used for the human evaluation). It also pre-computes USR scores for the _Maintains Context_ (MCtx/DR) metric. |
| plot_human_evaluation.py  | Creates bar plots with human evaluation scores for each metric and replier |

## Automatic Evaluation with USR

To evaluate the responses of our repliers (stored in `eval_responses_*.txt`) to the contexts in `eval_contexts.txt`, we performed an automatic evaluation using USR proposed by Mehri et al. (2020).

For this, we re-implemented USR using Huggingface's `transformers` which you can find in `USR.py`. In order to speed up evaluation, perform statistical tests and visualize the scores provided by USR, we ran our evaluation in Google Colaboratory (using their GPU option to speed up evaluation). 
The notebook can be found here: [Link](https://colab.research.google.com/drive/1QDXn4QB574fPuk4gD4EoQXRXDRkXA_QM?usp=sharing)

The results of both evaluations are stored in the `results` folder.
