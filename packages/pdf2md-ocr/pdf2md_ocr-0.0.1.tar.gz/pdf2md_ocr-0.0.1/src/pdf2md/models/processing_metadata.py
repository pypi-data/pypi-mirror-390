"""Processing Metadata model for tracking conversion statistics."""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Union
from pathlib import Path
from datetime import datetime
import json


@dataclass
class ProcessingMetadata:
    """Contains processing statistics and document information.
    
    Attributes:
        processing_time: Total processing time in seconds
        input_file_size: Original PDF size in bytes
        output_size: Total size of generated files
        pages_processed: Number of pages successfully processed
        images_extracted: Number of images extracted
        tables_found: Number of tables detected and converted
        equations_found: Number of mathematical equations converted
        language_detected: Detected document language
        processing_warnings: Non-fatal issues encountered
        marker_version: Version of Marker library used
        timestamp: When processing completed
    """
    
    processing_time: float = 0.0
    input_file_size: int = 0
    output_size: int = 0
    pages_processed: int = 0
    images_extracted: int = 0
    tables_found: int = 0
    equations_found: int = 0
    language_detected: str = ""
    processing_warnings: List[str] = field(default_factory=list)
    marker_version: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "processing_time": self.processing_time,
            "input_file_size": self.input_file_size,
            "output_size": self.output_size,
            "pages_processed": self.pages_processed,
            "images_extracted": self.images_extracted,
            "tables_found": self.tables_found,
            "equations_found": self.equations_found,
            "language_detected": self.language_detected,
            "processing_warnings": self.processing_warnings,
            "marker_version": self.marker_version,
            "timestamp": self.timestamp.isoformat()
        }
    
    def save_to_file(self, output_path: Union[str, Path]):
        """Save metadata to JSON file."""
        path = Path(output_path)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)