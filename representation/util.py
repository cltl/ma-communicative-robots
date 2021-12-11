import enum

import numpy as np
import uuid
from rdflib import URIRef
from typing import Union


Identifier = Union[URIRef, uuid.UUID, str, None]


def serializer(object):
    if isinstance(object, enum.Enum):
        return object.name
    if isinstance(object, (URIRef, uuid.UUID)):
        return str(object)
    if isinstance(object, np.ndarray):
        return object.tolist()
    return vars(object)