"""PDF to image conversion utilities."""

from io import BytesIO
from typing import List, Union, BinaryIO
import logging

import fitz  # PyMuPDF
import numpy as np
from PIL import Image

from ..exceptions import PDFConversionError

logger = logging.getLogger(__name__)

def pdf_to_images(
    pdf_input: Union[str, bytes, BinaryIO],
    dpi: int = 300,
    image_format: str = "RGB"
) -> List[np.ndarray]:
    """Convert PDF pages to image arrays using PyMuPDF.
    
    Args:
        pdf_input: PDF file path, bytes, or file-like object
        dpi: Resolution for conversion (default: 300)
        image_format: Color format - "RGB", "RGBA", or "L" for grayscale
        
    Returns:
        List of numpy arrays, one per PDF page
        
    Raises:
        PDFConversionError: If PDF cannot be processed
        
    Example:
        >>> images = pdf_to_images("document.pdf", dpi=200)
        >>> print(f"Converted {len(images)} pages")
    """
    try:
        # Handle different input types
        if isinstance(pdf_input, str):
            doc = fitz.open(pdf_input)
        elif isinstance(pdf_input, bytes):
            doc = fitz.open(stream=pdf_input, filetype="pdf")
        else:  # file-like object
            pdf_input.seek(0) # type: ignore
            doc = fitz.open(stream=pdf_input.read(), filetype="pdf") # type: ignore
        
        images = []
        matrix = fitz.Matrix(dpi/72, dpi/72)  # Scale factor for DPI
        
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            pix = page.get_pixmap(matrix=matrix)
            
            # Convert to PIL Image then numpy
            img_data = pix.tobytes("ppm")
            pil_image = Image.open(BytesIO(img_data))
            
            if image_format != "RGB":
                pil_image = pil_image.convert(image_format)
                
            images.append(np.array(pil_image))
            
        doc.close()
        return images
        
    except Exception as e:
        logger.error(f"PDF conversion failed: {e}")
        raise PDFConversionError(f"Failed to convert PDF: {str(e)}") from e
