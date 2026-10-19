from enum import Enum, auto


class EmotionType(Enum):
    GO = auto()
    EKMAN = auto()
    EMOTIC = auto()
    SENTIMENT = auto()


class Sentiment(Enum):
    POSITIVE = auto()
    NEGATIVE = auto()
    NEUTRAL = auto()


class EkmanEmotion(Enum):
    ANGER = auto()
    DISGUST = auto()
    FEAR = auto()
    JOY = auto()
    SADNESS = auto()
    SURPRISE = auto()
    NEUTRAL = auto()


class GoEmotion(Enum):
    AMUSEMENT = auto()
    EXCITEMENT = auto()
    JOY = auto()
    LOVE = auto()
    DESIRE = auto()
    OPTIMISM = auto()
    CARING = auto()
    PRIDE = auto()
    ADMIRATION = auto()
    GRATITUDE = auto()
    RELIEF = auto()
    APPROVAL = auto()
    FEAR = auto()
    NERVOUSNESS = auto()
    REMORSE = auto()
    EMBARRASSMENT = auto()
    DISAPPOINTMENT = auto()
    SADNESS = auto()
    GRIEF = auto()
    DISGUST = auto()
    ANGER = auto()
    ANNOYANCE = auto()
    DISAPPROVAL = auto()
    REALIZATION = auto()
    SURPRISE = auto()
    CURIOSITY = auto()
    CONFUSION = auto()
    NEUTRAL = auto()


class EmoticEmotion(Enum):
    """ 26 Emotions use in
    Kosti R., J.M. Alvarex, A. Recasens, and A. Paedriza, (2019), "Context based emotion recognition using emotic dataset",
    IEEE Transactions on patterns analysis and machine intelligence.

    Ordered as used in the Emotic model.
    """
    # KEEP ORDER!
    AFFECTION = 1
    ANGER = 2
    ANNOYANCE = 3
    ANTICIPATION = 4
    AVERSION = 5
    CONFIDENCE = 6
    DISAPPROVAL = 7
    DISCONNECTION = 8
    DISQUIETMENT = 9
    DOUBT_CONFUSION = 10
    EMBARRASSMENT = 11
    ENGAGEMENT = 12
    ESTEEM = 13
    EXCITEMENT = 14
    FATIGUE = 15
    FEAR = 16
    HAPPINESS = 17
    PAIN = 18
    PEACE = 19
    PLEASURE = 20
    SADNESS = 21
    SENSITIVITY = 22
    SUFFERING = 23
    SURPRISE = 24
    SYMPATHY = 25
    YEARNING = 26

EMOTION_NEG_SCALE = [
    "DISAPPROVAL", "ANNOYANCE", "ANGER", "DISGUST", "GRIEF", "SADNESS",
    "DISAPPOINTMENT", "EMBARRASSMENT", "REMORSE", "NERVOUSNESS", "FEAR",
    "CONFUSION"
]

EMOTION_NEUTRAL_SCALE = [ "SURPRISE", "REALIZATION", "UNDERSPECIFIED", "NEUTRAL"
]
EMOTION_POS_SCALE = ["CURIOSITY", "APPROVAL", "RELIEF", "GRATITUDE", "ADMIRATION", "PRIDE", "CARING",
    "OPTIMISM", "DESIRE", "LOVE", "JOY", "EXCITEMENT", "AMUSEMENT",
]

def _spread(emotions, low, high):
    """Spreads the emotions in the order of the list evenly over the range from low to high, rounded to integers."""
    if len(emotions) == 1:
        return {emotions[0]: round((low + high) / 2)}
    step = (high - low) / (len(emotions) - 1)
    return {emotion: round(low + index * step) for index, emotion in enumerate(emotions)}

# Score of each emotion from -5 to +5: the negative scale is spread from -5 (first) to -1 (last),
# the neutral scale is 0 and the positive scale is spread from 1 (first) to 5 (last)
EMOTION_SCORES = {**_spread(EMOTION_NEG_SCALE, -5, -1),
                  **{emotion: 0 for emotion in EMOTION_NEUTRAL_SCALE},
                  **_spread(EMOTION_POS_SCALE, 1, 5)}

def get_emotion_score(emotion):
    """Returns the score from -5 to +5 of an emotion label (e.g. 'joy'), 0 for emotions that are not on a scale."""
    if not emotion:
        return 0
    return EMOTION_SCORES.get(emotion.upper(), 0)

