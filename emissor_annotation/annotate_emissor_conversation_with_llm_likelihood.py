import logging
import re
import os
import argparse
import sys
import uuid
import time
from dataclasses import dataclass
from transformers import pipeline, AutoTokenizer

from cltl.combot.infra.time_util import timestamp_now
from emissor.representation.scenario import Mention, TextSignal, Annotation
from emissor.persistence import ScenarioStorage
from emissor.persistence.persistence import ScenarioController
from emissor.processing.api import SignalProcessor
from emissor.representation.scenario import Modality, Signal
logger = logging.getLogger(__name__)

@dataclass
class Likelihood:
    score: float
    model: str
    max: float

class MLM:
    def __init__(self, path=None, top_results=20):
        """ Load pretrained RoBERTa model for masked Langauge model based likelihood.

            params
            str path: path to stored model or None

            returns: None
        """
        if path is None:
            self.__model_name = 'google-bert/bert-base-multilingual-cased'
        else:
            self.__model_name = path

        print('Extracting the likelihood score using', self.__model_name)

        self.__tokenizer = AutoTokenizer.from_pretrained(self.__model_name, local_files_only=True)
        self.__model = pipeline("fill-mask", model=self.__model_name)
        self.__model.top_k = top_results  ### we check against the top results

    def mask_target_sentence(self, context, target):
        masked_targets = []
        ## We limit the length of the target as too long utterance break the token limit
        target_tokens = re.split(' ', target[:500])
        for index, token in enumerate(target_tokens):
            sequence = context + " "
            for token in target_tokens[:index]:
                sequence += token + " "
            sequence += self.__tokenizer.mask_token
            for token in target_tokens[index + 1:]:
                sequence += " " + token
            masked_targets.append(sequence)
        return masked_targets, target_tokens

    def sentence_likelihood(self, context, target):
        masked_targets, target_tokens = self.mask_target_sentence(context, target)
        expected_target = ""
        max_scores = []
        scores = []
        for masked_target, token in zip(masked_targets, target_tokens):
            results = self.__model(masked_target)
            expected_target += results[0]['token_str'] + " "
            max_scores.append(results[0]['score'])
            match = False
            for result in results:
                if result['token_str'].lower().strip() == token.lower():
                    scores.append(result['score'])
                    match = True
                    break

            if not match:
                scores.append(0)
        likelihood = sum(scores) / len(scores)
        max_likelihood = sum(max_scores) / len(max_scores)

        return likelihood, expected_target, max_likelihood

    def score_pairs_for_likelihood(self, turns: []):
        for context, target in turns:
            llh, best_sentence, max_score = self.sentence_likelihood(context, target)
            print('Likelihood:', llh, 'Max score:', max_score, 'Best sentence:', best_sentence)

@dataclass
class LikelihoodEvent:
    @classmethod
    # def create_text_mention(cls, text_signal: TextSignal, llh: Likelihood , source: str):
    #     return cls(class_type(cls), [LikelihoodEvent.to_mention(text_signal, llh, source)])

    @staticmethod
    def to_mention(text_signal: TextSignal, llh: Likelihood, source: str) -> Mention:
        """
        Create Mention with annotations.
        """
        segment = text_signal.ruler
        annotation = Annotation("Likelihood", llh, source, timestamp_now())

        return Mention(str(uuid.uuid4()), [segment], [annotation])

class LikelihoodAnnotator (SignalProcessor):

    def __init__(self, model: str, model_name: str, max_content: int, top_results: int):
        """ an evaluator that will use reference metrics to approximate the quality of a conversation, across turns.
        params
        returns: None
        """
        self._classifier = MLM(path=model, top_results=top_results)
        self._model_name = model_name
        self._max_context = max_content
        self._max_text_length=514
        self._context = ""


    def process_signal(self, scenario: ScenarioController, signal: Signal):
        if not signal.modality == Modality.TEXT:
            return
        mention = self.annotate(signal)
        signal.mentions.append(mention)

    def annotate(self, textSignal):
        utterance = textSignal.text
        if len(utterance)> self._max_text_length:
            utterance=utterance[:self._max_text_length]
        likelihood, expected_target, max_likelihood = self._classifier.sentence_likelihood(self._context, utterance)
        mention = LikelihoodEvent.to_mention(textSignal, likelihood, self._model_name)
        ### Update the context
        self._context += utterance
        if len(self._context)> self._max_context:
            self._context=self._context[:self._max_context]

        return mention

    def remove_annotations(self, signal, annotation_source: [str]):
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

### How to run: python3 annotate_emissor_conversation_with_llm_likelihood.py --emissor "../data/emissor"

def main(emissor:str, scenario:str, model_path="google-bert/bert-base-multilingual-cased", model_name="mBERT", max_context=300, len_top_tokens=20):

    annotator = LikelihoodAnnotator(model=model_path, model_name=model_name, max_content=max_context,
                                    top_results=len_top_tokens)

    print("model_path", model_path)
    print("model_name", model_name)
    print("context_threshold", max_context)
    print("top_results", len_top_tokens)
    scenario_storage = ScenarioStorage(emissor)
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
            annotator.remove_annotations(signal=signal,annotation_source=[model_name])
            annotator.process_signal(scenario=scenario_ctrl, signal=signal)
        #### Save the modified scenario to emissor
        scenario_storage.save_scenario(scenario_ctrl)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Statistical evaluation emissor scenario')
    parser.add_argument('--emissor', type=str, required=False, help="Path to the emissor folder", default='')
    parser.add_argument('--scenario', type=str, required=False, help="Identifier of the scenario", default='')
    parser.add_argument('--model_path', type=str, required=False, help="Path to the model or huggingface URL", default="google-bert/bert-base-multilingual-cased")
    parser.add_argument('--model_name', type=str, required=False, help="Model name for annotation in emissor", default="mBERT")
    parser.add_argument('--context', type=int, required=False, help="Maximum character length of the context" , default=300)
    parser.add_argument('--top_results', type=int, required=False, help="Maximum number of MASKED results considered" , default=20)
    args, _ = parser.parse_known_args()
    print('Input arguments', sys.argv)
    main(emissor=args.emissor,
         scenario=args.scenario,
         model_path=args.model_path,
         model_name = args.model_name,
         max_context=args.context,
         len_top_tokens=args.top_results)

# DEBUG
#     emissor_path = "/Users/piek/Desktop/test/cltl-llm-app/py-app/storage/emissor"
#     scenario=""
#     main(emissor_path=emissor_path,
#          scenario=scenario,
#          model_path=args.model_path,
#          model_name = args.model_name,
#          max_context=args.context,
#          len_top_tokens=args.top_results)

                    