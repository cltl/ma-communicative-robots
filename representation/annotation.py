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


class ImageLabel(enum.Enum):
    FACE = 0


class EntityType(enum.Enum):
    PERSON = 0
    FRIEND = 1
    OBJECT = 2


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
    def from_friends(cls, subject_id, predicate_id, object_id) -> Triple:
        return cls(Entity(friends_namespace.term(subject_id), EntityType.FRIEND),
                   predicate_namespace.term(predicate_id),
                   Entity(friends_namespace.term(object_id), EntityType.FRIEND))


class Token(AtomicContainer):
    def __init__(self, value: str) -> None:
        AtomicContainer.__init__(self, value)


class Utterance(Sequence):
    def __init__(self, chat_id: Identifier, utterance: str, tokens: Iterable[Token], id_: Identifier = None) -> None:
        self.chat_id = chat_id if chat_id else uuid.uuid4()
        self.utterance = utterance
        Sequence.__init__(self, tuple(tokens))
