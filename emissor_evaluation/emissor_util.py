import os
from emissor.persistence import ScenarioStorage
from emissor.representation.scenario import Modality
from emissor.representation.scenario import Signal, TextSignal

def get_text_signals_from_a_scenario(emissor_folder:str, scenario_id:str):
    text_signals=[]
    scenario_folder = os.path.join(emissor_folder, scenario_id)
    scenario_storage = ScenarioStorage(emissor_folder)
    scenario_ctrl = scenario_storage.load_scenario(scenario_id)
    try:
        text_signals = scenario_ctrl.get_signals(Modality.TEXT)
    except:
        print('Error loading text signals from text.json')
    return text_signals

def get_speaker_from_text_signal(textSignal: TextSignal):
    speaker = None
    mentions = textSignal.mentions
    for mention in mentions:
        annotations = mention.annotations
        for annotation in annotations:
            if annotation.type == 'ConversationalAgent':
                speaker = annotation.value
                break
        if speaker:
            break
    return speaker
