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

from signal_meta_data import Object, BoundingBoxSegment, Person, SpeakerAnnotation, TimeSegment, \
    ImageSignal, TextSignal, UtteranceAnnotation, Triple, Entity, Scenario

TOPIC_ON_CHAT_ENTER = "pepper.framework.context.topic.chat_enter"
TOPIC_ON_CHAT_TURN = "pepper.framework.context.topic.chat_turn"
TOPIC_ON_CHAT_EXIT = "pepper.framework.context.topic.chat_exit"

TOPIC_FACE = "pepper.framework.sensor.api.face_detector.topic"
TOPIC_FACE_NEW = "pepper.framework.sensor.api.face_detector.topic.new"
TOPIC_FACE_KNOWN = "pepper.framework.sensor.api.face_detector.topic.known"


class Event:
    def __init__(self, payload, metadata):
        self.payload = payload
        self.metadata = metadata


def convert_context(scenario: Scenario) -> LeolaniContext:
    leolani_context = LeolaniContext(scenario.id, convert(scenario.context.persons))
    leolani_context.add_objects(convert(scenario.context.objects))

    return leolani_context


def convert_person(person: Person) -> str:
    # TODO Person in Leolani is currently just a name, we should give it an ID
    return person.name


def convert_speaker(speaker: SpeakerAnnotation) -> str:
    return speaker.person.name


def convert_speaker_from_image(speaker: SpeakerAnnotation, image_path: str, time: TimeSegment) -> LeolaniFace:
    # TODO Representation of the face (image)
    representation = None
    # TODO Emotion?
    return LeolaniFace(speaker.person.name, 1.0, representation, convert(speaker.segment), convert_image(image_path, speaker.segment, time))


def read_image(path):
    image = Image.open(path)
    return np.asarray(image)


def convert_image(path: str, bounding_box: BoundingBoxSegment, time: TimeSegment) -> AbstractImage:
    image_array = read_image(path)
    return AbstractImage(image_array, convert(bounding_box), np.array(()), time.start)


# TODO Object class is just a dummy
def convert_object(obj: Object) -> LeolaniObject:
    return LeolaniObject(object.id, 1.0, convert(obj.bounding_box))


def convert_bounding_box(bounding_box: BoundingBoxSegment):
    return LeolaniBounds(*bounding_box.bounding_box)


def convert_entity(entity: Entity) -> dict:
    return {"label": str(entity.id), "type": entity.type.name.lower()}


def convert_predicate(predicate: URIRef) -> dict:
    return {"type": str(predicate)}


def convert_triple(triple: Triple) -> LeolaniTriple:
    builder = RdfBuilder()

    subject = convert(triple.subject)
    predicate = convert_predicate(triple.predicate)
    obj = convert(triple.object)

    return builder.fill_triple(subject, predicate, obj)


# TODO we could directly add to the context here, but that would not make it available to intentions
def integrate_image_signal(signal: ImageSignal) -> Tuple[Event]:
    # Convert annotation from Face recognition to event payload
    speaker = signal.speaker
    time = signal.time
    img_path = signal.files[0]


    # TODO Convert annotation from Object recognition to event payload
    return ((TOPIC_FACE, Event(convert_speaker_from_image(speaker, img_path, time), None)),)


def integrate_text_signal(signal: TextSignal, context: LeolaniContext) -> Tuple[Tuple[Tuple[(str, Event)]], Tuple[LeolaniTriple]]:
    events = tuple(ev for utt in signal.utterances for ev in integrate_utterance(utt, context))

    triples = convert(signal.triples)

    return events, triples


def integrate_utterance(utterance: UtteranceAnnotation, context: LeolaniContext) -> Tuple[Tuple[(str, Event)]]:
    events: Tuple[Tuple[(str, Event)]] = ()

    speaker = utterance.speaker
    chat_id = utterance.chat_id

    # TODO Leolani will do its own NLP processing
    # utterance.tokens
    # utterance.metions
    utterance_hypothesis = UtteranceHypothesis(utterance.utterance, 1.0)

    if context.chatting and context.chat.id != chat_id:
        context.stop_chat()
        events += ((TOPIC_ON_CHAT_EXIT, Event(None, None)),)

    if not context.chatting:
        # TODO Leolani doesn't support setting chat id and time
        context.start_chat(speaker.person.name)
        events += ((TOPIC_ON_CHAT_ENTER, Event(speaker.person.name, None)),)

    context.chat.add_utterance([utterance_hypothesis], False)
    events += ((TOPIC_ON_CHAT_TURN, Event(utterance_hypothesis, None)),)

    # TODO emotion
    # utterance.emotion

    # On chat turn event payload
    return events


def convert_utterance(utterance: UtteranceAnnotation, context: LeolaniContext) -> LeolaniUtterance:
    chat = LeolaniChat(utterance.speaker.person.name, context)

    hyp = UtteranceHypothesis(utterance.utterance, 0.99)

    leolani_utterance = LeolaniUtterance(chat, [hyp], False, -1)
    leolani_utterance._type = UtteranceType.STATEMENT

    leolani_utterance.pack_perspective({"certainty": 0.5, "polarity": 1, "sentiment": 0})

    return leolani_utterance


def convert(obj: object):
    if isinstance(obj, (str, int, float, bool)):
        return obj
    if isinstance(obj, (list, tuple)):
        return tuple(convert(o) for o in obj)
    if isinstance(obj, Scenario):
        return convert_context(obj)
    if isinstance(obj, Object):
        return convert_object(obj)
    if isinstance(obj, BoundingBoxSegment):
        return convert_bounding_box(obj)
    if isinstance(obj, SpeakerAnnotation):
        return convert_speaker(obj)
    if isinstance(obj, Person):
        return convert_person(obj)
    if isinstance(obj, Entity):
        return convert_entity(obj)
    if isinstance(obj, Triple):
        return convert_triple(obj)


if __name__ == "__main__":
    print(convert_bounding_box(BoundingBoxSegment(0,1,2,3)))