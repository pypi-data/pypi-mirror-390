"""PDF Document model for representing input PDF files."""

from dataclasses import dataclass, field
from typing import Dict, Any, Union
from pathlib import Path
from enum import Enum


class ProcessingState(Enum):
    """States for PDF document processing."""
    CREATED = "created"
    VALIDATED = "validated" 
    ANALYZED = "analyzed"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class PDFDocument:
    """Represents an input PDF file to be processed.
    
    Attributes:
        file_path: Absolute path to the PDF file
        file_size: Size in bytes for progress estimation
        page_count: Number of pages (detected during processing)
        is_encrypted: Whether PDF is password protected
        language: Detected document language (e.g., "en", "es")
        metadata: PDF metadata (title, author, creation date)
        state: Current processing state
    """
    
    file_path: str
    file_size: int = 0
    page_count: int = 0
    is_encrypted: bool = False
    language: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    state: ProcessingState = ProcessingState.CREATED
    
    def __post_init__(self):
        """Validate the PDFDocument after initialization."""
        if not self.file_path:
            raise ValueError("file_path cannot be empty")
        
        path = Path(self.file_path)
        if not path.is_absolute():
            raise ValueError("file_path must be absolute")
        
        if not path.suffix.lower() == '.pdf':
            raise ValueError("file must have .pdf extension")
    
    @classmethod
    def from_path(cls, file_path: Union[str, Path]) -> 'PDFDocument':
        """Create a PDFDocument from a file path."""
        path = Path(file_path).resolve()
        
        if not path.exists():
            raise FileNotFoundError(f"PDF file not found: {path}")
        
        if not path.is_file():
            raise ValueError(f"Path is not a file: {path}")
        
        file_size = path.stat().st_size
        if file_size == 0:
            raise ValueError(f"PDF file is empty: {path}")
        
        return cls(
            file_path=str(path),
            file_size=file_size,
            state=ProcessingState.VALIDATED
        )
    
    def set_analyzed(self, page_count: int, is_encrypted: bool, 
                    language: str = "", metadata: Dict[str, Any] = None):
        """Mark document as analyzed with extracted information."""
        self.page_count = page_count
        self.is_encrypted = is_encrypted
        self.language = language
        if metadata:
            self.metadata = metadata
        self.state = ProcessingState.ANALYZED
    
    def set_processing(self):
        """Mark document as currently being processed."""
        self.state = ProcessingState.PROCESSING
    
    def set_completed(self):
        """Mark document as successfully processed."""
        self.state = ProcessingState.COMPLETED
    
    def set_failed(self):
        """Mark document as failed to process."""
        self.state = ProcessingState.FAILED