"""Peafowl Dox - Document processing utilities."""

from .core.image_utils import multipart_to_array, resize_image, prepare_for_ocr
from .core.pdf_converter import pdf_to_images
from .core.image_processor import ImageProcessor
from .exceptions import PeafowlDoxError, ImageProcessingError, PDFConversionError

__version__ = "0.1.0"
__all__ = [
    "multipart_to_array",
    "resize_image", 
    "prepare_for_ocr",
    "pdf_to_images",
    "ImageProcessor",
    "PeafowlDoxError",
    "ImageProcessingError", 
    "PDFConversionError"
]
