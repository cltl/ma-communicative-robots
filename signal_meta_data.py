# Define Annotation Class
import enum
import json
import uuid
import numpy as np
from typing import Iterable, Sequence, Tuple, Generic, TypeVar, Union, Dict

from rdflib import URIRef, Namespace

friends_namespace = Namespace("http://cltl.nl/leolani/friends/")
data_namespace = Namespace("http://cltl.nl/combot/signal/")
# TODO reference ontolgoy
predicate_namespace = Namespace("http://cltl.nl/combot/predicate/")


T = TypeVar("T")


class EntityType(enum.Enum):
    PERSON = 0
    FRIEND = 1
    OBJECT = 2


class Modality(enum.Enum):
    IMAGE = 0
    TEXT = 1
    AUDIO = 2


class Emotion(enum.Enum):
    ANGER = 0
    DISGUST = 1
    FEAR = 2
    HAPPINESS = 3
    JOY = 4
    SADNESS = 5
    SURPRISE = 6


class Gender(enum.Enum):
    UNDEFINED = 0
    FEMALE = 1
    MALE = 2
    OTHER = 3


class Segment(Generic[T]):
    # TODO This is not relevant for the data representation, but it would be nice if we could relate segment to a ruler/container type
    """Base class of segments that allow to identify a segment relative to a ruler in a signal"""
    def extract(self, signal: T) -> T:
        """
        Extract this segment specified from the provided signal.

        Parameters
        ----------
        signal : object
        The base signal the segement refers to.
        """
        raise NotImplementedError


class OffsetSegment(Segment[Sequence]):
    def __init__(self, start: int, end: int) -> None:
        self.offset = (start, end)

    @property
    def start(self):
        return self.offset[0]

    @property
    def end(self):
        return self.offset[1]

    def extract(self, sequence: Sequence):
        return sequence[self.start:self.end]


class BoundingBoxSegment(Segment[np.array]):
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

    def extract(self, image: np.array):
        return image[self.x_min:self.y_max,self.y_min:self.y_max]

# TODO see comment on Segment
class TemporalContainer:
    def extract(self, start: int, end: int):
        pass


class TimeSegment(Segment[TemporalContainer]):
    def __init__(self, start: int, end: int) -> None:
        self.end = end
        self.start = start

    def extract(self, container: TemporalContainer):
        return container.extract(self.start, self.end)


# TODO do we need that?
class Object:
    pass


class Person:
    def __init__(self, id: Union[uuid.UUID, None], name: str, age: int, gender: Gender, emotion: Emotion):
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


class SpeakerAnnotation(Generic[T]):
    def __init__(self, person: Person, segment: Segment[T]):
        self.person = person
        self.segment = segment


# Does it makes sense to separate annotations
class UtteranceAnnotation:
    def __init__(self, chat_id: Union[uuid.UUID, None], utterance_id: [uuid.UUID, None], utterance: str,
                 tokens: Iterable[Tuple[(str, OffsetSegment)]], speaker: Friend, emotion: Emotion, mentions: Iterable[Mention]) -> None:
        self.chat_id = chat_id if chat_id else uuid.uuid4()
        self.utterance_id = utterance_id if utterance_id else uuid.uuid4()
        self.utterance = utterance
        self.tokens = tuple(tokens)
        self.speaker = SpeakerAnnotation(speaker, OffsetSegment(0, len(self.tokens)))
        self.mentions = tuple(mentions)
        self.emotion = emotion


class Signal(TemporalContainer):
    def __init__(self, id: Union[uuid.UUID, None], modality: Modality, time: TimeSegment, files: Iterable[str]) -> None:
        self.id = id if id else uuid.uuid4()
        self.modality = modality
        self.time = time
        # TODO multiple files?
        self.files = files


class TextSignal(Signal):
    def __init__(self, id: Union[uuid.UUID, None], time: TimeSegment, files: Iterable[str],
                 utterances: Iterable[UtteranceAnnotation], triples: Iterable[Triple]):
        super().__init__(id, Modality.TEXT, time, files)
        self.utterances = utterances
        self.triples = triples


class ImageSignal(Signal):
    def __init__(self, id: Union[uuid.UUID, None], time: TimeSegment, files: Iterable[str], emotion: Emotion, speaker: SpeakerAnnotation) -> None:
        super().__init__(id, Modality.IMAGE, time, files)
        # TODO speaker and image should have emotion?
        self.speaker = speaker
        self.emotion = emotion


# TODO
class AudioSignal(Signal):
    def __init__(self, id: Union[uuid.UUID, None], time: TimeSegment, files: Iterable[str], speaker: SpeakerAnnotation) -> None:
        super().__init__(id, Modality.IMAGE, time, files)
        self.speaker = speaker


# TODO Scenario and signal "container"
class Scenario(TemporalContainer):
    def __init__(self, id: uuid.UUID, start: int, end: int, signals: Dict[str, str]) -> None:
        pass


def serializer(object):
    if isinstance(object, enum.Enum):
        return object.name
    if isinstance(object, (URIRef, uuid.UUID)):
        return str(object)

    return vars(object)


if __name__ == '__main__':
    piek = Friend(uuid.uuid4(), "Piek", 60, Gender.MALE)
    speaker = SpeakerAnnotation(piek, BoundingBoxSegment(0,0,1,1))
    image_signal = ImageSignal(uuid.uuid4(), TimeSegment(0, 2), [], Emotion.HAPPINESS, speaker)
    print(json.dumps(image_signal, default=serializer, indent=4))
