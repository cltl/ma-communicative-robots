import time
from datetime import datetime
from random import choice
import pathlib
# general imports for EMISSOR and the BRAIN
from cltl import brain
from cltl.brain.utils.helper_functions import brain_response_to_json
from cltl.combot.backend.api.discrete import UtteranceType
from cltl.reply_generation.data.sentences import GREETING, ASK_NAME, ELOQUENCE, TALK_TO_ME
from cltl.triple_extraction.api import Chat, UtteranceHypothesis
from replier import SimReplier
import sys
import os

src_path = os.path.abspath(os.path.join('..'))
if src_path not in sys.path:
    sys.path.append(src_path)

#### The next utils are needed for the interaction and creating triples and capsules
import chatbots.util.driver_util as d_util
import chatbots.util.capsule_util as c_util
from random import getrandbits
import requests
from semantic_search import get_the_most_similar

##### Setting the location
place_id = getrandbits(8)
location = None
try:
    location = requests.get("https://ipinfo.io").json()
except:
    print("failed to get the IP location")

##### Setting the agents
AGENT = "Leolani2"
HUMAN_NAME = "Fina"
HUMAN_ID = "Fina"

### The name of your scenario
scenario_id = datetime.today().strftime("%Y-%m-%d-%H_%M_%S")

### Specify the path to an existing data folder where your scenario is created and saved as a subfolder
# Find the repository root dir
parent, dir_name = (d_util.__file__, "_")
while dir_name and dir_name != "src":
    parent, dir_name = os.path.split(parent)
root_dir = parent
scenario_path = os.path.abspath(os.path.join(root_dir, 'data'))

if not os.path.exists(scenario_path):
    os.mkdir(scenario_path)
    print("Created a data folder for storing the scenarios", scenario_path)

### Define the folders where the images and rdf triples are saved
imagefolder = scenario_path + "/" + scenario_id + "/" + "image"
rdffolder = scenario_path + "/" + scenario_id + "/" + "rdf"

### Create the scenario folder, the json files and a scenarioStorage and scenario in memory
scenarioStorage = d_util.create_scenario(scenario_path, scenario_id)
scenario_ctrl = scenarioStorage.create_scenario(scenario_id, int(time.time() * 1e3), None, AGENT)

log_path = pathlib.Path(rdffolder)
my_brain = brain.LongTermMemory(address="http://localhost:7200/repositories/Leolani",
                                log_dir=log_path,
                                clear_all=False)
replier = SimReplier()

chat = Chat(HUMAN_ID)

#### Initial prompt by the system from which we create a TextSignal and store it
initial_prompt = f"{choice(GREETING)} {HUMAN_NAME} {choice(TALK_TO_ME)}"
print(f'{AGENT} : {initial_prompt}')
textSignal = d_util.create_text_signal(scenario_ctrl, initial_prompt)
scenario_ctrl.append_signal(textSignal)

utterance = ""
context = ""

from sentence_transformers import SentenceTransformer

model = SentenceTransformer('multi-qa-mpnet-base-cos-v1')
model.save("sbert_models")

#### Get input and loop
while not (utterance.lower() == 'stop' or utterance.lower() == 'bye'):
    ###### Getting the next input signals
    utterance = input('\n')
    print(f'{HUMAN_NAME} : {utterance}')
    textSignal = d_util.create_text_signal(scenario_ctrl, utterance)
    scenario_ctrl.append_signal(textSignal)

    #### Process input and generate reply

    chat.add_utterance([UtteranceHypothesis(c_util.seq_to_text(textSignal.seq), 1.0)])
    chat.last_utterance.analyze()

    capsule = c_util.scenario_utterance_and_triple_to_capsule(scenario_ctrl,
                                                              place_id,
                                                              location,
                                                              textSignal,
                                                              HUMAN_ID,
                                                              chat.last_utterance.type,
                                                              chat.last_utterance.perspective,
                                                              chat.last_utterance.triple)

    if chat.last_utterance.triple is None:
        reply = choice(ELOQUENCE)
        print(AGENT + ": " + " " + reply)

    if chat.last_utterance.type == UtteranceType.STATEMENT:
        brain_response = my_brain.update(capsule, reason_types=True, create_label=True)
        brain_response = brain_response_to_json(brain_response)
        print(brain_response)
        cand_list = replier.get_candidates(brain_response)

        if context == '':
            context = utterance

        print(context)

        reply, explanation = get_the_most_similar(context, cand_list, model=model)

        print(explanation)

        context = context + " " + utterance + " " + reply + " "

        if len(context) < 300:
            context = context
        else:
            context = utterance
        print(context)
        print(AGENT + ": " + " " + reply)

    if chat.last_utterance.type == UtteranceType.QUESTION:
        capsule = c_util.lowcase_triple_json_for_query(capsule)
        brain_response = my_brain.query_brain(capsule)
        brain_response = brain_response_to_json(brain_response)
        reply = replier.reply_to_question(brain_response)

        print(AGENT + ": " + " " + reply)

    textSignal = d_util.create_text_signal(scenario_ctrl, reply)
    scenario_ctrl.append_signal(textSignal)

scenario_ctrl.scenario.ruler.end = int(time.time() * 1e3)
scenarioStorage.save_scenario(scenario_ctrl)