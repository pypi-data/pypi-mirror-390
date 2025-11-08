"""Peafowl Dox - Document processing utilities."""

from .core.image_utils import multipart_to_array, resize_image, preprocess_image
from .core.pdf_converter import pdf_to_images
from .core.document_processor import DocumentProcessor
from .exceptions import PeafowlDoxError, ImageProcessingError, PDFConversionError

__version__ = "0.2.0"
__all__ = [
    "multipart_to_array",
    "resize_image", 
    "preprocess_image",
    "pdf_to_images",
    "DocumentProcessor",
    "PeafowlDoxError",
    "ImageProcessingError", 
    "PDFConversionError"
]
