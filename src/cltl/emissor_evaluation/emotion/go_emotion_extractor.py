import time
import dataclasses
from typing import Optional, Any, List, Union

from transformers import pipeline

from src.cltl.emissor_evaluation.emotion import emotion_types as emotions


_MODEL_NAME = "bhadresh-savani/bert-base-go-emotion"
_THRESHOLD = 0.5


# GO Emotions is a finetuned BERT transformer with the GO Emotion data
#https://github.com/google-research/google-research/tree/master/goemotions
#https://github.com/google-research/google-research/blob/master/goemotions/goemotions_model_card.pdf


@dataclasses.dataclass
class Emotion:
    """
    Information about an Emotion.
    "Emotion type"
    "Emotion value"
    "confidence"
    "source"
    """
    # TODO Collection[EmotionType]?
    type: emotions.EmotionType
    value: str
    confidence: Optional[float]

    def to_enum(self) -> Union[emotions.GoEmotion, emotions.EkmanEmotion, emotions.EmoticEmotion, emotions.Sentiment]:
        if self.type == emotions.EmotionType.GO:
            return emotions.GoEmotion[self.value.upper()]
        if self.type == emotions.EmotionType.EKMAN:
            return emotions.EkmanEmotion[self.value.upper()]
        if self.type == emotions.EmotionType.EMOTIC:
            return emotions.EmoticEmotion[self.value.upper()]
        if self.type == emotions.EmotionType.SENTIMENT:
            return emotions.Sentiment[self.value.upper()]

        raise ValueError("Unknown type: " + self.type)


class GoEmotionDetector():
    def __init__(self, model: str):
        self.emotion_pipeline = pipeline('sentiment-analysis',  model=model, top_k=None)

    def extract_audio_emotions(self, audio_signal: Any) -> List[Emotion]:
        raise NotImplementedError()

    def extract_text_emotions(self, utterance: str) -> List[Emotion]:
        if not utterance:
            return []

        start = time.time()

        results = []

        # truncation avoids errors for utterances longer than the 512 tokens of the model
        response = self.emotion_pipeline(utterance, truncation=True)

        emotion_labels = emotions.sort_predictions(response[0])
        results.extend(self._filter_by_threshold(emotions.EmotionType.GO, emotion_labels))

        ekman_labels = emotions.get_total_mapped_scores(emotions.go_ekman_map, emotion_labels)
        results.extend(self._filter_by_threshold(emotions.EmotionType.EKMAN, ekman_labels))

        sentiment_labels = emotions.get_total_mapped_scores(emotions.go_sentiment_map, emotion_labels)
        results.extend(self._filter_by_threshold(emotions.EmotionType.SENTIMENT, sentiment_labels))

        return results

    def _filter_by_threshold(self, emotion_type, results):
        return [Emotion(type=emotion_type, value=result['label'], confidence=result['score'])
                for result in results
                if result['score'] > 0 and result['score'] / results[0]['score'] > _THRESHOLD]

if __name__ == "__main__":
    utterance = "I love cats."
    analyzer = GoEmotionDetector(model=_MODEL_NAME)
    results = analyzer.extract_text_emotions(utterance)
    emotion_json ={}
    for emotion in results:
        emotion_json.update({'type': emotion.type, 'value':emotion.value, 'confident': emotion.confidence})
        print(emotion_json)
