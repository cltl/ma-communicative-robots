import numpy as np
from PIL import Image
from leolani.datarepresentation.interaction import Context as LeolaniContext
from leolani.datarepresentation.language import Chat as LeolaniChat
from leolani.datarepresentation.language import Utterance as LeolaniUtterance
from leolani.datarepresentation.language import UtteranceHypothesis, UtteranceType
from leolani.datarepresentation.rdf_builder import RdfBuilder
from leolani.datarepresentation.representation import Triple as LeolaniTriple
from leolani.datarepresentation.vision import Bounds as LeolaniBounds
from leolani.datarepresentation.vision import Face as LeolaniFace
from leolani.datarepresentation.vision import Object as LeolaniObject, AbstractImage
from rdflib import URIRef
from typing import Tuple

from signal_meta_data import Object, BoundingBoxSegment, Person, FaceAnnotation, TimeSegment, \
    ImageSignal, TextSignal, UtteranceAnnotation, Triple, Entity, Scenario, Gender, Emotion

TOPIC_ON_CHAT_ENTER = "pepper.framework.context.topic.chat_enter"
TOPIC_ON_CHAT_TURN = "pepper.framework.context.topic.chat_turn"
TOPIC_ON_CHAT_EXIT = "pepper.framework.context.topic.chat_exit"

TOPIC_FACE = "pepper.framework.sensor.api.face_detector.topic"
TOPIC_FACE_NEW = "pepper.framework.sensor.api.face_detector.topic.new"
TOPIC_FACE_KNOWN = "pepper.framework.sensor.api.face_detector.topic.known"


def convert_context(context: LeolaniContext) -> Scenario:
    time = TimeSegment(max(utt.datetime for utt in context.chat.utterances),
                       min(utt.datetime for utt in context.chat.utterances))

    return Scenario(convert(context.id), time, convert(context.friends), context(context.objects))


def convert_person(person: Person) -> str:
    # TODO Person in Leolani is currently just a name, we should give it an ID
    return person.name


def convert_speaker(face: LeolaniFace) -> FaceAnnotation:
    name = face.name
    bounds = face.bounds

    person = Person(name, name, None, Gender.UNDEFINED, Emotion.NEUTRAL)

    # TODO image is not persisted in Leolani -> collect different annotations for the same image
    # -> Add signal id(s) to event metadata and group event stream by signal id
    time = TimeSegment(int(face.time), int(face.time))
    image = face.image

    return FaceAnnotation(person, convert(bounds))