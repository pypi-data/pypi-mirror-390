from dataclasses import dataclass
from enum import StrEnum, auto
from typing import Protocol

from PIL.Image import Image

from ruurd_photos_ml.analysis.base_model import BaseBoundingBox


class FacialRecognitionProtocol(Protocol):
    """Protocol for facial recognition."""

    def get_faces(self, image: Image) -> list["FaceBox"]:
        """Detect and embed faces from an image.

        Args:
            image: The image to get the faces from.

        Returns:
            The face boxes.
        """


class FacialRecognitionProvider(StrEnum):
    """Facial recognition providers enum."""

    INSIGHT = auto()


class FaceSex(StrEnum):
    """Enum for sex of the detected person."""

    MALE = "M"
    FEMALE = "F"


@dataclass
class FaceBox(BaseBoundingBox):
    """Represents a face bounding box with facial attributes.

    Attributes:
        age: The estimated age of the person.
        sex: The gender of the person.
        mouth_left: The position of the left mouth corner.
        mouth_right: The position of the right mouth corner.
        nose_tip: The position of the nose tip.
        eye_left: The position of the left eye.
        eye_right: The position of the right eye.
        embedding: The facial embedding vector.
    """

    age: int
    sex: FaceSex
    mouth_left: tuple[float, float]
    mouth_right: tuple[float, float]
    nose_tip: tuple[float, float]
    eye_left: tuple[float, float]
    eye_right: tuple[float, float]
    embedding: list[float]
