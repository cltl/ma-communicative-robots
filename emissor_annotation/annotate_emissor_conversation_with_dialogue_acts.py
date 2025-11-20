import argparse
from emissor.persistence import ScenarioStorage
from emissor.representation.scenario import Modality, Signal
from cltl.dialogue_act_classification.add_dialogue_acts_to_emissor import DialogueActAnnotator
import os

def main(emissor: str, model_name="MIDAS", scenario="", model_path=""):
    print("Processing emissor", emissor)
    print("Using model", model_path)
    annotator = DialogueActAnnotator(model_path=model_path, model_name=model_name)
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
            annotator.remove_annotations(signal,[model_name, "python-source:cltl.dialogue_act_classification.midas_classifier"])
            annotator.process_signal(scenario=scenario_ctrl, signal=signal)
        #### Save the modified scenario to emissor
        scenario_storage.save_scenario(scenario_ctrl)

### How to run: python3 examples/annotato_emissor_conversation_with_emotions.py --emissor "../data/emissor" --model "../resources/midas-da-xlmroberta" --model-name midas --scenario "14a1c27d-dfd2-465b-9ab2-90e9ea91d214"

if __name__ == '__main__':
    default = "../data/emissor"
    model="CLTL/midas-da-xlmroberta"
    parser = argparse.ArgumentParser(description='Annotate emissor with emotions')
    parser.add_argument('--emissor', type=str, required=True, help="Path to the folder with emissor scenarios", default=default)
    parser.add_argument('--scenario', type=str, required=False, help="Identifier of the scenario. If left out all subfolders will be considered as scenarios to process", default='')
    parser.add_argument('--model_path', type=str, required=False, help="Path to the MIDAS DA XLMRoBERTa model", default=model)
    parser.add_argument('--model_name', type=str, required=False, help="Name of the model to label the provenance of the annotation in emissor", default='MIDAS')

    args, _ = parser.parse_known_args()
    folder = os.path.exists(args.emissor)
    if not os.path.exists(args.emissor):
        raise ValueError("The folder %s does not exists. The --emissor argument should point to a folder that contains the scenarios to annotate", args.emissor)


    main(emissor=args.emissor,
         scenario=args.scenario,
         model_path=model,
         model_name = args.model_name)
