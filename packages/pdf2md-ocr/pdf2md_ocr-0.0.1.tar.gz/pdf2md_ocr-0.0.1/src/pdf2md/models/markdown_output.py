"""Markdown Output model for representing conversion results."""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Union
from pathlib import Path

from .extracted_image import ExtractedImage
from .processing_metadata import ProcessingMetadata


@dataclass
class MarkdownOutput:
    """Represents the generated markdown content and structure.
    
    Attributes:
        content: Main markdown text content
        output_path: Path where markdown file will be saved
        image_references: List of image filenames referenced in markdown
        images: List of extracted image objects
        table_count: Number of tables converted
        equation_count: Number of equations converted to LaTeX
        metadata: Processing statistics and information
        success: Whether conversion was successful
        error: Exception if conversion failed
        error_message: Human-readable error message
    """
    
    content: str = ""
    output_path: str = ""
    image_references: List[str] = field(default_factory=list)
    images: List[ExtractedImage] = field(default_factory=list)
    table_count: int = 0
    equation_count: int = 0
    metadata: Optional[ProcessingMetadata] = None
    success: bool = False
    error: Optional[Exception] = None
    error_message: str = ""
    
    def __post_init__(self):
        """Initialize metadata if not provided."""
        if self.metadata is None:
            self.metadata = ProcessingMetadata()
    
    @property
    def images_extracted(self) -> int:
        """Number of images extracted."""
        return len(self.images)
    
    @property
    def pdf_metadata(self) -> Dict[str, Any]:
        """PDF metadata for backward compatibility."""
        return self.metadata.to_dict() if self.metadata else {}
    
    @property
    def image_format(self) -> str:
        """Format of extracted images."""
        if self.images:
            return self.images[0].image_format
        return "png"  # default
    
    @property
    def pages_processed(self) -> int:
        """Number of pages processed."""
        return self.metadata.pages_processed if self.metadata else 0
    
    def add_image(self, image: ExtractedImage):
        """Add an extracted image to the output."""
        self.images.append(image)
        if image.filename not in self.image_references:
            self.image_references.append(image.filename)
    
    def save_markdown(self, output_path: Optional[Union[str, Path]] = None):
        """Save markdown content to file."""
        path = Path(output_path or self.output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'w', encoding='utf-8') as f:
            f.write(self.content)
        
        self.output_path = str(path)
    
    def save_metadata(self, output_dir: Union[str, Path]):
        """Save processing metadata to JSON file."""
        if self.metadata:
            output_path = Path(output_dir) / "metadata.json"
            self.metadata.save_to_file(output_path)