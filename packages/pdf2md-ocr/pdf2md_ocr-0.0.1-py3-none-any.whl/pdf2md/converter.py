"""PDF Converter core logic using the Marker library.

This module provides the main PDF conversion functionality, handling PDF processing,
image extraction, and markdown generation using the Marker library for high-quality
PDF to markdown conversion.
"""

import logging
import os
import shutil
import subprocess
import tempfile
import time
from collections.abc import Callable
from datetime import datetime
from pathlib import Path
from typing import Any

from .exceptions import (
    EncryptedPDFError,
    InvalidInputError,
    OutputWriteError,
    PDFProcessingError,
    ResourceConstraintError,
)
from .models.extracted_image import ExtractedImage
from .models.markdown_output import MarkdownOutput
from .models.pdf_document import PDFDocument
from .models.processing_metadata import ProcessingMetadata


class PDFConverter:
    """PDF to Markdown converter using the Marker library.

    This class handles the conversion of PDF documents to structured markdown,
    including text extraction, image processing, and metadata generation.
    """

    def __init__(
        self,
        progress_callback: Callable[[int, int, str], None] | None = None,
        image_format: str = "png",
        max_pages: int = 0,
        extract_images: bool = True,
        preserve_layout: bool = True,
        marker_timeout: int | None = None,
    ):
        """Initialize the PDF converter.

        Args:
            progress_callback: Optional callback for progress updates (current, total, message)
            image_format: Format for extracted images (png, jpeg, webp)
            max_pages: Maximum pages to process (0 = unlimited)
            extract_images: Whether to extract images from PDF
            preserve_layout: Whether to preserve original document layout
            marker_timeout: Timeout in seconds for marker_single command (None = no timeout)
        """
        self.progress_callback = progress_callback
        self.image_format = image_format.lower()
        self.max_pages = max_pages
        self.extract_images = extract_images
        self.preserve_layout = preserve_layout
        self.marker_timeout = marker_timeout

        # Validate image format
        valid_formats = {"png", "jpeg", "webp"}
        if self.image_format not in valid_formats:
            raise ValueError(f"Unsupported image format: {image_format}")

        self.logger = logging.getLogger(__name__)

    def convert(self, input_path: str, output_dir: str) -> MarkdownOutput:
        """Convert PDF to Markdown.

        Args:
            input_path: Path to input PDF file
            output_dir: Directory for output files

        Returns:
            MarkdownOutput with conversion results
        """
        start_time = time.time()

        try:
            # Initialize result
            result = MarkdownOutput()
            result.metadata = ProcessingMetadata()
            result.metadata.timestamp = datetime.now()

            # Create and validate PDF document
            pdf_doc = self._create_pdf_document(input_path)

            # Ensure output directory exists
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)

            # Update progress
            self._update_progress(1, 5, "Analyzing PDF structure...")

            # Analyze PDF
            self._analyze_pdf(pdf_doc)
            result.metadata.input_file_size = pdf_doc.file_size
            result.metadata.pages_processed = (
                min(pdf_doc.page_count, self.max_pages)
                if self.max_pages > 0
                else pdf_doc.page_count
            )

            # Update progress
            self._update_progress(2, 5, "Processing PDF content...")

            # Convert PDF using Marker
            markdown_content, images = self._convert_with_marker(pdf_doc, output_path)

            # Update progress
            self._update_progress(3, 5, "Processing extracted images...")

            # Process extracted images
            processed_images = self._process_images(images, output_path)

            # Update progress
            self._update_progress(4, 5, "Generating markdown output...")

            # Create output
            output_file = output_path / f"{Path(input_path).stem}.md"
            result.content = markdown_content
            result.output_path = str(output_file)
            result.images = processed_images
            result.image_references = [img.filename for img in processed_images]

            # Save markdown file
            result.save_markdown()

            # Update progress
            self._update_progress(5, 5, "Finalizing conversion...")

            # Finalize metadata
            result.metadata.processing_time = time.time() - start_time
            result.metadata.images_extracted = len(processed_images)
            result.metadata.output_size = self._calculate_output_size(output_path)
            result.metadata.marker_version = self._get_marker_version()

            # Save metadata
            result.save_metadata(output_path)

            result.success = True
            pdf_doc.set_completed()

            return result

        except Exception as e:
            return self._handle_conversion_error(e, start_time)

    def _create_pdf_document(self, input_path: str) -> PDFDocument:
        """Create and validate PDF document."""
        try:
            return PDFDocument.from_path(input_path)
        except FileNotFoundError:
            raise InvalidInputError(f"PDF file not found: {input_path}")
        except ValueError as e:
            raise InvalidInputError(str(e))

    def _analyze_pdf(self, pdf_doc: PDFDocument):
        """Analyze PDF document structure and metadata."""
        try:
            # Basic PDF validation without marker imports
            with open(pdf_doc.file_path, "rb") as f:
                # Basic PDF validation
                header = f.read(8)
                if not header.startswith(b"%PDF-"):
                    raise PDFProcessingError(
                        "Invalid PDF file format", pdf_path=pdf_doc.file_path
                    )

            # For now, use basic analysis - actual marker analysis happens in conversion
            # In a real implementation, you could use PyPDF2 or similar for basic metadata
            pdf_doc.set_analyzed(
                page_count=10,  # Placeholder - would detect actual page count
                is_encrypted=False,  # Placeholder - would detect encryption
                language="en",  # Placeholder - would detect language
                metadata={"title": "Document", "author": "Unknown"},  # Placeholder
            )

        except ImportError:
            raise PDFProcessingError("Marker library not available")
        except MemoryError:
            raise ResourceConstraintError(
                "Insufficient memory to analyze PDF", resource_type="memory"
            )
        except Exception as e:
            if "encrypted" in str(e).lower() or "password" in str(e).lower():
                raise EncryptedPDFError(pdf_path=pdf_doc.file_path)
            raise PDFProcessingError(
                f"PDF analysis failed: {str(e)}", pdf_path=pdf_doc.file_path
            )

    def _convert_with_marker(
        self, pdf_doc: PDFDocument, output_path: Path
    ) -> tuple[str, list[Any]]:
        """Convert PDF using Marker CLI tool."""
        try:
            # Create a temporary directory for marker output
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                input_pdf = Path(pdf_doc.file_path)  # Ensure it's a Path object

                # Marker CLI outputs to same directory as input with .md extension
                # So we need to copy the PDF to temp directory and run from there
                temp_pdf = temp_path / input_pdf.name
                shutil.copy2(input_pdf, temp_pdf)

                # Prepare marker_single command using current Python environment
                marker_cmd = [
                    "marker_single",  # Use the installed executable directly
                    str(temp_pdf),
                    "--output_dir",
                    str(temp_path),  # Specify output directory
                ]

                # Add max_pages if specified
                if self.max_pages and self.max_pages > 0:
                    marker_cmd.extend(["--max_pages", str(self.max_pages)])

                # Log marker conversion start
                timeout_str = (
                    f"timeout={self.marker_timeout}s"
                    if self.marker_timeout
                    else "no timeout"
                )
                self.logger.info(
                    f"Starting marker_single conversion ({timeout_str})..."
                )
                self._update_progress(
                    2, 5, f"Converting with marker ({timeout_str})..."
                )

                # Run marker conversion with optional timeout
                # Pass the current environment to ensure marker_single is found
                result = subprocess.run(
                    marker_cmd,
                    cwd=temp_path,
                    capture_output=True,
                    text=True,
                    timeout=self.marker_timeout,  # Optional timeout (None = no timeout)
                    env=os.environ.copy(),  # Use current environment to find marker_single
                )

                # Check if conversion was successful by looking for output files
                # Marker creates a directory with the same name as the PDF file (without extension)
                output_dir_name = temp_pdf.stem
                marker_output_dir = temp_path / output_dir_name

                if result.returncode != 0 and not marker_output_dir.exists():
                    # Only treat as error if no output directory was created AND return code is non-zero
                    error_msg = result.stderr if result.stderr else result.stdout
                    raise PDFProcessingError(f"Marker conversion failed: {error_msg}")

                if not marker_output_dir.exists():
                    raise PDFProcessingError("No output directory generated by marker")

                # Look for the markdown file in the output directory
                md_files = list(marker_output_dir.glob("*.md"))
                if not md_files:
                    raise PDFProcessingError("No markdown file generated by marker")

                # Read the generated markdown content
                markdown_file = md_files[0]
                with open(markdown_file, encoding="utf-8") as f:
                    full_text = f.read()

                # Look for extracted images directory (if any)
                processed_images = []
                images_dir = (
                    marker_output_dir / "images"
                )  # Check if marker created an images subdirectory
                if self.extract_images and images_dir.exists():
                    # Create output images directory
                    output_images_dir = output_path.parent / "images"
                    output_images_dir.mkdir(exist_ok=True)

                    # Process each extracted image
                    for i, img_file in enumerate(sorted(images_dir.glob("*"))):
                        if img_file.is_file():
                            # Copy image to output directory
                            new_name = f"image_{i + 1:03d}{img_file.suffix}"
                            output_img_path = output_images_dir / new_name
                            shutil.copy2(img_file, output_img_path)

                            processed_images.append(
                                {
                                    "filename": new_name,
                                    "page": i + 1,
                                    "data": None,  # Data already saved to file
                                    "width": 800,  # Default dimensions
                                    "height": 600,
                                }
                            )

                return full_text, processed_images

        except subprocess.TimeoutExpired:
            timeout_str = (
                f"{self.marker_timeout} seconds" if self.marker_timeout else "N/A"
            )
            raise PDFProcessingError(
                f"PDF conversion timed out (limit: {timeout_str}). "
                f"Use --timeout to increase the limit or omit it for no timeout."
            )
        except subprocess.CalledProcessError as e:
            raise PDFProcessingError(f"Marker process failed: {e}")
        except MemoryError:
            raise PDFProcessingError("PDF conversion requires more memory")
        except Exception as e:
            if "encrypted" in str(e).lower():
                raise PDFProcessingError(f"PDF is encrypted: {pdf_doc.file_path}")
            raise PDFProcessingError(f"PDF conversion failed: {str(e)}")

    def _process_images(
        self, images: list[Any], output_path: Path
    ) -> list[ExtractedImage]:
        """Process and save extracted images."""
        if not self.extract_images or not images:
            return []

        processed_images = []
        images_dir = output_path / "images"
        images_dir.mkdir(exist_ok=True)

        try:
            for i, img_data in enumerate(images):
                # Create ExtractedImage object
                filename = img_data.get(
                    "filename", f"image_{i + 1:03d}.{self.image_format}"
                )

                extracted_image = ExtractedImage(
                    filename=filename,
                    original_page=img_data.get("page", 1),
                    image_format=self.image_format,
                    dimensions=(
                        img_data.get("width", 800),
                        img_data.get("height", 600),
                    ),
                    file_size=len(img_data.get("data", b"")),
                    alt_text=f"Image {i + 1} from page {img_data.get('page', 1)}",
                    output_path=str(images_dir / filename),
                )

                # In a real implementation, you would save the actual image data
                # For now, create a placeholder file
                image_file = images_dir / filename
                with open(image_file, "wb") as f:
                    f.write(img_data.get("data", b"mock_image_data"))

                extracted_image.file_size = image_file.stat().st_size
                processed_images.append(extracted_image)

            return processed_images

        except OSError as e:
            raise OutputWriteError(
                f"Failed to save images: {str(e)}", output_path=str(images_dir)
            )

    def _calculate_output_size(self, output_path: Path) -> int:
        """Calculate total size of output files."""
        total_size = 0

        try:
            for file_path in output_path.rglob("*"):
                if file_path.is_file():
                    total_size += file_path.stat().st_size
        except OSError:
            # If we can't calculate size, return 0
            pass

        return total_size

    def _get_marker_version(self) -> str:
        """Get Marker library version."""
        try:
            import marker

            return getattr(marker, "__version__", "unknown")
        except ImportError:
            return "not available"

    def _update_progress(self, current: int, total: int, message: str):
        """Update progress if callback is available."""
        if self.progress_callback:
            self.progress_callback(current, total, message)

    def _handle_conversion_error(
        self, error: Exception, start_time: float
    ) -> MarkdownOutput:
        """Handle conversion errors and return error result."""
        result = MarkdownOutput()
        result.success = False
        result.error = error
        result.error_message = str(error)

        # Create metadata for failed conversion
        result.metadata = ProcessingMetadata()
        result.metadata.processing_time = time.time() - start_time
        result.metadata.marker_version = self._get_marker_version()

        return result


