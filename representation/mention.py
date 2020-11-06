# Define Annotation Class
from __future__ import annotations
import enum

import uuid
from rdflib import URIRef, Namespace
from typing import Iterable, Tuple, Generic, TypeVar

from representation.container import Sequence, AtomicContainer, Ruler, Index
from representation.entity import Person, Emotion
from representation.scenario import Mention, Annotation
from representation.util import Identifier


friends_namespace = Namespace("http://cltl.nl/leolani/friends/")
data_namespace = Namespace("http://cltl.nl/combot/signal/")
predicate_namespace = Namespace("http://cltl.nl/combot/predicate/")


class EntityType(enum.Enum):
    PERSON = 0
    FRIEND = 1
    OBJECT = 2


class Entity:
    def __init__(self, id: URIRef, type: EntityType) -> None:
        self.id = id
        self.type = type


class Triple(Annotation):
    def __init__(self, segment: Tuple[Ruler, Ruler, Ruler], subject: Entity, predicate: URIRef, object_: Entity,
                 source: Identifier, timestamp: int) -> None:
        super().__init__(segment, source, timestamp)
        self.subject = subject
        self.predicate = predicate
        self.object = object_

    # TODO make this more generic
    @classmethod
    def from_friends(cls, segment: Tuple[Ruler, Ruler, Ruler], subject_id, predicate_id, object_id,
                     source: Identifier, timestamp: int) -> Triple:
        return cls(segment, Entity(friends_namespace.term(subject_id), EntityType.FRIEND),
                   predicate_namespace.term(predicate_id),
                   Entity(friends_namespace.term(object_id), EntityType.FRIEND),
                   source, timestamp)


T = TypeVar('T')
class FaceAnnotation(Generic[T], Annotation):
    def __init__(self, segment: T, source: Identifier, timestamp: int):
        super().__init__(segment, source, timestamp)


class PersonAnnotation(Generic[T], Annotation):
    def __init__(self, person: Person, segment: T, source: Identifier, timestamp: int):
        super().__init__(segment, source, timestamp)
        self.person = person


class Token(Annotation, AtomicContainer):
    def __init__(self, value: str, offset: Index, source: Identifier, timestamp: int) -> None:
        Annotation.__init__(self, offset, source, timestamp)
        AtomicContainer.__init__(self, value)


class UtteranceAnnotation(Annotation, Sequence):
    def __init__(self, id_: Identifier, chat_id: Identifier, utterance: str, tokens: Iterable[Token],
                 speaker: Person, emotion: Emotion, source: Identifier, timestamp: int) -> None:
        self.chat_id = chat_id if chat_id else uuid.uuid4()
        self.utterance = utterance
        self.emotion = emotion
        Annotation.__init__(self, tuple(t.ruler for t in tokens), source, timestamp)
        Sequence.__init__(self, tuple(tokens))