class VADEmotion(Enum):
    """ VAD Emotions use in
        Kosti R., J.M. Alvarex, A. Recasens, and A. Paedriza, (2019), "Context based emotion recognition using emotic dataset",
        IEEE Transactions on patterns analysis and machine intelligence.

    Ordered as used in the Emotic model.
    """
    # KEEP ORDER!
    VALENCE = 1
    AROUSAL = 2
    DOMINANCE = 3


# Use a mapping to get a dictionary of the mapped GO_emotion scores
def get_mapped_scores(emotion_map, go_emotion_scores):
    mapped_scores = {}

    for prediction in go_emotion_scores:
        go_emotion = prediction['label']
        for key in emotion_map:
            if go_emotion in emotion_map[key]:
                if not key in mapped_scores:
                    mapped_scores[key] = [prediction['score']]
                else:
                    mapped_scores[key].append(prediction['score'])
    return mapped_scores


# Get the averaged score for an emotion or sentiment from the GO_emotion scores mapped according to the emotion_map
def get_total_mapped_scores(emotion_map, go_emotion_scores):
    total_mapped_scores = []
    mapped_scores = get_mapped_scores(emotion_map, go_emotion_scores)
    for emotion in mapped_scores:
        lst = mapped_scores[emotion]
        total_score = sum(lst)
        total_mapped_scores.append({'label':emotion, 'score':total_score})
    return sort_predictions(total_mapped_scores)


# TODO use enums here to avoid duplication
# MAP EKMAN TO SENTIMENT
ekman_sentiment_map={
    "positive": ["joy", "positive"],
    "negative": ["anger", "disgust", "fear", "sadness", "negative"],
    "neutral": ["neutral", "surprise", "ambiguous"]
}


# Mapping GO_Emotions to sentiment values
go_sentiment_map={
    "positive": ["curiosity", "amusement", "excitement", "joy", "love", "desire", "optimism", "caring", "pride", "admiration", "gratitude", "relief", "approval"],
    "negative": ["fear",  "confusion", "nervousness", "remorse", "embarrassment", "disappointment", "sadness", "grief", "disgust", "anger", "annoyance", "disapproval"],
    "neutral": ["realization", "surprise", "neutral"]
}


# Mapping GO_Emotions to Ekman values
go_ekman_map={
    "anger": ["anger", "annoyance", "disapproval"],
    "disgust": ["disgust"],
    "fear": ["fear", "nervousness", "confusion"],
    "joy": ["joy", "curiosity", "amusement", "approval", "excitement", "gratitude",  "love", "optimism", "relief", "pride", "admiration", "desire", "caring"],
    "sadness": ["sadness", "disappointment", "embarrassment", "grief",  "remorse"],
    "surprise": ["surprise", "realization"],
    "neutral": ["neutral"]
}

face_ekman_map={
    "joy" : ['affection', 'confidence', 'esteem', 'excitement', 'happiness',  'peace', 'pleasure',  'sympathy'],
    "anger": ['anger', 'annoyance', 'embarrassment'],
    "fear": ['doubt_confusion', 'fear', 'pain',  'suffering', 'yearning'],
    "disgust": ['aversion', 'disapproval', 'disconnection', 'embarrassment'],
    "sadness": ['disconnection', 'disquietment', 'fatigue', 'sadness'],
    "surprise": ['engagement', 'excitement', 'sensitivity', 'surprise'],
    "neutral": ['anticipation', 'peace']
}

face_sentiment_map={
    "positive" : ['affection', 'confidence', 'esteem', 'excitement', 'happiness',  'peace', 'pleasure',  'sympathy', 'engagement', 'excitement', 'sensitivity', 'surprise'],
    "negative": ['anger', 'annoyance', 'embarrassment', 'doubt_confusion', 'fear', 'pain',  'suffering', 'yearning', 'aversion', 'disapproval', 'disconnection', 'embarrassment', 'disconnection', 'disquietment', 'fatigue', 'sadness'],
    "neutral": ['anticipation', 'peace']
}

# Sort a list of results in JSON format by the value of the score element
def sort_predictions(predictions):
    return sorted(predictions, key=lambda x: x['score'], reverse=True)

