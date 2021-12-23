from os import listdir
import os
import json
from thought_replier import PriorFreqReplier
from cltl.brain.long_term_memory import LongTermMemory
from pathlib import Path

mypath = 'evaluation_dataset/brain_responses'
speaker = 'Imme'
savefile = 'save_file.json'
files = listdir(mypath)
files.sort(key= lambda x: float(x.strip('br_.json')))
results = []
brain = LongTermMemory(address = "http://localhost:7200/repositories/sandbox",
                                      log_dir = Path("logs"),
                                      clear_all = False)
replier = PriorFreqReplier(brain,savefile)
frequencies = ['low', 'medium', 'high']

for frequency_group in frequencies:
    for file in files:
        brain_response = open(os.path.join(mypath, file),'r')
        brain_response = json.load(brain_response)
        capsule = brain_response[list(brain_response)[1]]
        if capsule['utterance_type'] == 'question':
            reply = replier.reply_to_question(brain_response, frequency_group)
        elif capsule['utterance_type'] == 'statement':
            reply = replier.reply_to_statement(brain_response, frequency_group)
        with open('results_PriorFreq/{}_freq.txt'.format(frequency_group), 'a+') as f:
            f.write(reply+"\n")
        results.append(reply)