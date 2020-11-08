# Define Annotation Class
import enum
from datetime import date

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
        ### in GRaSP instances have a list of mentions which are all the segments that have been annotated with "reference" to this mention, these all get the grasp:denotedBy relation
        ### Do we want to do the same thing here? This would be a reverse index of (a subset of) the annotations.


class Object(Instance):
    def __init__(self, id: Identifier, label: str):
        super().__init__(id)
        self.label = label


class Person(Instance):
    def __init__(self, id: Identifier, name: str, age: int, gender: Gender, emotion: Emotion):
        super().__init__(id)
        self.name = name  # this could be a list of names
        #self.pronoun = pronoun # this could be a list of pronouns
        self.age = age # this should be changed to day of birth
        self.gender = gender
        self.emotion = emotion


class Friend(Person):
    pass
