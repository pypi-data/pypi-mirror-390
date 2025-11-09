"""Extracted Image model for images extracted from PDFs."""

from dataclasses import dataclass
from typing import Tuple


@dataclass 
class ExtractedImage:
    """Represents an image extracted from the PDF.
    
    Attributes:
        filename: Generated filename (e.g., "image_001.png")
        original_page: Source page number in PDF
        image_format: Format (PNG, JPEG, etc.)
        dimensions: Width and height in pixels
        file_size: Size in bytes
        alt_text: Generated alt text for accessibility
        output_path: Full path where image is saved
    """
    
    filename: str
    original_page: int
    image_format: str
    dimensions: Tuple[int, int]
    file_size: int = 0
    alt_text: str = ""
    output_path: str = ""
    
    def __post_init__(self):
        """Validate the ExtractedImage after initialization."""
        if not self.filename:
            raise ValueError("filename cannot be empty")
        
        if self.original_page < 1:
            raise ValueError("original_page must be >= 1")
        
        if not self.image_format:
            raise ValueError("image_format cannot be empty")
        
        width, height = self.dimensions
        if width <= 0 or height <= 0:
            raise ValueError("dimensions must be positive integers")