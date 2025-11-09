"""Custom exception classes for PDF2MD.

This module defines the exception hierarchy for the PDF2MD application,
providing specific error types for different failure scenarios with
appropriate exit codes and user-friendly error messages.
"""


class PDF2MDError(Exception):
    """Base exception class for all PDF2MD errors.

    Attributes:
        message: Human-readable error message
        exit_code: Exit code to use when this error causes program termination
        details: Additional technical details for debugging
    """

    def __init__(self, message: str, exit_code: int = 1, details: str | None = None):
        super().__init__(message)
        self.message = message
        self.exit_code = exit_code
        self.details = details

    def __str__(self) -> str:
        return self.message


class InvalidInputError(PDF2MDError):
    """Raised when input file validation fails.

    This includes cases like:
    - File doesn't exist
    - Not a PDF file
    - Empty file
    - Invalid file extension
    """

    def __init__(self, message: str, file_path: str | None = None):
        super().__init__(message, exit_code=1)
        self.file_path = file_path


class PDFProcessingError(PDF2MDError):
    """Raised when PDF processing fails.

    This includes cases like:
    - Corrupted PDF file
    - Unsupported PDF features
    - Parsing errors
    """

    def __init__(self, message: str, pdf_path: str | None = None):
        super().__init__(message, exit_code=2)
        self.pdf_path = pdf_path


class EncryptedPDFError(PDF2MDError):
    """Raised when attempting to process an encrypted PDF without password.

    This is a specific type of processing error with its own exit code
    to help users understand they need to decrypt the PDF first.
    """

    def __init__(
        self,
        message: str = "PDF is encrypted and requires a password",
        pdf_path: str | None = None,
    ):
        super().__init__(message, exit_code=3)
        self.pdf_path = pdf_path


class ResourceConstraintError(PDF2MDError):
    """Raised when system resource constraints prevent processing.

    This includes cases like:
    - Out of memory
    - Disk space insufficient
    - Processing timeout
    """

    def __init__(self, message: str, resource_type: str | None = None):
        super().__init__(message, exit_code=4)
        self.resource_type = resource_type  # "memory", "disk", "time", etc.


class OutputWriteError(PDF2MDError):
    """Raised when output file/directory operations fail.

    This includes cases like:
    - Permission denied on output directory
    - Disk full during write
    - Invalid output path
    """

    def __init__(self, message: str, output_path: str | None = None):
        super().__init__(message, exit_code=1)
        self.output_path = output_path


class DockerError(PDF2MDError):
    """Raised when Docker operations fail.

    This includes cases like:
    - Docker not available
    - Image not found
    - Container execution failure
    - Volume mount errors
    """

    def __init__(self, message: str, docker_command: str | None = None):
        super().__init__(message, exit_code=1)
        self.docker_command = docker_command


class ConfigurationError(PDF2MDError):
    """Raised when configuration is invalid or missing.

    This includes cases like:
    - Invalid command line arguments
    - Missing required configuration
    - Conflicting options
    """

    def __init__(self, message: str, config_key: str | None = None):
        super().__init__(message, exit_code=1)
        self.config_key = config_key


# Convenience functions for creating common errors


def invalid_pdf_file(file_path: str) -> InvalidInputError:
    """Create an InvalidInputError for non-PDF files."""
    return InvalidInputError(
        f"File is not a valid PDF: {file_path}. Only PDF files are supported.",
        file_path=file_path,
    )


def file_not_found(file_path: str) -> InvalidInputError:
    """Create an InvalidInputError for missing files."""
    return InvalidInputError(f"Input file not found: {file_path}", file_path=file_path)


def empty_file(file_path: str) -> InvalidInputError:
    """Create an InvalidInputError for empty files."""
    return InvalidInputError(
        f"Input file is empty: {file_path}. File size must be > 0 bytes.",
        file_path=file_path,
    )


def corrupted_pdf(file_path: str, details: str | None = None) -> PDFProcessingError:
    """Create a PDFProcessingError for corrupted PDFs."""
    message = f"PDF file appears to be corrupted: {file_path}"
    if details:
        message += f" ({details})"
    error = PDFProcessingError(message, pdf_path=file_path)
    error.details = details
    return error


def encrypted_pdf(file_path: str) -> EncryptedPDFError:
    """Create an EncryptedPDFError for password-protected PDFs."""
    return EncryptedPDFError(
        f"PDF is encrypted and requires a password: {file_path}. "
        f"Please decrypt the PDF first or provide the password.",
        pdf_path=file_path,
    )


def out_of_memory(details: str | None = None) -> ResourceConstraintError:
    """Create a ResourceConstraintError for memory issues."""
    message = "Insufficient memory to process PDF"
    if details:
        message += f": {details}"
    message += ". Try processing a smaller PDF or increase available memory."
    return ResourceConstraintError(message, resource_type="memory")


def disk_full(output_path: str) -> OutputWriteError:
    """Create an OutputWriteError for disk space issues."""
    return OutputWriteError(
        f"Insufficient disk space to write output: {output_path}",
        output_path=output_path,
    )


def permission_denied(path: str, operation: str = "access") -> OutputWriteError:
    """Create an OutputWriteError for permission issues."""
    return OutputWriteError(
        f"Permission denied to {operation}: {path}. Check file/directory permissions.",
        output_path=path,
    )


def docker_not_available() -> DockerError:
    """Create a DockerError when Docker is not available."""
    return DockerError(
        "Docker is not available. Please install Docker and ensure it's running."
    )


def docker_image_not_found(image_name: str) -> DockerError:
    """Create a DockerError when Docker image is not found."""
    return DockerError(
        f"Docker image not found: {image_name}. Please build or pull the image first."
    )


def invalid_arguments(message: str) -> ConfigurationError:
    """Create a ConfigurationError for invalid command line arguments."""
    return ConfigurationError(f"Invalid command line arguments: {message}")


def conflicting_options(option1: str, option2: str) -> ConfigurationError:
    """Create a ConfigurationError for conflicting options."""
    return ConfigurationError(
        f"Conflicting options: {option1} and {option2} cannot be used together."
    )
