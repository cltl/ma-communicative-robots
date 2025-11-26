from __future__ import annotations

import abc
import enum
import logging
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Iterable, Optional, Tuple, List

import numpy as np

logger = logging.getLogger(__name__)

class Object:
    type: str
    label: str
    confidence: Optional[float]


def spherical2cartesian(phi: float, theta: float, depth: float) -> Tuple[float, float, float]:
    """
    Spherical Coordinates to Cartesian Coordinates
    """
    x = depth * np.sin(theta) * np.cos(phi)
    y = depth * np.cos(theta)
    z = depth * np.sin(theta) * np.sin(phi)

    return x, y, z

class CameraResolution(enum.Enum):
    """
    Image height and width.
    """
    NATIVE = -1, -1
    QQQQVGA = 30, 40
    QQQVGA = 60, 80
    QQVGA = 120, 160
    QVGA = 240, 320
    VGA = 480, 640
    VGA4 = 960, 1280

    @property
    def height(self):
        return self.value[0]

    @property
    def width(self):
        return self.value[1]

    @property
    def bounds(self):
        return Bounds(0, self.width, 0, self.height)


@dataclass
class Bounds:
    x0: float
    x1: float
    y0: float
    y1: float

    @classmethod
    def from_diagonal(cls, x0, y0, x1, y1):
        return cls(x0, x1, y0, y1)

    @property
    def width(self) -> float:

        return self.x1 - self.x0

    @property
    def height(self) -> float:

        return self.y1 - self.y0

    @property
    def center(self) -> (float, float):

        return self.x0 + self.width / 2, self.y0 + self.height / 2

    @property
    def area(self) -> float:

        return self.width * self.height

    def intersection(self, bounds: Bounds) -> Optional[Bounds]:

        x0 = max(self.x0, bounds.x0)
        y0 = max(self.y0, bounds.y0)
        x1 = min(self.x1, bounds.x1)
        y1 = min(self.y1, bounds.y1)

        return None if x0 >= x1 or y0 >= y1 else Bounds(x0, x1, y0, y1)

    def overlap(self, other: Bounds) -> float:

        intersection = self.intersection(other)

        if intersection:
            return min(intersection.area / self.area, self.area / intersection.area)
        else:
            return 0.0

    def is_subset_of(self, other: Bounds) -> bool:
        return self.x0 >= other.x0 and self.y0 >= other.y0 and self.x1 <= other.x1 and self.y1 <= other.y1

    def is_superset_of(self, other: Bounds) -> bool:
        return self.x0 <= other.x0 and self.y0 <= other.y0 and self.x1 >= other.x1 and self.y1 >= other.y1

    def contains(self, point: Tuple[float, float]) -> bool:
        x, y = point
        return self.x0 < x < self.x1 and self.y0 < y < self.y1

    def scaled(self, x_scale: float, y_scale: float) -> Bounds:
        return Bounds(self.x0 * x_scale, self.x1 * x_scale, self.y0 * y_scale, self.y1 * y_scale)

    def to_diagonal(self) -> Tuple[float, float, float, float]:
        return (self.x0, self.y0, self.x1, self.y1)


@dataclass
class Image:
    image: np.ndarray
    view: Tuple[float, float, float, float]
    depth: Optional[np.ndarray] = None

    @property
    def bounds(self) -> Bounds:
        return self.resolution.bounds

    @property
    def resolution(self) -> CameraResolution:
        try:
            return CameraResolution(self.image.shape[:2])
        except ValueError:
            return CameraResolution.NATIVE

    def get_section(self, bounds: Bounds) -> np.ndarray:

        x0 = int(bounds.x0 * self.image.shape[1])
        x1 = int(bounds.x1 * self.image.shape[1])
        y0 = int(bounds.y0 * self.image.shape[0])
        y1 = int(bounds.y1 * self.image.shape[0])

        return self.image[y0:y1, x0:x1]

    def get_depth(self, bounds: Bounds) -> Optional[np.ndarray]:

        if self.depth is None:
            return None

        x0 = int(bounds.x0 * self.depth.shape[1])
        x1 = int(bounds.x1 * self.depth.shape[1])
        y0 = int(bounds.y0 * self.depth.shape[0])
        y1 = int(bounds.y1 * self.depth.shape[0])

        return self.depth[y0:y1, x0:x1]

    def get_direction(self, coordinates: Tuple[float, float]) -> Tuple[float, float]:

        return (self.view.x0 + coordinates[0] * self.view.width,
                self.view.y0 + coordinates[1] * self.view.height)

    def frustum(self, depth_min: float, depth_max: float) -> np.ndarray:

        return np.array([
            # Near Viewing Plane
            [spherical2cartesian(self.view.x0, self.view.y0, depth_min),
            spherical2cartesian(self.view.x0, self.view.y1, depth_min),
            spherical2cartesian(self.view.x1, self.view.y1, depth_min),
            spherical2cartesian(self.view.x1, self.view.y0, depth_min)],

            # Far Viewing Plane
            [spherical2cartesian(self.view.x0, self.view.y0, depth_max),
            spherical2cartesian(self.view.x0, self.view.y1, depth_max),
            spherical2cartesian(self.view.x1, self.view.y1, depth_max),
            spherical2cartesian(self.view.x1, self.view.y0, depth_max)]
        ])


class Camera(abc.ABC):
    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

    def start(self):
        pass

    def stop(self):
        pass

    @property
    def rate(self) -> float:
        """Rate of the camera recording.
            Images per seconds recorded by the Camera.

            If a negative rate is returned, only capturing images is supported,
            if a zero is returned, the camera will record at the maximum available rate.
        """
        raise NotImplementedError()

    @property
    def resolution(self) -> CameraResolution:
        raise NotImplementedError()

    @contextmanager
    def capture(self) -> Image:
        raise NotImplementedError()

    @contextmanager
    def record(self) -> Iterable[Image]:
        raise NotImplementedError()

    def stop_recording(self):
        raise NotImplementedError()

    @property
    def is_recording(self) -> bool:
        raise NotImplementedError()
