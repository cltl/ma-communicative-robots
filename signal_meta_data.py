# Define Annotation Class        
from rdflib import URIRef, BNode, Literal, Namespace

lfriends = Namespace("http://leolani.cltl.nl/people/")

class Signal:
    def __init__(self, sui, modality, time_begin, time_end):
        self.sui = sui
        self.modality = modality
        self.time_begin = time_begin
        self.time_end = time_end


class friend:
    def __init__(self, name, age, gender):
        self.url = lfriends+name
        self.name = Literal(name)  # passing a string
        self.age = Literal(age)  # passing a python int
        self.gender = Literal(gender)


# Define ImageAnnotation Class        
class ImageAnnotation:
    def __init__(self, sui, suifile, time_begin, time_end, boxsegment, speaker, emotion):
        self.sui = sui
        self.suifile = suifile
        self.time_begin = time_begin
        self.time_end = time_end
        self.box = boxsegment
        self.speaker = speaker
        self.emotion = emotion


# Define ImageAnnotation Class
class TextAnnotation:
    def __init__(self, sui, suifile, time_begin, time_end, utterance, tokens, speaker, emotion, mention, referent):
        self.sui = sui
        self.suifile = suifile
        self.time_begin = time_begin
        self.time_end = time_end
        self.utterance = utterance
        self.tokens = tokens
        self.speaker = speaker
        self.emotion = emotion
        self.mention = mention
        self.referent = referent