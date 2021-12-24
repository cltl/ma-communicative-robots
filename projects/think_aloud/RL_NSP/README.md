## Overview

In this directory we provide the *reinforcement learning* (RL) and *next sentence prediction* (NSP) implementations of the Leolani replier (Thomas' project).

The code base consists of the following files:

| Files               | Description   |
| ------------------- |:--------------|
| main.py             | Runs an interaction with the chatbot. By default it runs the RL implementation, but can be changed to `NSP` or `Lenka` using the `--mode` command line argument (see Usage section).|
| chatbots.py         | Implements a chatbot based on the Leolani triple extractor, brain, EMISSOR and the proposed repliers implemented in `repliers.py`. |
| repliers.py         | Defines the `RLReplier`, `NSPReplier` and baseline `LenkaReplier`. |
| EMISSOR.py          | Implements a wrapper class around [EMISSOR](https://github.com/leolani/EMISSOR) in order to integrate it into the Chatbot defined in `chatbots.py`. |
| generate_replies.py | Generates responses with the RL-, NSP- and Lenka-based repliers used for evaluation (requires `brain_responses.zip`) |
| requirements.txt    | Requirements file containing the minimum number of packages needed to run the implementation. |

<p> The implementations of the RL and NSP method are divided into separate folders:</p>


| Folders                   | Description     |
| ------------------------- | :-------------- |
| \reinforcement_learning   | Resource files and implementation of the UCB RL algorithm |
| \next_sentence_prediction | Resource files and implementation of the Pytorch NSP model |
| \utils                    | Utility functions used by `chatbots.py` and `repliers.py` (e.g. for brain response formatting and thought extraction) |

## Usage

In order to run the code, install the required dependencies in `requirements.txt` using `pip install -r requirements.txt`; then run one of the following commands in the `RL_NSP` directory:

**Windows:**<br>

RL:      `$ py -3 main.py --speaker=john --mode=RL --savefile=reinforcement_learning/thoughts.json `<br>
NSP:    `$ py -3 main.py --speaker=john --mode=NSP --savefile=next_sentence_prediction/model `<br>
Lenka: `$ py -3 main.py --speaker=john --mode=Lenka `

**Ubuntu:**<br>

RL:      `$ python3 main.py --speaker=john --mode=RL --savefile=reinforcement_learning/thoughts.json `<br>
NSP:    `$ python3 main.py --speaker=john --mode=NSP --savefile=next_sentence_prediction/model `<br>
Lenka: `$ python3 main.py --speaker=john --mode=Lenka `

The code has been tested on both Windows 10 and Ubuntu 20.04.

**Important:** In order to run NSP, make sure to download the NSP model and place the resource files into a directory `\next_sentence_prediction\model`. The model files can be found in the following [Google Drive folder](https://drive.google.com/drive/folders/10GEpnjqXn4DfyKjFjJG7KbJEygvdAI2J?usp=sharing).
