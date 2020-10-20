# Define Annotation Class        
from rdflib import URIRef, BNode, Literal, Namespace

lfriends = Namespace("http://leolani.cltl.nl/people/")

class Signal:
    def __init__(self, sui, modality, time_begin, time_end):
        self.sui = sui
        self.modality = modality
        self.time_begin = time_begin
        self.time_end = time_end   
        
    def print(self):
        print('sui', self.sui)
        print('modality', self.modality)
        print('time start', self.time_begin)
        print('time end', self.time_end)
        
    def tojson(self):
        jsonout = {}
        jsonout["sui"] = self.sui
        jsonout["modality"] = self.modality
        jsonout["time_begin"] = self.time_begin
        jsonout["time_end"] = self.time_end
        return jsonout


class friend:
    def __init__(self, name, age, gender):
        self.url = lfriends+name
        self.name = Literal(name)  # passing a string
        self.age = Literal(age)  # passing a python int
        self.gender = Literal(gender)
        
    def tojson(self):
        jsonout = {}
        jsonout["url"] = self.url
        jsonout["name"] = self.name
        jsonout["age"] = self.age
        jsonout["gender"] = self.gender
        return jsonout

# Define ImageAnnotation Class        
class ImageAnnotation:
    def __init__(self, sui, suifile, time_begin, time_end, boxsegment, speaker, 
                 emotion):
        self.sui = sui
        self.suifile = suifile
        self.time_begin = time_begin
        self.time_end = time_end
        self.box = boxsegment
        self.speaker = speaker
        self.emotion = emotion
 
    def print(self):
        print('sui', self.sui) 
        print('sui file', self.suifile)
        print('time start', self.time_begin)
        print('time end', self.time_end)
        print('box', self.box)
        print('speaker', self.speaker)
        print('emotion', self.emotion)
 
    def tojson(self):
        jsonout = {}
        jsonout["sui"] = self.sui
        jsonout["suifile"] = self.suifile
        jsonout["time_begin"] = self.time_begin
        jsonout["time_end"] = self.time_end       
        jsonout["box"] = self.box       
        jsonout["speaker"] = self.speaker.tojson()
        jsonout["emotion"] = self.emotion
        return jsonout


        
# Define ImageAnnotation Class        
class TextAnnotation:
    def __init__(self, sui, suifile, time_begin, time_end, utterance, tokens, 
                 speaker, emotion, mention, referent):

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
        
        
    def print(self):
        print('sui', self.sui) 
        print('sui_file', self.suifile)
        print('time_begin', self.time_begin)
        print('time_end', self.time_end)
        print('speaker', self.speaker)
        print('emotion', self.emotion)
        print('utterance', self.utterance)
        print('tokens', self.tokens)
        print('mention', self.mention)
        print('referent', self.referent)

 
    def tojson(self):
        jsonout = {}
        jsonout["sui"] = self.sui
        jsonout["suifile"] = self.suifile
        jsonout["time_begin"] = self.time_begin
        jsonout["time_end"] = self.time_end    
        jsonout["speaker"] = self.speaker
        jsonout["emotion"] = self.emotion
        jsonout["utterance"] = self.utterance
        jsonout["tokens"] = self.tokens      
        jsonout["mention"] = self.mention      
        jsonout["referent"] = self.referent  
        return jsonout

