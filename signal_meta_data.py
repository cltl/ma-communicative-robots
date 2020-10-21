# Define Annotation Class        
from rdflib import URIRef, BNode, Literal, Namespace

lfriends = Namespace("http://leolani.cltl.nl/people/")

class Mention:
    def __init__(self, token_id, offset, phrase, referent):
        self.token_id = token_id
        self.offset = offset
        self.phrase = phrase
        self.referent = referent

    def __init__(self, tokentuple, referent):
        self.token_id = tokentuple[0]
        self.offset = tokentuple[1]
        self.phrase = tokentuple[2]
        self.referent = referent


class Signal:
    def __init__(self, sui, modality, time_begin, time_end):
        self.sui = sui
        self.modality = modality
        self.time_begin = time_begin
        self.time_end = time_end


class Friend:
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
    def __init__(self, sui, 
                 suifile, 
                 time_begin, 
                 time_end,
                 chat_id,
                 utterance_id,
                 utterance, 
                 tokens, 
                 speaker, 
                 emotion, 
                 mentions,
                 triples
                ):
        self.sui = sui
        self.suifile = suifile
        self.time_begin = time_begin
        self.time_end = time_end
        self.chat_id = chat_id
        self.utterance_id = utterance_id
        self.utterance = utterance
        self.tokens = tokens ### tuples with offsets, strings and token ids
        self.speaker = speaker
        self.emotion = emotion
        self.mentions = mentions ## this should be a list of tuples with tokens and referents
        self.triples = triples ## list of triples