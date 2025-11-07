from dataclasses import dataclass


@dataclass
class BaseBoundingBox:
    """Base class for a bounding box with position and size.

    Attributes:
        position: The position of the bounding box, proportional to the full image width and height.
        width: The width of the bounding box.
        height: The height of the bounding box.
        confidence: The confidence of the detected item (OCR/Object/Face).
    """

    # position, width, height are proportional to full image width/height
    position: tuple[float, float]
    width: float
    height: float
    confidence: float
