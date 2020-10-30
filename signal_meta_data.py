# Define Annotation Class
import enum
import os

import json
import uuid
from rdflib import URIRef, Namespace
from typing import Iterable, Tuple, Union, Dict

friends_namespace = Namespace("http://cltl.nl/leolani/friends/")
data_namespace = Namespace("http://cltl.nl/combot/signal/")
# TODO reference ontolgoy
predicate_namespace = Namespace("http://cltl.nl/combot/predicate/")


class EntityType(enum.Enum):
    PERSON = 0
    FRIEND = 1
    OBJECT = 2


class Modality(enum.Enum):
    IMAGE = 0
    TEXT = 1
    AUDIO = 2


class Emotion(enum.Enum):
    NEUTRAL = 0
    ANGER = 1
    DISGUST = 2
    FEAR = 3
    HAPPINESS = 4
    JOY = 5
    SADNESS = 6
    SURPRISE = 7


class Gender(enum.Enum):
    UNDEFINED = 0
    FEMALE = 1
    MALE = 2
    OTHER = 3


# TODO Relate the container/ruler, or at least add a type
class Segment():
    """Base class of segments that allow to identify a segment relative to a ruler in a signal"""


class OffsetSegment(Segment):
    def __init__(self, start: int, end: int) -> None:
        self.offset = (start, end)

    @property
    def start(self):
        return self.offset[0]

    @property
    def end(self):
        return self.offset[1]


class BoundingBoxSegment(Segment):
    def __init__(self, x_min: int, y_min: int, x_max: int, y_max: int) -> None:
        self.bounding_box = (x_min, y_min, x_max, y_max)

    @property
    def x_min(self):
        return self.bounding_box[0]

    @property
    def y_min(self):
        return self.bounding_box[1]

    @property
    def x_max(self):
        return self.bounding_box[2]

    @property
    def y_max(self):
        return self.bounding_box[3]


class TimeSegment(Segment):
    def __init__(self, start: int, end: int) -> None:
        self.end = end
        self.start = start


# TODO do we need objects?
class Object:
    pass


class Person:
    # TODO Should be identified by its properties not by an ID (though it should have an ID)?
    def __init__(self, id: Union[uuid.UUID, str, None], name: str, age: int, gender: Gender, emotion: Emotion):
        self.id = id if id else uuid.uuid4()
        self.name = name
        self.age = age
        self.gender = gender
        self.emotion = emotion


# TODO do we need a Person?
class Friend(Person):
    pass


class Entity:
    def __init__(self, id: URIRef, type: EntityType) -> None:
        self.id = id
        self.type = type


class Triple:
    def __init__(self, subject: Entity, predicate: URIRef, object_: Entity) -> None:
        self.subject = subject
        self.predicate = predicate
        self.object = object_

    # TODO make this more generic
    @classmethod
    def from_friends(cls, subject_id, predicate_id, object_id):
        return cls(Entity(friends_namespace.term(subject_id), EntityType.FRIEND),
                   predicate_namespace.term(predicate_id),
                   Entity(friends_namespace.term(object_id), EntityType.FRIEND))


class Mention:
    def __init__(self, token_offset: OffsetSegment, phrase: str, referent: Union[Friend, Person, Object]):
        self.token_offset = token_offset
        self.phrase = phrase
        self.referent = referent


# TODO Does it makes sense to separate annotations
# TODO Annotations don't have timestamps
# TODO Annotations as nested attributes or with an ID referencing the signal
class FaceAnnotation:
    def __init__(self, person: Person, segment: Segment):
        self.person = person
        self.segment = segment


class UtteranceAnnotation:
    def __init__(self, chat_id: Union[uuid.UUID, str, None], utterance_id: [uuid.UUID, str, None], utterance: str,
                 tokens: Iterable[Tuple[(str, OffsetSegment)]], speaker: Friend, emotion: Emotion, mentions: Iterable[Mention]) -> None:
        self.chat_id = chat_id if chat_id else uuid.uuid4()
        self.utterance_id = utterance_id if utterance_id else uuid.uuid4()
        self.utterance = utterance
        self.tokens = tuple(tokens)
        self.speaker = FaceAnnotation(speaker, OffsetSegment(0, len(self.tokens)))
        self.mentions = tuple(mentions)
        self.emotion = emotion


class Signal:
    def __init__(self, id: Union[uuid.UUID, str, None], modality: Modality, time: TimeSegment, files: Iterable[str]) -> None:
        self.id = id if id else uuid.uuid4()
        self.modality = modality
        self.time = time
        # TODO multiple files: do we need to relate them to each other or the attributes to the files?
        self.files = files


class TextSignal(Signal):
    def __init__(self, id: Union[uuid.UUID, str, None], time: TimeSegment, files: Iterable[str],
                 utterances: Iterable[UtteranceAnnotation], triples: Iterable[Triple]):
        super().__init__(id, Modality.TEXT, time, files)
        self.utterances = utterances
        self.triples = triples


class ImageSignal(Signal):
    def __init__(self, id: Union[uuid.UUID, str, None], time: TimeSegment, files: Iterable[str], emotion: Emotion,
                 faces: Iterable[FaceAnnotation], speaker: FaceAnnotation) -> None:
        super().__init__(id, Modality.IMAGE, time, files)
        # TODO speaker and image should both have emotion?
        self.faces = faces
        self.speaker = speaker
        self.emotion = emotion


# TODO Audio Signal
class AudioSignal(Signal):
    def __init__(self, id: Union[uuid.UUID, str, None], time: TimeSegment, files: Iterable[str], speaker: FaceAnnotation) -> None:
        super().__init__(id, Modality.IMAGE, time, files)
        self.speaker = speaker

# TODO Video Signal
class VideoSignal(Signal):
    def __init__(self, id: Union[uuid.UUID, str, None], time: TimeSegment, files: Iterable[str], speaker: FaceAnnotation) -> None:
        super().__init__(id, Modality.IMAGE, time, files)
        self.speaker = speaker


# TODO Should be dynamic or static, should be a Chat instead?
class ScenarioContext:
    def __init__(self, agent: Union[uuid.UUID, str], speaker: Person, persons: Iterable[Person], objects: Iterable[Object]) -> None:
        self.agent = agent
        self.speaker = speaker
        self.persons = persons
        self.objects = objects


# TODO Location -> Spatial container?
class Scenario:
    def __init__(self, id: Union[uuid.UUID, str, None], time: TimeSegment, context: ScenarioContext, signals: Dict[Modality, str]) -> None:
        self.id = id
        self.time = time
        self.context = context
        self.signals = signals


# TODO Just a list or with some structure, e.g. relate the ruler in the file (dict: time -> event)
def append_signal(path: str, signal: object, terminate: bool=False, indent=4):
    os.makedirs(os.path.dirname(path), exist_ok=True)

    initialize = not os.path.isfile(path)
    with open(path, "a") as signal_file:
        if initialize:
            signal_file.write("[\n")
        if signal:
            json.dump(signal, signal_file, default=serializer, indent=indent)
            signal_file.write(",\n")
        if terminate:
            signal_file.write("]")


def serializer(object):
    if isinstance(object, enum.Enum):
        return object.name
    if isinstance(object, (URIRef, uuid.UUID)):
        return str(object)

    return vars(object)
