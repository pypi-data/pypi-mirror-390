"""Conversion Configuration model for PDF processing settings."""

from dataclasses import dataclass
from typing import Tuple, Union
from pathlib import Path


@dataclass
class ConversionConfig:
    """Configuration parameters for the conversion process.
    
    Attributes:
        input_path: Input PDF file path
        output_dir: Output directory path
        progress_enabled: Whether to show progress feedback
        image_format: Preferred format for extracted images (default: PNG)
        max_image_size: Maximum dimensions for extracted images
        preserve_layout: Whether to preserve original document layout
        include_metadata: Whether to generate metadata JSON file
        max_pages: Maximum number of pages to process (0 = all)
        quiet: Whether to suppress output (quiet mode)
        extract_images: Whether to extract images from PDF
        marker_timeout: Timeout in seconds for marker conversion (None = no timeout)
    """
    
    input_path: str
    output_dir: str
    progress_enabled: bool = True
    image_format: str = "png"
    max_image_size: Tuple[int, int] = (2048, 2048)
    preserve_layout: bool = True
    include_metadata: bool = True
    max_pages: int = 0
    quiet: bool = False
    extract_images: bool = True
    marker_timeout: Union[int, None] = None
    
    def __post_init__(self):
        """Validate the ConversionConfig after initialization."""
        # Validate input path
        if not self.input_path:
            raise ValueError("input_path cannot be empty")
        
        input_path = Path(self.input_path)
        if not input_path.is_absolute():
            # Convert to absolute path
            self.input_path = str(input_path.resolve())
        
        # Validate output directory
        if not self.output_dir:
            raise ValueError("output_dir cannot be empty")
        
        output_path = Path(self.output_dir)
        if not output_path.is_absolute():
            # Convert to absolute path
            self.output_dir = str(output_path.resolve())
        
        # Validate image format
        valid_formats = {"png", "jpeg", "jpg", "webp"}
        if self.image_format.lower() not in valid_formats:
            raise ValueError(f"image_format must be one of: {', '.join(valid_formats)}")
        
        # Normalize image format
        self.image_format = self.image_format.lower()
        if self.image_format == "jpg":
            self.image_format = "jpeg"
        
        # Validate max image size
        width, height = self.max_image_size
        if width <= 0 or height <= 0:
            raise ValueError("max_image_size dimensions must be positive integers")
        
        # Validate max_pages
        if self.max_pages < 0:
            raise ValueError("max_pages must be >= 0 (0 means no limit)")
    
    @classmethod
    def from_args(cls, input_path: Union[str, Path], output_dir: Union[str, Path], 
                  **kwargs) -> 'ConversionConfig':
        """Create ConversionConfig from command line arguments."""
        return cls(
            input_path=str(input_path),
            output_dir=str(output_dir),
            **kwargs
        )
    
    def ensure_output_dir_exists(self):
        """Create output directory if it doesn't exist."""
        output_path = Path(self.output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
    
    def get_output_markdown_path(self) -> Path:
        """Get the path for the output markdown file."""
        input_path = Path(self.input_path)
        output_dir = Path(self.output_dir)
        markdown_filename = input_path.stem + ".md"
        return output_dir / markdown_filename
    
    def get_images_dir(self) -> Path:
        """Get the path for the images directory."""
        return Path(self.output_dir) / "images"