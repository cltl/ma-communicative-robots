# Define Annotation Class
import enum

import uuid
from rdflib import URIRef, Namespace
from typing import Iterable, Tuple, Generic, TypeVar

from representation.container import Sequence, AtomicContainer, Ruler, Index
from representation.entity import Person, Emotion
from representation.scenario import Mention
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


class Triple(Mention):
    def __init__(self, segment: Tuple[Ruler, Ruler, Ruler], subject: Entity, predicate: URIRef, object_: Entity) -> None:
        super().__init__(segment)
        self.subject = subject
        self.predicate = predicate
        self.object = object_

    # TODO make this more generic
    @classmethod
    def from_friends(cls, segment: Tuple[Ruler, Ruler, Ruler], subject_id, predicate_id, object_id):
        return cls(segment, Entity(friends_namespace.term(subject_id), EntityType.FRIEND),
                   predicate_namespace.term(predicate_id),
                   Entity(friends_namespace.term(object_id), EntityType.FRIEND))


# TODO Annotations don't have timestamps
T = TypeVar('T')
class FaceAnnotation(Generic[T], Mention):
    def __init__(self, segment: T):
        super().__init__(segment)


class PersonAnnotation(Generic[T], Mention):
    def __init__(self, person: Person, segment: T):
        super().__init__(segment, person.id)
        self.person = person


class Token(Mention, AtomicContainer):
    def __init__(self, value: str, offset: Index) -> None:
        Mention.__init__(self, offset)
        AtomicContainer.__init__(self, value)


class UtteranceAnnotation(Mention, Sequence):
    def __init__(self, id_: Identifier, chat_id: Identifier, utterance: str, tokens: Iterable[Token],
                 speaker: Person, emotion: Emotion) -> None:
        self.chat_id = chat_id if chat_id else uuid.uuid4()
        self.utterance = utterance
        self.emotion = emotion
        Mention.__init__(self, tuple(t.ruler for t in tokens), speaker.id)
        Sequence.__init__(self, tuple(tokens))
