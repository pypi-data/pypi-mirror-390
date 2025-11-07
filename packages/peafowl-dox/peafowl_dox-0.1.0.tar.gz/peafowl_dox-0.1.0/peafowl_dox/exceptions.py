"""Custom exceptions for peafowl_dox package."""

class PeafowlDoxError(Exception):
    """Base exception for all peafowl_dox errors."""
    pass

class ImageProcessingError(PeafowlDoxError):
    """Raised when image processing operations fail."""
    pass

class PDFConversionError(PeafowlDoxError):
    """Raised when PDF conversion operations fail."""
    pass
