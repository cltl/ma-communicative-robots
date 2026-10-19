from emissor.representation.scenario import TextSignal


def make_annotation_label (signal, threshold, annotations:[]):
    dacts = get_dact_from_text_signal(signal)
    gos = get_go_from_text_signal(signal)
    ekmans = get_ekman_from_text_signal(signal)
    sentiments = get_sentiment_from_text_signal(signal)
    likelihood = get_likelihood_from_text_signal(signal)
    label = "llh:"+str(round(likelihood, 2))
    # JSON(value='love', type='GO', confidence=0.890785276889801)
    # JSON(value='joy', type='EKMAN', confidence=0.9762245354068)
    # JSON(value='positive', type='SENTIMENT', confidence=0.9762245354068)
    # JSON(value='complaint', type='MIDAS', confidence=0.2305116355419159)
    if dacts:
        for dac in dacts:
            conf = dac.confidence
            dac_label = dac.value
            type = dac.type
            if conf > threshold:
                if not dac_label in label:
                    label += ";"+dac_label
    if sentiments and "sentiment" in annotations:
        for sentiment in sentiments:
            conf = sentiment.confidence
            sentiment_label = sentiment.value
            if not sentiment_label=="neutral":
                if conf > threshold:
                    if not sentiment_label in label:
                        label += ";"+sentiment_label
    if gos and "go" in annotations:
        for go in gos:
            conf = go.confidence
            go_label = go.value
            if not go_label=="neutral":
                type = go.type
                if conf > threshold:
                    if not go_label in label:
                        label += ";"+go_label
    if ekmans and "ekman" in annotations:
        for ekman in ekmans:
            conf = ekman.confidence
            ekman_label = ekman.value
            if not ekman_label=="neutral":
                type = ekman.type
                if conf > threshold:
                    if not ekman_label in label:
                        label += ";"+ekman_label
    return label


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

def get_sentiment_score_from_text_signal(textSignal: TextSignal):
    score = 0
    sentiments = get_sentiment_from_text_signal(textSignal)
    if sentiments:
        for sentiment in sentiments:
            if sentiment.value== 'negative':
                score += -1
            elif sentiment.value == "positive":
                score += 1
    return score

def get_go_feedback_score_from_text_signal(textSignal: TextSignal):
    score = 0
    negative = ['remorse', 'nervousness', 'fear', 'sadness', 'embarassment', 'disappointment', 'grief', 'disgust', 'anger', 'annoyance', 'disapproval', 'confusion']
    positive = ['joy', 'amusement','excitement', 'love', 'desire', 'optimism', 'caring', 'pride', 'admiration', 'gratitude', 'belief', 'approval', 'curiosity']
    gos = get_go_from_text_signal(textSignal)
    if gos:
        for go in gos:
            if go.value in negative:
                score += -1
            elif go.value in [positive]:
                score += 1
    return score

def get_ekman_feedback_score_from_text_signal(textSignal: TextSignal):
    score = 0
    negative = ['anger', 'disgust', 'fear', 'sadness']
    positive = ['joy']

    ekmans = get_ekman_from_text_signal(textSignal)
    if ekmans:
        for ekman in ekmans:
            if ekman.value in negative:
                score += -1
            elif ekman.value in [positive]:
                score += 1
    return score


def get_dact_feedback_score_from_text_signal(textSignal: TextSignal):
    score = 0;
    negative = ['neg_answer', 'complaint', 'abandon', 'apology','non-sense', 'hold']
    positive = ['pos_answer', 'back-channeling', 'appreciation', 'thanking', 'respond_to_apology']
    dacts = get_dact_from_text_signal(textSignal)
    if dacts:
        for dac in dacts:
            if dac.value in negative:
                score +=-1
            elif dac.value in positive:
                score += 1
    return score

def get_dact_from_text_signal(textSignal: TextSignal):
    values = []
    mentions = textSignal.mentions
    for mention in mentions:
        annotations = mention.annotations
        for annotation in annotations:
            if annotation.type.endswith('DialogueAct'):
                values.append(annotation.value)
    return values

def get_go_from_text_signal(textSignal: TextSignal):
    values = []
    mentions = textSignal.mentions
    for mention in mentions:
        annotations = mention.annotations
        for annotation in annotations:
            if annotation.value:
                if annotation.type and annotation.type.endswith('Emotion') and annotation.value.type=='GO':
                    values.append(annotation.value)
    return values


def get_ekman_from_text_signal(textSignal: TextSignal):
    values = []
    mentions = textSignal.mentions
    for mention in mentions:
        annotations = mention.annotations
        for annotation in annotations:
            if annotation.value:
                if annotation.type.endswith('Emotion') and annotation.value.type=='EKMAN':
                    values.append(annotation.value)
    return values

def get_sentiment_from_text_signal(textSignal: TextSignal):
    values = []
    mentions = textSignal.mentions
    for mention in mentions:
        annotations = mention.annotations
        for annotation in annotations:
            if annotation.value:
                if annotation.type.endswith('Emotion') and annotation.value.type=='SENTIMENT':
                    values.append(annotation.value)
    return values

def get_likelihood_from_text_signal(textSignal: TextSignal, threshold=0.3):
    score = 0
    mentions = textSignal.mentions
    for mention in mentions:
        annotations = mention.annotations
        for annotation in annotations:
            if annotation.value:
                if annotation.type.endswith('Likelihood'):
                    score = float(annotation.value)
    if score>0:
        score = 10*(score-threshold)
    return score

def get_utterances_with_context_from_signals(signals: [], max_context=200):
    ids = []
    quadruples = []
    speakers = set()
    context = ""
    target = ""
    cue = ""
    for index, signal in enumerate(signals):
        ids.append(signal.id)
        speaker = get_speaker_from_text_signal(signal)
        if speaker:
            speakers.add(speaker)
        if index == 0:
            target = ''.join(signal.seq)
        else:
            cue = target
            context += " " + target
            target = ''.join(signal.seq)
        if len(context) > max_context:
            context = context[len(context) - max_context:]
        target = target.replace("\n", ' ')
        quadruple = (context, target, cue, speaker)
        quadruples.append(quadruple)
    return ids, quadruples, speakers

def get_texts_from_utterances(utterances=[]):
    texts = []
    for utt in utterances:
        texts.append(utt[1].replace("\n", ' '))
    return texts


def find_signal(signals:[TextSignal], text:str):
    for index, s in enumerate(signals):
        utterance = ''.join(s.seq)
        if text in utterance:
            return index
    return -1
