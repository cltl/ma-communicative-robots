## Overview

In this folder you will find the code used for the evaluation of our systems. 

We performed two separate evaluations; a _human evaluation_ and an _automatic evaluation_ with USR (Mehri et al., 2020). 

## Dataset
In order to perform the evaluation, an evaluation dataset was constructed from previous interactions with Leolani. This dataset `eval_contexts.txt`, and the code used to generate it, can be found in the `data_generator` folder.

## Human Evaluation

For the human evaluation, responses of our systems to the instances in the dataset were evaluated using a questionnaire. The following files were used to create the form and visualize the results:

| Files                      | Description |
| -------------------------- |-------------|
| brain_responses.zip        | Zip file containing precomputed brain responses in JSON format. These brain responses were generated from the contexts in the evaluation dataset and used as input to the different repliers to generate responses (the results of which are stored in `results`). |
| generate_evaluation_csv.py | Generates a csv file with the responses of the repliers to each context in the dataset as rows. Evaluation metrics are marked as columns. It assigns a unique (but random) ID to the responses of each replier to hide the identity of the system that generated the response (to ensure a blind evaluation). |
| plot_human_evaluation.py   | Plots human evaluation scores for each metric and replier |

The results of the human evaluation are stored in the `results` folder.

## Automatic Evaluation with USR

To evaluate the responses of our repliers to the contexts in the dataset, we performed an automatic evaluation using USR (Mehri et al., 2020).

For this, we implemented USR using Huggingface's `transformers` which you can find in `USR.py`. In order to speed up evaluation, perform statistical tests and visualize the scores provided by USR, we ran our evaluation in Google Colaboratory (using their GPU option to speed up evaluation). 
The notebook can be found here: [Link](https://colab.research.google.com/drive/1QDXn4QB574fPuk4gD4EoQXRXDRkXA_QM?usp=sharing)
