from ruurd_photos_ml.analysis.caption.instruct_blip_captioner import (
    InstructBlipCaptioner,
)
from ruurd_photos_ml.analysis.caption.protocol import (
    CaptionerProtocol,
    CaptionerProvider,
)
from ruurd_photos_ml.analysis.caption.sf_blip_captioner import SfBlipCaptioner
from ruurd_photos_ml.analysis.embedding.open_clip_embedder import OpenCLIPEmbedder
from ruurd_photos_ml.analysis.embedding.protocol import EmbedderProtocol, EmbedderProvider
from ruurd_photos_ml.analysis.embedding.zero_clip_embedder import ZeroCLIPEmbedder
from ruurd_photos_ml.analysis.facial_recognition.insight_facial_recognition import (
    InsightFacialRecognition,
)
from ruurd_photos_ml.analysis.facial_recognition.protocol import (
    FacialRecognitionProtocol,
    FacialRecognitionProvider,
)
from ruurd_photos_ml.analysis.llm.gemma_llm import GemmaLLM
from ruurd_photos_ml.analysis.llm.protocol import LLMProtocol, LLMProvider
from ruurd_photos_ml.analysis.object_detection.protocol import (
    ObjectDetectionProtocol,
    ObjectDetectionProvider,
)
from ruurd_photos_ml.analysis.object_detection.resnet_object_detection import (
    ResnetObjectDetection,
)
from ruurd_photos_ml.analysis.ocr.protocol import OCRProtocol, OCRProvider
from ruurd_photos_ml.analysis.ocr.resnet_tesseract_ocr import ResnetTesseractOCR


def get_ocr(provider: OCRProvider = OCRProvider.RESNET_TESSERACT) -> OCRProtocol:
    """Get OCR implementation."""
    return {
        OCRProvider.RESNET_TESSERACT: ResnetTesseractOCR,
    }[provider]()


def get_object_detection(
    provider: ObjectDetectionProvider = ObjectDetectionProvider.RESNET,
) -> ObjectDetectionProtocol:
    """Get object detection implementation."""
    return {
        ObjectDetectionProvider.RESNET: ResnetObjectDetection,
    }[provider]()


def get_facial_recognition(
    provider: FacialRecognitionProvider = FacialRecognitionProvider.INSIGHT,
) -> FacialRecognitionProtocol:
    """Get facial recognition implementation."""
    return {
        FacialRecognitionProvider.INSIGHT: InsightFacialRecognition,
    }[provider]()


def get_captioner(
    provider: CaptionerProvider = CaptionerProvider.BLIP_INSTRUCT,
) -> CaptionerProtocol:
    """Get the captioner by the provider."""
    return {
        CaptionerProvider.SF_BLIP: SfBlipCaptioner,
        CaptionerProvider.BLIP_INSTRUCT: InstructBlipCaptioner,
    }[provider]()


def get_embedder(provider: EmbedderProvider = EmbedderProvider.OPEN_CLIP) -> EmbedderProtocol:
    """Get the LLM by the provider."""
    return {
        EmbedderProvider.OPEN_CLIP: OpenCLIPEmbedder,
        EmbedderProvider.ZERO_CLIP: ZeroCLIPEmbedder,
    }[provider]()


def get_llm(provider: LLMProvider = LLMProvider.GEMMA_3) -> LLMProtocol:
    """Get the LLM by the provider."""
    return {
        LLMProvider.GEMMA_3: GemmaLLM,
    }[provider]()
