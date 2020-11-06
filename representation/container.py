# Define Annotation Class
from __future__ import annotations

import json
import numpy as np
import uuid
from typing import Union, TypeVar, Generic, Iterable, Tuple

from representation.util import serializer, Identifier


class Ruler:
    """Base type of Rulers that allow to identify a segment relative to a ruler in a signal"""
    def __init__(self, container_id: Identifier):
        self.type = self.__class__.__name__
        self.container_id = container_id


R = TypeVar('R', bound=Ruler)
T = TypeVar('T')
class Container(Generic[R, T]):
    """Base class of segments that allow to identify a segment relative to a ruler in a signal"""
    def __getitem__(self, segment: R) -> T:
        raise NotImplementedError()


class BaseContainer(Container[R, T]):
    """Base class of segments that allow to identify a segment relative to a ruler in a signal"""

    def __init__(self, id_: Identifier, ruler: R) -> None:
        self.id = id_
        self.ruler = ruler


class Index(Ruler):
    def __init__(self, container_id: Identifier, start: int, stop: int):
        super().__init__(container_id)
        self.start = start
        self.stop = stop

    def get_offset(self, start: int, end: int) -> Index:
        if start < self.start or end > self.stop:
            raise ValueError("start and end must be within [{}, {}), was [{}, {})".format(self.start, self.stop, start, end))

        return Index(self.container_id, start, end)


class Sequence(BaseContainer[Index, T]):
    def __init__(self, seq: Iterable[T] = None, id_: Identifier = None, start=0, stop=None) -> None:
        self.seq = tuple(seq) if seq is not None else None
        id_ = id_ if id_ else uuid.uuid4()
        super().__init__(id_, Index(id_, start, stop if stop is not None else len(self.seq)))

    def __getitem__(self, offset: Index) -> T:
        return self.seq[offset.start:offset.stop]


class MultiIndex(Ruler):
    def __init__(self, container_id: Identifier, bounds: Tuple[Tuple[int,int], ...]) -> None:
        super().__init__(container_id)
        if len(bounds) < 2:
            raise ValueError("MultiIndex must have at least two dimensions, was " + str(len(bounds)))
        self.bounds = bounds

    def get_area_bounding_box(self, x_min: int, y_min: int, x_max: int, y_max: int) -> MultiIndex:
        if x_min < self.bounds[0][0] or x_max >= self.bounds[0][1] \
                or y_min < self.bounds[1][0] or y_max >= self.bounds[1][1]:
            raise ValueError("start and end must be within [%s, %s), was " + str(self.bounds))

        return MultiIndex(self.container_id, ((x_min, x_max), (y_min, y_max)) + self.bounds[2:])


class ArrayContainer(BaseContainer[MultiIndex, T]):
    def __init__(self, array: Union[tuple, list, np.ndarray] = None, id_: Identifier = None,
                 bounds: Tuple[Tuple[int,int], ...] = None) -> None:
        self.array = np.array(array) if array is not None else None
        id_ = id_ if id_ else uuid.uuid4()
        bounds = bounds if bounds else tuple((0, upper) for upper in array.shape)
        super().__init__(id_, MultiIndex(id_, bounds))

    def __getitem__(self, bounding_box: MultiIndex) -> T:
        return self.array[tuple(slice(b[0], b[1], 1) for b in bounding_box.bounds)]


class TemporalRuler(Ruler):
    def __init__(self, container_id: Identifier, start: int, end: int) -> None:
        super().__init__(container_id)
        self.start = start
        self.end = end

    def get_time_segment(self, start: int, end: int) -> TemporalRuler:
        if start < self.start or end >= self.end:
            raise ValueError("start and end must be within [%s, %s), was [%s, %s)".format(self.start, self.end, start, end))

        return TemporalRuler(self.container_id, start, end)


class TemporalContainer(BaseContainer[TemporalRuler, TemporalRuler]):
    def __init__(self, start: int, end: int, id_: Identifier = None) -> None:
        id_ = id_ if id_ else uuid.uuid4()
        self.start_date = start
        self.end_date = end
        super().__init__(id_, TemporalRuler(id_, start, end))

    def __getitem__(self, segment: TemporalRuler) -> TemporalRuler:
        return segment


class AtomicRuler(Ruler):
    pass


class AtomicContainer(BaseContainer[AtomicRuler, T]):
    def __init__(self, value: T, id_: Identifier = None) -> None:
        self.value = value
        id_ = id_ if id_ else uuid.uuid4()
        super().__init__(id_, AtomicRuler(id_))

    def __getitem__(self, segment: AtomicRuler) -> T:
        if not segment.container_id == self.id:
            raise ValueError("Invalid segment")

        return self.value


if __name__ == "__main__":
    from pprint import pprint

    tokens = Sequence(["I", "am", "in", "Amsterdam"])
    token_offset = tokens.ruler.get_offset(0, 1)
    token_segment = tokens[token_offset]
    pprint(token_segment)
    print(json.dumps(tokens, default=serializer, indent=2))

    array = ArrayContainer(np.zeros((5,5,3), dtype=int))
    bbox = array.ruler.get_area_bounding_box(0,0,2,2)
    area = array[bbox]
    pprint(area)
    print(json.dumps(array, default=serializer, indent=2))

    period = TemporalContainer(0, 1000)
    time_segment = period.ruler.get_time_segment(10,100)
    sub_period = period[time_segment]
    print(sub_period)
    print(json.dumps(period, default=serializer, indent=2))