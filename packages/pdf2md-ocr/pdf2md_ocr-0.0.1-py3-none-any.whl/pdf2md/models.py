"""Data models for PDF2MD.

This module defines the core data structures used throughout the application,
including PDF documents, conversion results, progress tracking, and Docker configurations.
"""

import json
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any


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
    metadata: dict[str, Any] = field(default_factory=dict)
    state: ProcessingState = ProcessingState.CREATED

    def __post_init__(self):
        """Validate the PDFDocument after initialization."""
        if not self.file_path:
            raise ValueError("file_path cannot be empty")

        path = Path(self.file_path)
        if not path.is_absolute():
            raise ValueError("file_path must be absolute")

        if not path.suffix.lower() == ".pdf":
            raise ValueError("file must have .pdf extension")

    @classmethod
    def from_path(cls, file_path: str | Path) -> "PDFDocument":
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
            file_path=str(path), file_size=file_size, state=ProcessingState.VALIDATED
        )

    def set_analyzed(
        self,
        page_count: int,
        is_encrypted: bool,
        language: str = "",
        metadata: dict[str, Any] | None = None,
    ):
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
    dimensions: tuple[int, int]
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
    processing_warnings: list[str] = field(default_factory=list)
    marker_version: str = ""
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict[str, Any]:
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
            "timestamp": self.timestamp.isoformat(),
        }

    def save_to_file(self, output_path: str | Path):
        """Save metadata to JSON file."""
        path = Path(output_path)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)


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
    image_references: list[str] = field(default_factory=list)
    images: list[ExtractedImage] = field(default_factory=list)
    table_count: int = 0
    equation_count: int = 0
    metadata: ProcessingMetadata | None = None
    success: bool = False
    error: Exception | None = None
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
    def pdf_metadata(self) -> dict[str, Any]:
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

    def save_markdown(self, output_path: str | Path | None = None):
        """Save markdown content to file."""
        path = Path(output_path or self.output_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, "w", encoding="utf-8") as f:
            f.write(self.content)

        self.output_path = str(path)

    def save_metadata(self, output_dir: str | Path):
        """Save processing metadata to JSON file."""
        if self.metadata:
            output_path = Path(output_dir) / "metadata.json"
            self.metadata.save_to_file(output_path)


@dataclass
class ConversionProgress:
    """Tracks progress during conversion process.

    Attributes:
        current_step: Current step number (0-based)
        total_steps: Total number of steps
        current_message: Current status message
        callback: Optional callback function for progress updates
        error_callback: Optional callback function for error reporting
        start_time: When processing started
    """

    current_step: int = 0
    total_steps: int = 0
    current_message: str = ""
    callback: callable | None = None
    error_callback: callable | None = None
    start_time: datetime | None = None

    def set_total_steps(self, total: int):
        """Set the total number of steps."""
        self.total_steps = total
        if self.start_time is None:
            self.start_time = datetime.now()

    def advance_step(self, message: str):
        """Advance to the next step with a status message."""
        self.current_step += 1
        self.current_message = message

        if self.callback:
            self.callback(self.current_step, self.total_steps, message)

    def update_progress(self, current: int, message: str):
        """Update progress with specific step number."""
        self.current_step = current
        self.current_message = message

        if self.callback:
            self.callback(current, self.total_steps, message)

    def report_error(self, message: str):
        """Report an error during processing."""
        if self.error_callback:
            self.error_callback(message)

    def start_timing(self):
        """Start timing the process."""
        self.start_time = datetime.now()

    def get_processing_rate(self) -> float | None:
        """Get processing rate in items per second."""
        if not self.start_time or self.current_step == 0:
            return None

        elapsed = (datetime.now() - self.start_time).total_seconds()
        if elapsed == 0:
            return None

        return self.current_step / elapsed

    def is_complete(self) -> bool:
        """Check if processing is complete."""
        return self.current_step >= self.total_steps


@dataclass
class VolumeMount:
    """Represents a Docker volume mount configuration.

    Attributes:
        host_path: Path on the host system
        container_path: Path inside the container
        mode: Mount mode ("ro" for read-only, "rw" for read-write)
    """

    host_path: str
    container_path: str
    mode: str = "ro"

    def __post_init__(self):
        """Validate volume mount configuration."""
        if not self.host_path:
            raise ValueError("host_path cannot be empty")

        if not self.container_path:
            raise ValueError("container_path cannot be empty")

        if self.mode not in ("ro", "rw"):
            raise ValueError("mode must be 'ro' or 'rw'")

        # Normalize container path
        self.container_path = self.container_path.replace("//", "/").rstrip("/")
        if not self.container_path.startswith("/"):
            self.container_path = "/" + self.container_path

    def to_docker_arg(self) -> str:
        """Convert to Docker -v argument format."""
        return f"{self.host_path}:{self.container_path}:{self.mode}"


@dataclass
class DockerConfig:
    """Configuration for Docker container execution.

    Attributes:
        image: Docker image name and tag
        volume_mounts: List of volume mounts
        environment: Environment variables
        user_id: User ID for non-root execution
        memory_limit: Memory limit (e.g., "1g", "512m")
        cpu_limit: CPU limit (e.g., "2", "0.5")
        workdir: Working directory inside container
        security_opts: Security options
        remove_after_run: Whether to remove container after execution
    """

    image: str
    volume_mounts: list[VolumeMount] = field(default_factory=list)
    environment: dict[str, str] = field(default_factory=dict)
    user_id: int = 1000
    memory_limit: str | None = None
    cpu_limit: str | None = None
    workdir: str = "/app"
    security_opts: list[str] = field(default_factory=lambda: ["no-new-privileges"])
    remove_after_run: bool = True

    def __post_init__(self):
        """Validate Docker configuration."""
        if not self.image:
            raise ValueError("image cannot be empty")

    def add_volume_mount(self, host_path: str, container_path: str, mode: str = "ro"):
        """Add a volume mount to the configuration."""
        mount = VolumeMount(host_path, container_path, mode)
        self.volume_mounts.append(mount)

    def to_docker_args(self) -> list[str]:
        """Convert configuration to Docker command arguments."""
        args = ["docker", "run"]

        if self.remove_after_run:
            args.append("--rm")

        # User ID
        args.extend(["--user", f"{self.user_id}:{self.user_id}"])

        # Working directory
        args.extend(["--workdir", self.workdir])

        # Security options
        for opt in self.security_opts:
            args.extend(["--security-opt", opt])

        # Resource limits
        if self.memory_limit:
            args.extend(["--memory", self.memory_limit])

        if self.cpu_limit:
            args.extend(["--cpus", self.cpu_limit])

        # Environment variables
        for key, value in self.environment.items():
            args.extend(["-e", f"{key}={value}"])

        # Volume mounts
        for mount in self.volume_mounts:
            args.extend(["-v", mount.to_docker_arg()])

        # Image name
        args.append(self.image)

        return args


@dataclass
class ConversionResult:
    """Result of a Docker-based conversion operation.

    Attributes:
        success: Whether the conversion succeeded
        exit_code: Exit code from Docker container
        stdout: Standard output from container
        stderr: Standard error from container
        execution_time: Time taken for execution
        error_message: Human-readable error message
        docker_command: Docker command that was executed
    """

    success: bool
    exit_code: int = 0
    stdout: str = ""
    stderr: str = ""
    execution_time: float = 0.0
    error_message: str = ""
    docker_command: list[str] = field(default_factory=list)
