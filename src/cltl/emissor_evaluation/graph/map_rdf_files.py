import json
from pathlib import Path
import re
import os
import numpy as np


def load_scenario(scenario_folder, rdf_folder):
    # Read rdf files, ordered temporaly
    files = sorted([path for path in rdf_folder.glob('*.trig')])

    # Read from EMISSOR
    text_json = os.path.join(scenario_folder, 'text.json')
    if not os.path.exists(text_json):
        return [], files

    with open(text_json, 'r') as j:
        data = json.loads(j.read())

    return data, files


def get_speaker(data, files):
    # Read only trig files
    if not data:
        for f in files:
            txt = Path(f).read_text()
            matches = re.search(r"leolaniFriends:(.*) a", txt)
            if matches:
                # Found it!
                return matches.group(1)

    # Read from EMISSOR
    speaker = 'SPEAKER'
    for item in data:
        for m in item['mentions']:
            for ann in m['annotations']:
                if ann['type'] == 'VectorIdentity':
                    # Establish speaker identity
                    speaker = ann['value']

    return speaker


def process_mentions(ann, utt_id, rdf_file, speaker=None, files=None):
    # Process utterances
    if ann["type"] == "ConversationalAgent":
        rdf_file, files = search_id_in_log(utt_id, rdf_file, files)
        return rdf_file, speaker
    else:
        return rdf_file, speaker


def search_id_in_log(utt_id, rdf_file, files):
    files_to_remove = []

    for f in files:
        txt = Path(f).read_text()
        if utt_id in txt:
            # Found it!
            rdf_file.append(f.stem + '.trig')
            files.remove(f)
            break

    for f in files_to_remove:
        files.remove(f)

    return rdf_file, files


def map_only_trig(files, speaker):
    utterances = []
    files_to_remove = []

    for rdf_file in files:
        txt = Path(rdf_file).read_text()
        matches = re.findall(r"utterance(.*) a grasp:Utterance", txt)
        if matches:
            # Get the highest id
            matches = [int(x) for x in matches]
            utt_idx = np.argmax(matches)
            utt_id = matches[utt_idx]

            # Find utterance text
            matches = re.findall(
                fr'rdf:value "(.*)"\^\^xml1:string ;(\s+)prov:wasDerivedFrom leolaniTalk:chat(.*)_utterance{utt_id} .',
                txt)
            utterance_text = matches[0][0]

            files_to_remove.append(rdf_file)

            # Add utterance, with rdf file pointers if available
            utterance = {"Turn": utt_id, "Turn nr": utt_id, "Speaker": speaker,
                         "Response": utterance_text, "rdf_file": [rdf_file.stem + '.trig']}
            utterances.append(utterance)

    for f in files_to_remove:
        files.remove(f)

    return utterances, files


def map_emissor(data, files, speaker):
    # Loop through utterances, to map ids to those present in the rdf files
    utterances = []
    for index, item in enumerate(data):
        utt_id = item['id']
        rdf_file = []

        # Loop through mentions to find an utterance id
        for m in item['mentions']:
            for ann in m['annotations']:
                rdf_file, utterance_speaker = process_mentions(ann, utt_id, rdf_file, speaker=speaker, files=files)

        # Add utterance, with rdf file pointers if available
        utterance = {"Turn": utt_id, "Turn nr": index, "Speaker": utterance_speaker,
                     "Response": item['text'], "rdf_file": rdf_file}
        utterances.append(utterance)

    return utterances, files


def map_scenarios(scenario_folder, rdf_folder):
    data, files = load_scenario(scenario_folder, rdf_folder)
    speaker = get_speaker(data, files)

    # Read only trig files
    if not data:
        utterances, files = map_only_trig(files, speaker)

    # Read from EMISSOR
    else:
        utterances, files = map_emissor(data, files, speaker)

    # Check if there is a generic rdf file left to map, probably the ontology upload
    if len(files) == 1:
        utterances[0]["rdf_file"].append(files[0].stem + '.trig')
        files.remove(files[0])

    turn_to_trig_file = os.path.join(scenario_folder, 'turn_to_trig_file.json')
    with open(turn_to_trig_file, 'w') as f:
        js = json.dumps(utterances)
        f.write(js)
