## Overview

In this directory we have provided the reinforcement learning (RL) and next sentence prediction (NSP) implementations of the replier alongside the baseline LenkaReplier.

The code base consists of the following files:

| Files            | Description   |
| ---------------- |:-------------|
| main.py          | The main file to run an interaction with the chatbot. By default it runs the RL implementation, but can be changed to `NSP` or `Lenka` using the `--mode` command line argument.|
| chatbots.py      | Implements a chatbot around the RL-, NSP- or LenkaReplier based on the Leolani triple extraction, brain and the proposed RL/NSPRepliers. |
| repliers.py      | Defines the RLReplier, NSPReplier and baseline LenkaReplier. |
| EMISSOR.py       | Implements a wrapper around EMISSOR in order to integrate it into the Chatbot defined in `chatbots.py`. |
| requirements.txt | Reduced requirements file, containing the minimum packages needed to run the implementation. |

Furthermore, method specific resources are stored in `\reinforcement_learning` and `\next_sentence_prediction`, which include definitions and resource files of the UCB RL algorithm and NSP model, respectively. `\utils` primarily contains utility functions used by `chatbots.py`/`repliers.py`.

## Usage

In order to run the code, install the required dependencies in `requirements.txt` (`pip install -r requirements.txt`) and run one of the following commands in the `RL_NSP` directory:

**Windows:**<br>

for RL:      `$ py -3 main.py --speaker-john --mode=RL --savefile=reinforcement_learning/thoughts.json `<br>
for NSP:    `$ py -3 main.py --speaker-john --mode=NSP --savefile=next_sentence_prediction/model `<br>
for Lenka: `$ py -3 main.py --speaker-john --mode=Lenka `

**Ubuntu:**<br>

for RL:      `$ python3 main.py --speaker-john --mode=RL --savefile=reinforcement_learning/thoughts.json `<br>
for NSP:    `$ python3 main.py --speaker-john --mode=NSP --savefile=next_sentence_prediction/model `<br>
for Lenka: `$ python3 main.py --speaker-john --mode=Lenka `

The code has been tested on both Windows 10 and Ubuntu 20.04.

**Important:** In order to run NSP, make sure to download the NSP model from <ADD DRIVE LINK> and unzip this file into `\next_sentence_prediction`.
