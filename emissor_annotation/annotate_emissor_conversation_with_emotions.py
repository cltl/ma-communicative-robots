import argparse
from emissor.persistence import ScenarioStorage
from emissor.representation.scenario import Modality, Signal
from cltl.emotion_extraction.add_emotions_to_emissor import EmotionAnnotator
import pathlib
import os


def remove_annotations(signal, annotation_source: [str]):
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

def main(emissor: str, scenario: str, model_path: str, model_name = "GO"):
    annotator = EmotionAnnotator(model=model_path, model_name=model_name)
    scenario_storage = ScenarioStorage(emissor)
    scenarios = []
    if scenario:
        scenarios = [scenario]
    else:
        scenarios = list(scenario_storage.list_scenarios())
    print("Processing scenarios: ", scenarios)
    for scenario in scenarios:
        print('Processing scenario', scenario)
        scenario_ctrl = scenario_storage.load_scenario(scenario)
        signals = scenario_ctrl.get_signals(Modality.TEXT)
        for signal in signals:
            remove_annotations(signal=signal,annotation_source=[model_name])
            annotator.process_signal(scenario=scenario_ctrl, signal=signal)
        #### Save the modified scenario to emissor
        scenario_storage.save_scenario(scenario_ctrl)



### How to run: python annotate_emissor_conversation_with_emotions.py --emissor "../data/emissor"

if __name__ == '__main__':
    default = "../data/emissor"
    model="bhadresh-savani/bert-base-go-emotion"
    model="AnasAlokla/multilingual_go_emotions"
  #  Languages: Arabic, English, French, Spanish, Dutch, Turkish
    parser = argparse.ArgumentParser(description='Annotate emissor with emotions')
    parser.add_argument('--emissor', type=str, required=True, help="Path to the folder with emissor scenarios", default=default)
    parser.add_argument('--scenario', type=str, required=False, help="Identifier of the scenario. If left out all subfolders will be considered as scenarios to process", default='')
    parser.add_argument('--model_path', type=str, required=False, help="Path to the GO Emotions BERT model", default=model)
    parser.add_argument('--model_name', type=str, required=False, help="Name of the model to label the provenance of the annotation in emissor", default='GO')

    args, _ = parser.parse_known_args()
    folder = os.path.exists(args.emissor)
    if not os.path.exists(args.emissor):
        raise ValueError("The folder %s does not exists. The --emissor argument should point to a folder that contains the scenarios to annotate", args.emissor)

    main(emissor=args.emissor,
         scenario=args.scenario,
         model_path= model,
         model_name = args.model_name)
