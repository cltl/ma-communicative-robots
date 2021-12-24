## Overview

In this directory we provide the reinforcement learning (RL) and next sentence prediction (NSP) implementations of the Leolani replier alongside the base LenkaReplier.

The source code consists of the following files and folders:

| Files               | Description   |
| ------------------- |:--------------|
| main.py             | The main file to run an interaction with the chatbot. By default it runs the RL implementation, but can be changed to `NSP` or `Lenka` using the `--mode` command line argument (see Usage).|
| chatbots.py         | Implements a chatbot based on the Leolani triple extractor, brain, EMISSOR and the proposed repliers implemented in `repliers.py`. |
| repliers.py         | Defines the `RLReplier`, `NSPReplier` and baseline `LenkaReplier`. |
| EMISSOR.py          | Implements a wrapper class around [EMISSOR](https://github.com/leolani/EMISSOR) in order to integrate it into the Chatbot defined in `chatbots.py`. |
| generate_replies.py | Generates responses with the RL-, NSP- and Lenka-based repliers used for evaluation |
| requirements.txt    | Requirements file containing the minimum number of packages needed to run the implementation. |

| Folders                   | Description   |
| ------------------------- |:--------------|
| \reinforcement_learning   | Definitions and resource files of the UCB RL algorithm |
| \next_sentence_prediction | Definitions and resource files of the `pytorch` NSP model |
| \utils                    | utility functions used by `chatbots.py` and `repliers.py` |

## Usage

In order to run the code, install the required dependencies in `requirements.txt` (`pip install -r requirements.txt`) and run one of the following commands in the `RL_NSP` directory:

**Windows:**<br>

for RL:      `$ py -3 main.py --speaker=john --mode=RL --savefile=reinforcement_learning/thoughts.json `<br>
for NSP:    `$ py -3 main.py --speaker=john --mode=NSP --savefile=next_sentence_prediction/model `<br>
for Lenka: `$ py -3 main.py --speaker=john --mode=Lenka `

**Ubuntu:**<br>

for RL:      `$ python3 main.py --speaker=john --mode=RL --savefile=reinforcement_learning/thoughts.json `<br>
for NSP:    `$ python3 main.py --speaker=john --mode=NSP --savefile=next_sentence_prediction/model `<br>
for Lenka: `$ python3 main.py --speaker=john --mode=Lenka `

The code has been tested on both Windows 10 and Ubuntu 20.04.

**Important:** In order to run NSP, make sure to download the NSP model from <ADD DRIVE LINK> and unzip this file into `\next_sentence_prediction\model`. The model files can be found in the following [Google Drive link](https://drive.google.com/drive/folders/10GEpnjqXn4DfyKjFjJG7KbJEygvdAI2J?usp=sharing).
