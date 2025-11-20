import glob
import json
from collections import Counter
from datetime import datetime
import os
import argparse
import sys
from emissor.persistence import ScenarioStorage
from emissor.representation.scenario import Modality
from emissor.representation.scenario import Signal
import text_signal as text_util
import image_signal as image_util
import scenario_check as check


def get_statistics_from_signals(signals):
    type_counts = {}
    type_dict_text, nr_annotations = get_annotation_dict(signals)

    for annoType in type_dict_text.keys():
        timedValues = type_dict_text.get(annoType)
        valueList = []
        for value in timedValues:
            valueList.append(get_get_value_from_annotation(annoType, value[1]))
        type_counts[annoType]=Counter(valueList)

    return type_counts, type_dict_text, nr_annotations

def get_date_duration_in_minutes(scenario_ctrl):
    start = 0
    end = 0
    duration = 0
    date = None
    try:
        start = int(scenario_ctrl.scenario.start)
        end = int(scenario_ctrl.scenario.end)
        date = datetime.fromtimestamp(start/1000).strftime('%Y-%m-%d')
    except:
        print('Error getting duration')
        print('start', scenario_ctrl.scenario.start)
        print('end', scenario_ctrl.scenario.end)
    if start>0 and end>0:
        duration = (end - start) / 60000
    return date, duration

def get_utterance_stats(utterances):
    total_utt_length = 0
    total_token_length = 0
    total_tokens = 0
    for utt in utterances:
        tokens = utt[1].split(" ")
        total_utt_length += len(utt[1])
        total_tokens += len(tokens)
        for token in tokens:
            total_token_length += len(token)

    average_token_length = total_token_length/ total_tokens
    average_tokens_per_utt = total_tokens/len(utterances)
    average_utt_length = total_utt_length/len(utterances)
    return average_utt_length, average_tokens_per_utt, average_token_length


def get_meta_data (scenario_ctrl):
    speaker = "No speaker"
    agent = "No agent"
    location = "No location"
    people = "Not in context"
    objects = "Not in context"

    try:
        speaker = scenario_ctrl.scenario.context.speaker["name"] if "name" in scenario_ctrl.scenario.context.speaker else "No speaker"
    except:
        print("No speaker in context")
    try:
        agent = scenario_ctrl.scenario.context.agent["name"] if "name" in scenario_ctrl.scenario.context.agent else "No agent"
    except:
        print("No speaker in context")
    try:
        location = scenario_ctrl.scenario.context.location_id  #### Change this to location name when this implemented
    except:
        print("No location id in context")

    try:
        people = scenario_ctrl.scenario.context.persons
    except:
        print("No location id in context")
    try:
        objects = scenario_ctrl.scenario.context.objects
    except:
        print("No location id in context")

    return speaker, agent, location, people, objects


def analyse_interaction_json(emissor_folder, scenario_id):
    scenario_folder = os.path.join(emissor_folder, scenario_id)
    # Save
    evaluation_folder = os.path.join(scenario_folder, 'evaluation')
    if not os.path.exists(evaluation_folder):
        os.mkdir(evaluation_folder)
    meta = {}
    ### Create the scenario folder, the json files and a scenarioStorage and scenario in memory
    scenario_storage = ScenarioStorage(emissor_folder)
    scenario_ctrl = scenario_storage.load_scenario(scenario_id)
    t = {}
    #t['SCENARIO_FOLDER'] = scenario_folder
    t['Scenario_id']= scenario_id
    speaker, agent, location, people, objects = get_meta_data(scenario_ctrl)
    t['Agent']=agent
    t['Speaker']=speaker
    t['Location']=location
    t['People_seen '] = str(people)
    t['Objects_seen']= str(objects)
    date, duration = get_date_duration_in_minutes(scenario_ctrl)
    t['Date']=str(date)
    t['Duration_in_minutes'] = str(duration)
    meta["Scenario"]=t

    #### Text signals statistics
    text_signals=[]
    try:
        text_signals = scenario_ctrl.get_signals(Modality.TEXT)
    except:
        print('Error loading text signals from text.json')
    ids, utterances, speakers = text_util.get_utterances_with_context_from_signals(text_signals)
    t = {}
    t['Nr. of signals'] = str(len(utterances))
    average_utt_length, average_tokens_per_utt, average_token_length = get_utterance_stats(utterances)
    t['Average_utterance_length'] = str(average_utt_length)
    t['Average_tokens_per_utterance'] = str(average_tokens_per_utt)
    t['Average_token_length'] = str(average_token_length)

    text_type_counts, text_type_timelines, nr_annotations = get_statistics_from_signals(text_signals)

    t['Nr. of annotations']=  str(nr_annotations)
    items = {}
    for key in text_type_counts.keys():
        counts = text_type_counts.get(key)
        for c in counts:
            items[c]=str(counts.get(c))

    t['Text_annotations']=items
    meta["Text"]=t

    t={}
    image_signals =[]
    try:
        image_signals = scenario_ctrl.get_signals(Modality.IMAGE)
    except:
        print('Error loading image signals from image.json')
    t["Nr. of images"]=str (len(image_signals))
    text_type_counts, text_type_timelines, nr_annotations = get_statistics_from_signals(image_signals)
    t[ 'Nr. of annotations']=  str(nr_annotations)
    items = {}
    for key in text_type_counts.keys():
        counts = text_type_counts.get(key)
        for c in counts:
            items[c] = str(counts.get(c))
    t['Image_annotations'] = items
    meta["Image"]=t

    if not os.path.exists(evaluation_folder):
        os.mkdir(evaluation_folder)
    file_name = scenario_id + "_meta_data.json"
    file_path = os.path.join(evaluation_folder, file_name)
    print('Saving the meta data in', file_path)
    with open(file_path, 'w') as f:
        json_object = json.dumps(meta, indent=4)
        f.write(json_object)