class MarkerInterface:
    """Interface to the Marker library for PDF processing.

    This class provides a clean interface to the Marker library,
    handling model loading and PDF conversion operations.
    """

    def __init__(self):
        """Initialize Marker interface."""
        self._models_loaded = False
        self._models = None

    def load_models(self):
        """Load Marker models (cached after first load)."""
        if self._models_loaded:
            return self._models

        try:
            # In real implementation:
            # from marker.models import load_all_models
            # self._models = load_all_models()

            # Mock implementation
            self._models = {"mock": "models"}
            self._models_loaded = True
            return self._models

        except Exception as e:
            raise PDFProcessingError(f"Failed to load Marker models: {str(e)}")

    def convert_pdf(self, pdf_path: str, **kwargs) -> tuple[str, list[Any]]:
        """Convert PDF using Marker library.

        Args:
            pdf_path: Path to PDF file
            **kwargs: Additional conversion options

        Returns:
            Tuple of (markdown_content, extracted_images)
        """
        self.load_models()

        try:
            # In real implementation:
            # from marker.convert import convert_single_pdf
            # markdown_content, images = convert_single_pdf(pdf_path, self._models, **kwargs)

            # Mock implementation
            with open(pdf_path, "rb") as f:
                content = f.read()

            markdown_content = (
                f"# Mock Conversion\n\nProcessed {len(content)} bytes from {pdf_path}"
            )
            images = []

            return markdown_content, images

        except Exception as e:
            raise PDFProcessingError(f"Marker conversion failed: {str(e)}")


# Global marker interface instance
_marker_interface = None


def get_marker_interface() -> MarkerInterface:
    """Get global Marker interface instance."""
    global _marker_interface
    if _marker_interface is None:
        _marker_interface = MarkerInterface()
    return _marker_interface
