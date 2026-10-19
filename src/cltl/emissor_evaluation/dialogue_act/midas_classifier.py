from transformers import pipeline, XLMRobertaTokenizerFast
import dataclasses
from typing import Optional, List

# based on:
#https://github.com/DianDYu/MIDAS_dialog_act

## Labels in order from training
_LABELS={0: 'open_question_factual',
          1: 'pos_answer',
          2: 'command',
          3: 'opinion',
          4: 'statement',
          5: 'back-channeling',
          6: 'yes_no_question',
          7: 'appreciation',
          8: 'other_answers',
          9: 'thanking',
          10: 'open_question_opinion',
          11: 'hold',
          12: 'closing',
          13: 'comment',
          14: 'neg_answer',
          15: 'complaint',
          16: 'abandon',
          17: 'dev_command',
          18: 'apology',
          19: 'nonsense',
          20: 'other',
          21: 'opening',
          22: 'respond_to_apology'}


_LABEL2ID ={'open_question_factual': 0,
            'pos_answer': 1,
            'command': 2,
            'opinion': 3,
            'statement': 4,
            'back-channeling': 5,
            'yes_no_question': 6,
            'appreciation': 7,
            'other_answers': 8,
            'thanking': 9,
            'open_question_opinion': 10,
            'hold': 11, 'closing': 12,
            'comment': 13,
            'neg_answer': 14,
            'complaint': 15,
            'abandon': 16,
            'dev_command': 17,
            'apology': 18,
            'nonsense': 19,
            'other': 20,
            'opening': 21,
            'respond_to_apology': 22}

DIALOGUE_ACT_NEG_SCALE = [
    'abandon',
    'complaint',
    'nonsense',
    'neg_answer',
    'apology',
    'respond_to_apology',
    'comment',
    'opinion']

DIALOGUE_ACT_NEUTRAL_SCALE = [
    'command','statement','yes_no_question','other_answers','open_question_opinion',  'dev_command',
    'other', 'opening', 'hold', 'closing']

DIALOGUE_ACT_POS_SCALE = [
    'back-channeling','thanking',
    'open_question_factual',
    'pos_answer',
    'appreciation']

def _spread(dialogue_acts, low, high):
    """Spreads the dialogue acts in the order of the list evenly over the range from low to high, rounded to integers."""
    if len(dialogue_acts) == 1:
        return {dialogue_acts[0]: round((low + high) / 2)}
    step = (high - low) / (len(dialogue_acts) - 1)
    return {dialogue_act: round(low + index * step) for index, dialogue_act in enumerate(dialogue_acts)}

# Score of each dialogue act from -5 to +5: the negative scale is spread from -5 (first) to -1 (last),
# the neutral scale is 0 and the positive scale is spread from 1 (first) to 5 (last)
DIALOGUE_ACT_SCORES = {**_spread(DIALOGUE_ACT_NEG_SCALE, -5, -1),
                       **{dialogue_act: 0 for dialogue_act in DIALOGUE_ACT_NEUTRAL_SCALE},
                       **_spread(DIALOGUE_ACT_POS_SCALE, 1, 5)}

def get_dialogue_act_score(dialogue_act):
    """Returns the score from -5 to +5 of a dialogue act, 0 for dialogue acts that are not on a scale."""
    return DIALOGUE_ACT_SCORES.get(dialogue_act, 0)

@dataclasses.dataclass
class DialogueAct:
    """
    Information about a Dialogue Act.
    """
    type: str
    value: str
    confidence: Optional[float]

class MidasDialogTagger():
    def __init__(self, model_path):
        print("Loading MIDAS model...", model_path)
        # The model is an XLM-RoBERTa model, but its config says "roberta" and its tokenizer_config.json does not name
        # the tokenizer class, so AutoTokenizer loads a RobertaTokenizer that splits the text into single characters.
        # We therefore load the XLM-RoBERTa tokenizer explicitly and pass it to the pipeline.
        self._tokenizer = XLMRobertaTokenizerFast.from_pretrained(model_path)
        self._pipeline = pipeline("text-classification", model=model_path, tokenizer=self._tokenizer, top_k=1)
        self._label2id = _LABEL2ID
        self._id2label = _LABELS
        self._dialog =[""] ### initialise with an empty string to get started

    def reset(self):
        """Forgets the previous utterances, e.g. before tagging a new conversation."""
        self._dialog = [""]

    def _fit_to_model(self, turn0, utterance):
        """Shortens the previous turn and the utterance to fit the maximum input length of the model (512 tokens).
        The end of the previous turn is kept as context, and the utterance is only cut off if it is too long by itself."""
        # room for the start, separator and end tokens
        max_tokens = self._tokenizer.model_max_length - 3
        tokens0 = self._tokenizer.tokenize(turn0)
        tokens1 = self._tokenizer.tokenize(utterance)
        if len(tokens0) + len(tokens1) <= max_tokens:
            return turn0, utterance
        if len(tokens1) >= max_tokens:
            return "", self._tokenizer.convert_tokens_to_string(tokens1[:max_tokens])
        room = max_tokens - len(tokens1)
        return self._tokenizer.convert_tokens_to_string(tokens0[-room:]), utterance

    def extract_dialogue_act(self, utterance: str)-> List[DialogueAct]:
        if not utterance:
            return []
        turn0 = self._dialog[-1]
        self._dialog.append(utterance)
        turn0, utterance = self._fit_to_model(turn0, utterance)
        string = turn0 + self._tokenizer.sep_token + utterance
        result = self._pipeline(string, truncation=True)
        print(result)
        top_result = result[0]
        dialogueAct = DialogueAct(type="MIDAS", value=top_result[0]['label'], confidence=float(top_result[0]['score']))
        return [dialogueAct]

if __name__ == "__main__":
    sentences_en = ["I love cats", "Do you love cats?","Yes, I do", "Do you love cats?", "No, dogs"]
    sentences_nl = ["Ik ben dol op katten", "Hou jij van katten?","Ja, ik ben dol op ze", "Hou jij van katten?", "Nee, honden"]
    model_path = "CLTL/midas-da-xlmroberta"
#    model_path = "/Users/piek/Desktop/Leolani/leolani-models/dialogue_models/midas-da-xlmroberta"

    analyzer = MidasDialogTagger(model_path=model_path)
    for sentence in sentences_en+sentences_nl:
        response = analyzer.extract_dialogue_act(sentence)
        print(sentence, response)
