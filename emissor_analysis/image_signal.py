from emissor.representation.scenario import ImageSignal


def make_annotation_label (signal):
    face = get_face_for_image_signal(signal)
    object = get_object_for_image_signal(signal)
    id = get_identity_for_image_signal(signal)
    emotion = get_emotic_label_for_image_signal(signal)
#    emotion = get_ekman_label_for_image_signal(signal)
#    emotion = get_sentiment_label_for_image_signal(signal)
    return object, face, id, emotion


def get_face_for_image_signal(imageSignal: ImageSignal):
    label = ""
    mentions = imageSignal.mentions
    for mention in mentions:
        annotations = mention.annotations
        for annotation in annotations:
            if annotation.type == 'Face' and annotation.value:
                age = annotation.value.age
                gender = annotation.value.gender
                if not gender in label:
                    label += gender+"-"
                if not str(age) in label:
                    label+= str(age)
                return label
    return label

def get_emotic_values_from_text_signal(signal: ImageSignal):
    values = []
    mentions = signal.mentions
    for mention in mentions:
        annotations = mention.annotations
        for annotation in annotations:
            if annotation.type == 'python-type:cltl.emotion_extraction.api.Emotion' and annotation.value:
                if annotation.value.type=="EMOTIC":
                    values.append(annotation.value.value)
    return values

def get_emotic_feedback_score_from_signal(signal: ImageSignal):
    score = 0;
    #emotic mapping
    negative = ['anger', 'annoyance', 'aversion', 'disapproval','disconnection', 'disquietment', 'doubt_confusion', 'embarrasment', 'fatigue', 'fear','pain', 'sadness', 'suffering', 'yearning']
    positive = ['affection', 'anticipation', 'confidence', 'esteem', 'engagement','excitement', 'happiness', 'peace','pleasure','sensitivity','surpirse','sympathy']
    values = get_emotic_values_from_text_signal(signal)
    if values:
        for v in set(values):
            if v in negative:
                score +=-1
            elif v in positive:
                score += 1
            else:
                print("emotic", v)
    return score


def get_emotic_label_for_image_signal(imageSignal: ImageSignal):
    label = ""
    mentions = imageSignal.mentions
    for mention in mentions:
        annotations = mention.annotations
        for annotation in annotations:
            if annotation.type == 'python-type:cltl.emotion_extraction.api.Emotion' and annotation.value:
                if annotation.value.type=="EMOTIC":
                    label = annotation.value.value
                    confidence = annotation.value.confidence
                    label+=":"+str(round(confidence, 2))
                    return label
    return label

def get_ekman_label_for_image_signal(imageSignal: ImageSignal):
    label = ""
    mentions = imageSignal.mentions
    for mention in mentions:
        annotations = mention.annotations
        for annotation in annotations:
            if annotation.type == 'python-type:cltl.emotion_extraction.api.Emotion' and annotation.value:
                if annotation.value.type=="EKMAN":
                    label = annotation.value.value
                    confidence = annotation.value.confidence
                    label+=":"+str(round(confidence, 2))
                    return label
    return label

def get_sentiment_label_for_image_signal(imageSignal: ImageSignal):
    label = ""
    mentions = imageSignal.mentions
    for mention in mentions:
        annotations = mention.annotations
        for annotation in annotations:
            if annotation.type == 'python-type:cltl.emotion_extraction.api.Emotion' and annotation.value:
                if annotation.value.type=="SENTIMENT":
                    label = annotation.value.value
                    confidence = annotation.value.confidence
                    label+=":"+str(round(confidence, 2))
                    return label
    return label

def get_object_for_image_signal(imageSignal: ImageSignal):
    label = ""
    mentions = imageSignal.mentions
    for mention in mentions:
        annotations = mention.annotations
        for annotation in annotations:
            if annotation.type == 'python-type:cltl.object_recognition.api.Object' and annotation.value:
                object = annotation.value.label
                conf = annotation.value.confidence
                if not object in label:
                    label += object+"-"+str(round(conf, 2))+";"
            elif annotation.type == 'ObjectType':
                object = annotation.value
                if not object in label:
                    label += object+";"
    return label

def get_identity_for_image_signal(imageSignal: ImageSignal):
    label = ""
    mentions = imageSignal.mentions
    for mention in mentions:
        annotations = mention.annotations
        for annotation in annotations:
            if annotation.type == 'VectorIdentity' and annotation.value:
                id = annotation.value
                if not id in label:
                    label = id
            elif annotation.type == 'ObjectIdentity' and annotation.value:
                id = annotation.value
                if not id in label:
                    label = id
    return label
