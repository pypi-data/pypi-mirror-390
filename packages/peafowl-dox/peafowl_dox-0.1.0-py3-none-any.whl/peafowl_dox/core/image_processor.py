"""Enhanced image processor with OCR preparation capabilities."""

import os
import logging
from typing import Union

import cv2
import numpy as np

from ..exceptions import ImageProcessingError
from .image_utils import prepare_for_ocr


logger = logging.getLogger(__name__)

class ImageProcessor:
    """Enhanced image processor for document processing workflows.
    
    This processor handles image loading from multiple sources (file paths, bytes, arrays)
    and provides OCR-optimized preprocessing capabilities.
    
    Attributes:
        default_ocr_size: Default target size for OCR preprocessing. Can be an int (width) 
            or tuple (width, height).
    """
    
    def __init__(self, default_ocr_size: Union[int, tuple] = 1200):
        """Initialize processor with default settings.
        
        Args:
            default_ocr_size: Default target size for OCR operations. If int, represents
                maximum width while preserving aspect ratio. If tuple, represents (width, height).
                Defaults to 1200.
        """
        self.default_ocr_size = default_ocr_size
    
    def _prepare_image_from_path(self, img_path: str) -> np.ndarray:
        """Load image from file path and convert to RGB.
        
        Strategy: Validates file existence and permissions before attempting to load,
        providing specific error messages for common failure modes.
        
        Args:
            img_path: Path to the image file.
            
        Returns:
            RGB image array with shape (height, width, 3) and dtype uint8.
            
        Raises:
            FileNotFoundError: If the image file doesn't exist.
            PermissionError: If the file cannot be read due to permissions.
            ImageProcessingError: If the image cannot be loaded or converted.
        """
        try:
            if not os.path.exists(img_path):
                raise FileNotFoundError(f"Image file not found: '{img_path}'")
            
            if not os.access(img_path, os.R_OK):
                raise PermissionError(f"Cannot read image file: '{img_path}'")
            
            img_bgr = cv2.imread(img_path)
            
            if img_bgr is None:
                raise ImageProcessingError(f"Image at path '{img_path}' could not be loaded.")
            
            # OpenCV loads as BGR, convert to RGB for consistency
            img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
            return img_rgb
            
        except cv2.error as e:
            logger.error(f"OpenCV error while loading image from path: {e}")
            raise ImageProcessingError(f"OpenCV error processing '{img_path}': {str(e)}") from e
        except (FileNotFoundError, PermissionError):
            raise
        except Exception as e:
            logger.error(f"Unexpected error loading image from path: {e}")
            raise ImageProcessingError(f"Failed to load image from '{img_path}': {str(e)}") from e

    def _prepare_image_from_bytes(self, img_bytes: bytes) -> np.ndarray:
        """Convert image bytes to RGB format.
        
        Strategy: Uses OpenCV's imdecode to handle various image formats encoded as bytes.
        
        Args:
            img_bytes: Image data as bytes.
            
        Returns:
            RGB image array with shape (height, width, 3) and dtype uint8.
            
        Raises:
            ImageProcessingError: If bytes cannot be decoded or converted.
        """
        try:
            nparr = np.frombuffer(img_bytes, np.uint8)
            img_bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if img_bgr is None:
                raise ImageProcessingError("Image bytes could not be decoded.")
            
            # Convert BGR to RGB for consistency
            img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
            return img_rgb
            
        except cv2.error as e:
            logger.error(f"OpenCV error while converting image bytes: {e}")
            raise ImageProcessingError(f"OpenCV error processing image bytes: {str(e)}") from e
        except Exception as e:
            logger.error(f"Unexpected error converting image bytes: {e}")
            raise ImageProcessingError(f"Failed to process image bytes: {str(e)}") from e

    def process_image(self, img: Union[str, bytes, bytearray, np.ndarray]) -> np.ndarray:
        """Process image from multiple input formats into RGB numpy array.
        
        Strategy: Accepts various input types for flexibility. Always returns RGB format
        for consistency across the pipeline. For numpy arrays, attempts BGR->RGB conversion
        as a safe default (OpenCV convention).
        
        Args:
            img: Image as file path (str), bytes, bytearray, or numpy array.
            
        Returns:
            RGB image array with shape (height, width, 3) and dtype uint8.
            
        Raises:
            TypeError: If img type is not supported.
            FileNotFoundError: If file path doesn't exist.
            PermissionError: If file cannot be read.
            ImageProcessingError: If image conversion fails.
        """
        try:
            # Handle numpy array - assume OpenCV BGR convention
            if isinstance(img, np.ndarray):
                if img.ndim == 3 and img.shape[2] == 3:
                    # Attempt BGR->RGB conversion (safe for OpenCV arrays)
                    try:
                        return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                    except cv2.error as e:
                        logger.warning(f"Could not convert color space, returning as-is: {e}")
                        return img
                return img
            
            # Handle bytes-like objects
            if isinstance(img, (bytes, bytearray)):
                return self._prepare_image_from_bytes(img)
            
            # Handle file path
            if isinstance(img, str):
                return self._prepare_image_from_path(img)

            raise TypeError(f'img must be a file path, bytes, bytearray, or numpy.ndarray, got {type(img).__name__}')
            
        except (TypeError, ImageProcessingError, FileNotFoundError, PermissionError):
            raise
        except Exception as e:
            logger.error(f"Unexpected error in process_image: {e}")
            raise ImageProcessingError(f"Failed to process image: {str(e)}") from e
    
    def process_for_ocr(
        self, 
        img: Union[str, bytes, np.ndarray],
        target_size: Union[int, tuple, None] = None,
        enhance: bool = True
    ) -> np.ndarray:
        """Process and optimize image specifically for OCR workflows.
        
        Strategy: Two-stage pipeline - first normalize input format, then apply 
        OCR-specific enhancements (resizing, denoising, sharpening).
        
        Args:
            img: Image as file path (str), bytes, bytearray, or numpy array.
            target_size: Target size for OCR. If None, uses default_ocr_size.
                If int, represents max width. If tuple, represents (width, height).
            enhance: Whether to apply image enhancement techniques (denoising, sharpening).
                Defaults to True.
        
        Returns:
            Processed RGB image optimized for OCR, with shape (height, width, 3).
            
        Raises:
            TypeError: If img type is not supported.
            ImageProcessingError: If processing fails.
        """
        # Stage 1: Normalize to RGB numpy array
        rgb_image = self.process_image(img)
        
        # Stage 2: Apply OCR-specific preprocessing
        target = target_size or self.default_ocr_size
        return prepare_for_ocr(rgb_image, target, enhance)
