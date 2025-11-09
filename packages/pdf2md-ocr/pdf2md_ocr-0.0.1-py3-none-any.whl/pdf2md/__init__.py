"""PDF to Markdown Converter Package

A Docker-based CLI tool for converting PDF documents to structured markdown format
using the Marker library, with support for multi-architecture deployment and
semantic versioning.
"""

__version__ = "0.0.1"
__author__ = "PDF2MD Docker Project"
__description__ = "PDF to Markdown conversion tool in Docker"

# Core components
# Utilities
from . import utils
from .converter import PDFConverter
from .docker_interface import ContainerManager, DockerInterface

# Exceptions
from .exceptions import (
    ConfigurationError,
    DockerError,
    EncryptedPDFError,
    InvalidInputError,
    OutputWriteError,
    PDF2MDError,
    PDFProcessingError,
    ResourceConstraintError,
)
from .models.conversion_config import ConversionConfig
from .models.extracted_image import ExtractedImage
from .models.markdown_output import MarkdownOutput

# Data models
from .models.pdf_document import PDFDocument
from .models.processing_metadata import ProcessingMetadata
from .progress import ProgressBar, ProgressIndicator, Spinner

__all__ = [
    # Core components
    "PDFConverter",
    "ProgressIndicator",
    "ProgressBar",
    "Spinner",
    "DockerInterface",
    "ContainerManager",
    # Data models
    "PDFDocument",
    "MarkdownOutput",
    "ExtractedImage",
    "ProcessingMetadata",
    "ConversionConfig",
    # Exceptions
    "PDF2MDError",
    "InvalidInputError",
    "PDFProcessingError",
    "EncryptedPDFError",
    "ResourceConstraintError",
    "OutputWriteError",
    "DockerError",
    "ConfigurationError",
    # Utilities
    "utils",
]
