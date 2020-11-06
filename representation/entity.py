# Define Annotation Class
import enum

import uuid

from representation.util import Identifier


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


class Instance:
    def __init__(self, id: Identifier):
        self.id = id if id else uuid.uuid4()


# TODO do we need objects?
class Object(Instance):
    def __init__(self, id: Identifier, label: str):
        super().__init__(id)
        self.label = label


class Person(Instance):
    # TODO Should be identified by its properties not by an ID (though it should have an ID)?
    def __init__(self, id: Identifier, name: str, age: int, gender: Gender, emotion: Emotion):
        super().__init__(id)
        self.name = name
        self.age = age
        self.gender = gender
        self.emotion = emotion


# TODO do we need a Person?
class Friend(Person):
    pass
