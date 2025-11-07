from dataclasses import dataclass
from enum import StrEnum, auto
from typing import Protocol

from PIL.Image import Image

from ruurd_photos_ml.analysis.base_model import BaseBoundingBox


class ObjectDetectionProtocol(Protocol):
    """Protocol for object detection."""

    def detect_objects(self, image: Image) -> list["ObjectBox"]:
        """Check if an image has legible text."""


class ObjectDetectionProvider(StrEnum):
    """Object detection providers enum."""

    RESNET = auto()


@dataclass
class ObjectBox(BaseBoundingBox):
    """Represents an object bounding box with a label.

    Attributes:
        label: The label of the detected object.
    """

    label: str