def get_annotation_dict (signals:[Signal]):
        all_annotations = []
        type_dict = {}
        for signal in signals:
            mentions = signal.mentions
            timestamp = signal.time.start
            for mention in mentions:
                annotations = mention.annotations
                all_annotations.append((timestamp, annotations))
        for pair in all_annotations:
            time_key = pair[0]
            anno = pair[1]
            if anno:
                type_key = anno[0].type
                value = anno[0].value
                if not type_key=='Face' and not type_key==None:
                    #### create a dict with all values for each annotation type
                    if not type_dict.get(type_key):
                        type_dict[type_key] = [(time_key, value)]
                    else:
                        type_dict[type_key].append((time_key, value))
        return type_dict, len(all_annotations)

def get_get_value_from_annotation(annoType, annotation):
    anno = ""
    if isinstance(annotation, str):
        anno = annoType+":"+annotation
    elif isinstance(annotation, float):
        anno = annoType+":"+str(round(annotation, 2))
    else:
        try:
            # value is the correct python object
            value_dict = vars(annotation)
            if type(value_dict) is str:
                anno = annoType+":" + value_dict
            elif type(value_dict) is dict:
                anno = annoType+":" + str(value_dict)
        except:
            # value is a namedtuple
            try:
                value_dict = annotation._asdict()
                #print(value_dict)
                atype = ""
                avalue = ""
                if "value" in value_dict:
                    avalue = value_dict['value']
                    if "type" in value_dict:
                        atype= value_dict['type']
                elif "label" in value_dict:
                    avalue = value_dict['label']
                    if "type" in value_dict:
                        atype = value_dict['type']
                    elif "text" in value_dict:
                        atype = value_dict['label']
                        avalue = value_dict['text']
                    else:
                        atype = "label"
                elif "type" in value_dict:
                    if "text" in value_dict:
                        atype= value_dict['type']
                        avalue= value_dict['text']
                    else:
                        avalue = value_dict['type']
                        atype = "label"
                elif "pos" in value_dict:
                    avalue = value_dict['pos']
                    atype = "pos"
                else:
                    print('UNKNOWN annotation', annotation)
                    #
                anno = atype+":"+avalue
            except:
                if annotation:
                    atype = annotation.type
                    value = annotation.value
                    anno = atype+":"+value
                    print('UNKNOWN annotation type', type(annotation), annotation)
    return anno

def remove_annotations(emissor:str, scenario:str, annotation_source: [str]):
    scenario_storage = ScenarioStorage(emissor)
    scenario_ctrl = scenario_storage.load_scenario(scenario)
    signals = scenario_ctrl.get_signals(Modality.TEXT)
    for signal in signals:
        keep_mentions = []
        for mention in signal.mentions:
            clear = False
            for annotation in mention.annotations:
                if annotation.source and annotation.source in annotation_source:
                    clear = True
                    break
            if not clear:
                keep_mentions.append(mention)
        signal.mentions = keep_mentions
    scenario_storage.save_scenario(scenario_ctrl)

def process_all_scenarios(emissor:str, scenarios:[]):
    for scenario in scenarios:
        if not scenario.startswith("."):
            scenario_path = os.path.join(emissor, scenario)
            has_scenario, has_text, has_image, has_rdf = check.check_scenario_data(scenario_path, scenario)
            check_message = "Scenario:" + scenario + "\n"
            check_message += "\tScenario JSON:" + str(has_scenario) + "\n"
            check_message += "\tText JSON:" + str(has_text) + "\n"
            check_message += "\tImage JSON:" + str(has_image) + "\n"
            check_message += "\tRDF :" + str(has_rdf) + "\n"
            print(check_message)
            if not has_scenario:
                print("No scenario JSON found. Skipping:", scenario_path)
            elif not has_text:
                print("No text JSON found. Skipping:", scenario_path)
            else:
                analyse_interaction_json(emissor, scenario)

def main(emissor_path:str, scenario:str):
    folders = []
    if not scenario:
        folders = os.listdir(emissor_path)
    else:
        folders=[scenario]

    process_all_scenarios(emissor_path, folders)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Statistical evaluation emissor scenario')
    parser.add_argument('--emissor-path', type=str, required=True, help="Path to the emissor folder", default='')
    parser.add_argument('--scenario', type=str, required=False, help="Identifier of the scenario", default='')
    args, _ = parser.parse_known_args()
    print('Input arguments', sys.argv)

    main(args.emissor_path, args.scenario)

