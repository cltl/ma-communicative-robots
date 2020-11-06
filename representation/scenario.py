# Define Annotation Class
import enum
import os

import json
import uuid
from typing import Iterable, Union, Dict, Optional, Tuple, TypeVar

from representation.container import Container, TemporalContainer, Ruler, TemporalRuler, Sequence, ArrayContainer
from representation.entity import Person, Object
from representation.util import Identifier, serializer


class Modality(enum.Enum):
    IMAGE = 0
    TEXT = 1
    AUDIO = 2
    VIDEO = 3


class Mention:
    def __init__(self, segment: Union[Ruler, Iterable[Ruler]], referent: Optional[Identifier]=None):
        self.type = self.__class__.__name__
        self.segment = segment
        self.referent = referent


R = TypeVar('R', bound=Ruler)
T = TypeVar('T')
class Signal(Container[R, T]):
    def __init__(self, modality: Modality, time: TemporalRuler, files: Iterable[str],
                 mentions: Iterable[Mention]=None) -> None:
        self.modality = modality
        self.time = time
        # TODO multiple files: do we need to relate them to each other or the attributes to the files?
        self.files = files
        self.mentions = mentions if mentions is not None else []


class TextSignal(Signal[Sequence, str], Sequence[str]):
    def __init__(self, id_: Identifier, time: TemporalRuler, files: Iterable[str],
                 length, mentions: Iterable[Mention]=None):
        id_ = id_ if id_ else uuid.uuid4()
        Signal.__init__(self, Modality.TEXT, time, files, mentions)
        Sequence.__init__(self, id_=id_, stop=length)


class ImageSignal(Signal[ArrayContainer, float], ArrayContainer[float]):
    def __init__(self, id_: Identifier, time: TemporalRuler, files: Iterable[str],
                 bounds: Tuple[Tuple[int,int], ...], mentions: Iterable[Mention]=None) -> None:
        id_ = id_ if id_ else uuid.uuid4()
        Signal.__init__(self, Modality.IMAGE, time, files, mentions)
        ArrayContainer.__init__(self, id_=id_, bounds=bounds)


class AudioSignal(Signal[ArrayContainer, float], ArrayContainer[float]):
    def __init__(self, id_: Identifier, time: TemporalRuler, files: Iterable[str],
                 mentions: Iterable[Mention]=None) -> None:
        id_ = id_ if id_ else uuid.uuid4()
        Signal.__init__(self, Modality.AUDIO, time, files, mentions)
        ArrayContainer.__init__(self, id_=id_, bounds=None)


class VideoSignal(Signal[ArrayContainer, float], ArrayContainer[float]):
    def __init__(self, id_: Identifier, time: TemporalRuler, files: Iterable[str],
                 mentions: Iterable[Mention]=None) -> None:
        id_ = id_ if id_ else uuid.uuid4()
        Signal.__init__(self, Modality.VIDEO, time, files, mentions)
        ArrayContainer.__init__(self, id_=id_, bounds=None)


class ScenarioContext:
    def __init__(self, agent: Identifier, speaker: Person, persons: Iterable[Person], objects: Iterable[Object]) -> None:
        self.agent = agent
        self.speaker = speaker
        self.persons = persons
        self.objects = objects


class Scenario(TemporalContainer):
    def __init__(self, id_: Identifier, start: int, end: int, context: ScenarioContext, signals: Dict[Modality, str]) -> None:
        super().__init__(start, end, id_=id_)
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
