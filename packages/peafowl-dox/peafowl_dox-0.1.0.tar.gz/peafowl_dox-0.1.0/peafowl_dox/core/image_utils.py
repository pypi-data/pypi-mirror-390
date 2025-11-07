"""Image processing utilities.

This module provides utility functions for image manipulation and preprocessing,
particularly focused on OCR preparation and format conversion.
"""

from io import BytesIO
from typing import Union, BinaryIO, Tuple, Optional
import logging

import cv2
import numpy as np
from PIL import Image

from ..exceptions import ImageProcessingError


logger = logging.getLogger(__name__)


def multipart_to_array(
    multipart_image: Union[BinaryIO, BytesIO]
) -> np.ndarray:
    """Convert multipart/form-data image to numpy array.
    
    Reads binary image data from multipart form upload and converts it
    to a numpy array suitable for OpenCV/PIL processing.
    
    Args:
        multipart_image: Binary image data from file upload or BytesIO stream.
    
    Returns:
        np.ndarray: Image as numpy array in RGB format.
    
    Raises:
        ImageProcessingError: If image cannot be read or converted.
    
    Example:
        >>> from io import BytesIO
        >>> with open('image.jpg', 'rb') as f:
        ...     img_array = multipart_to_array(f)
        >>> print(img_array.shape)  # (height, width, channels)
    """
    multipart_image.seek(0)
    image = Image.open(BytesIO(multipart_image.read()))
    return np.array(image)


def resize_image(
    image: np.ndarray,
    target_size: Union[Tuple[int, int], int],
    maintain_aspect: bool = True,
    interpolation: int = cv2.INTER_AREA
) -> np.ndarray:
    """Resize image with optional aspect ratio preservation.
    
    Provides flexible image resizing with support for both fixed dimensions
    and maximum dimension constraints. Uses OpenCV for high-quality interpolation.
    
    Args:
        image: Input image as numpy array (H, W) or (H, W, C).
        target_size: Either a tuple (width, height) for fixed size,
            or an integer for maximum dimension while preserving aspect ratio.
        maintain_aspect: If True, preserves aspect ratio. When target_size is
            a tuple, scales to fit within bounds. Defaults to True.
        interpolation: OpenCV interpolation method. Defaults to cv2.INTER_AREA
            (best for shrinking). Use cv2.INTER_CUBIC or cv2.INTER_LINEAR
            for enlarging.
    
    Returns:
        np.ndarray: Resized image with same number of channels as input.
    
    Raises:
        ImageProcessingError: If resizing operation fails.
    
    Examples:
        >>> resized = resize_image(img, (800, 600), maintain_aspect=False)
        >>> resized = resize_image(img, (800, 600), maintain_aspect=True)
        >>> resized = resize_image(img, 800)
    
    Note:
        When maintain_aspect=True and target_size is a tuple, the output
        dimensions will be <= target dimensions, never exceeding either bound.
    """
    try:
        h, w = image.shape[:2]
        
        if isinstance(target_size, int):
            if maintain_aspect:
                if w > h:
                    new_w, new_h = target_size, int(h * target_size / w)
                else:
                    new_w, new_h = int(w * target_size / h), target_size
            else:
                new_w = new_h = target_size
        else:
            new_w, new_h = target_size
            
            if maintain_aspect:
                ratio = min(new_w / w, new_h / h)
                new_w, new_h = int(w * ratio), int(h * ratio)
        
        return cv2.resize(image, (new_w, new_h), interpolation=interpolation)
        
    except Exception as e:
        raise ImageProcessingError(f"Failed to resize image: {str(e)}") from e


def prepare_for_ocr(
    image: np.ndarray,
    target_size: Optional[Union[Tuple[int, int], int]] = None,
    enhance: bool = True
) -> np.ndarray:
    """Prepare image for OCR processing with optional enhancement.
    
    Applies a preprocessing pipeline optimized for Optical Character Recognition:
    1. Converts to grayscale (if needed)
    2. Resizes to target dimensions (if specified)
    3. Applies noise reduction and contrast enhancement (if enabled)
    
    This preprocessing improves OCR accuracy by normalizing image characteristics
    and reducing artifacts that confuse text recognition engines.
    
    Args:
        image: Input image as numpy array (H, W) or (H, W, C).
        target_size: Optional resize target. Can be (width, height) tuple
            or integer for max dimension. If None, keeps original size.
        enhance: If True, applies median blur for noise reduction and
            contrast enhancement. Recommended for low-quality scans.
            Defaults to True.
    
    Returns:
        np.ndarray: Grayscale image ready for OCR, with shape (H, W).
    
    Raises:
        ImageProcessingError: If preprocessing pipeline fails.
    
    Examples:
        >>> ocr_ready = prepare_for_ocr(color_image)
        >>> ocr_ready = prepare_for_ocr(image, target_size=1000)
        >>> ocr_ready = prepare_for_ocr(image, target_size=(1200, 1600), enhance=False)
    
    Note:
        Enhancement uses median blur (3x3 kernel) and contrast adjustment 
        (alpha=1.2, beta=10). Disable for clean, high-resolution scans.
    """
    try:
        processed = image.copy()
        
        if len(processed.shape) == 3:
            processed = cv2.cvtColor(processed, cv2.COLOR_RGB2GRAY)
        
        if target_size:
            processed = resize_image(processed, target_size)
        
        if enhance:
            processed = cv2.medianBlur(processed, 3)
            processed = cv2.convertScaleAbs(processed, alpha=1.2, beta=10)
        
        return processed
        
    except Exception as e:
        raise ImageProcessingError(f"Failed to prepare image for OCR: {str(e)}") from e
