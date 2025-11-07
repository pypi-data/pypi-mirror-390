"""Protocol / interface for OCR."""

from dataclasses import dataclass
from enum import StrEnum, auto
from typing import Protocol

from PIL.Image import Image

from ruurd_photos_ml.analysis.base_model import BaseBoundingBox


class OCRProtocol(Protocol):
    """Protocol for OCR."""

    def has_legible_text(self, image: Image) -> bool:
        """Check if an image has legible text."""

    def get_text(self, image: Image, languages: tuple[str, ...]) -> str:
        """Extract text from an image using OCR."""

    def get_boxes(self, image: Image, languages: tuple[str, ...]) -> list["OCRBox"]:
        """Get bounding boxes of text."""


class OCRProvider(StrEnum):
    """OCR providers enum."""

    RESNET_TESSERACT = auto()


@dataclass
class OCRBox(BaseBoundingBox):
    """Represents a bounding box for OCR with text content.

    Attributes:
        text: The recognized text within the bounding box.
    """

    text: str
