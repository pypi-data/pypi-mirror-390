"""File system utilities for PDF2MD.

This module provides utility functions for file validation, path normalization,
cleanup operations, and other file system related tasks.
"""

import hashlib
import mimetypes
import os
import shutil
import tempfile
from collections.abc import Generator
from pathlib import Path

from .exceptions import InvalidInputError, OutputWriteError


def validate_pdf_file(file_path: str | Path) -> Path:
    """Validate that a file is a readable PDF.

    Args:
        file_path: Path to PDF file

    Returns:
        Validated Path object

    Raises:
        InvalidInputError: If file is invalid
    """
    path = Path(file_path).resolve()

    # Check existence
    if not path.exists():
        raise InvalidInputError(f"File not found: {path}")

    # Check it's a file
    if not path.is_file():
        raise InvalidInputError(f"Path is not a file: {path}")

    # Check extension
    if path.suffix.lower() != ".pdf":
        raise InvalidInputError(f"File must have .pdf extension: {path}")

    # Check file size
    if path.stat().st_size == 0:
        raise InvalidInputError(f"File is empty: {path}")

    # Basic PDF format validation
    try:
        with open(path, "rb") as f:
            header = f.read(8)
            if not header.startswith(b"%PDF-"):
                raise InvalidInputError(f"File is not a valid PDF: {path}")
    except OSError as e:
        raise InvalidInputError(f"Cannot read file: {path} ({e})")

    return path


def ensure_output_directory(output_path: str | Path, create: bool = True) -> Path:
    """Ensure output directory exists and is writable.

    Args:
        output_path: Path to output directory
        create: Whether to create directory if it doesn't exist

    Returns:
        Validated Path object

    Raises:
        OutputWriteError: If directory cannot be created or is not writable
    """
    path = Path(output_path).resolve()

    if path.exists():
        if not path.is_dir():
            raise OutputWriteError(f"Output path is not a directory: {path}")

        # Check if writable
        if not os.access(path, os.W_OK):
            raise OutputWriteError(f"Output directory is not writable: {path}")

    elif create:
        try:
            path.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            raise OutputWriteError(f"Cannot create output directory: {path} ({e})")

    else:
        raise OutputWriteError(f"Output directory does not exist: {path}")

    return path


def normalize_path(path: str | Path, base_path: str | Path | None = None) -> Path:
    """Normalize a file path.

    Args:
        path: Path to normalize
        base_path: Base path for relative paths

    Returns:
        Normalized absolute Path object
    """
    path_obj = Path(path)

    # Handle relative paths
    if not path_obj.is_absolute() and base_path:
        path_obj = Path(base_path) / path_obj

    return path_obj.resolve()


def safe_filename(filename: str, max_length: int = 255) -> str:
    """Create a safe filename by removing/replacing invalid characters.

    Args:
        filename: Original filename
        max_length: Maximum filename length

    Returns:
        Safe filename
    """
    # Remove/replace invalid characters
    invalid_chars = '<>:"/\\|?*'
    safe_name = filename

    for char in invalid_chars:
        safe_name = safe_name.replace(char, "_")

    # Remove control characters
    safe_name = "".join(char for char in safe_name if ord(char) >= 32)

    # Trim to max length
    if len(safe_name) > max_length:
        name_part, ext = os.path.splitext(safe_name)
        max_name_length = max_length - len(ext)
        safe_name = name_part[:max_name_length] + ext

    # Ensure not empty
    if not safe_name or safe_name.startswith("."):
        safe_name = f"file_{hash(filename) % 10000}{Path(filename).suffix}"

    return safe_name


def calculate_file_hash(file_path: str | Path, algorithm: str = "sha256") -> str:
    """Calculate hash of a file.

    Args:
        file_path: Path to file
        algorithm: Hash algorithm ('md5', 'sha1', 'sha256')

    Returns:
        Hex digest of file hash
    """
    hash_func = hashlib.new(algorithm)

    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            hash_func.update(chunk)

    return hash_func.hexdigest()


def get_file_info(file_path: str | Path) -> dict:
    """Get comprehensive file information.

    Args:
        file_path: Path to file

    Returns:
        Dictionary with file information
    """
    path = Path(file_path)
    stat = path.stat()

    return {
        "path": str(path.resolve()),
        "name": path.name,
        "stem": path.stem,
        "suffix": path.suffix,
        "size": stat.st_size,
        "modified": stat.st_mtime,
        "created": stat.st_ctime,
        "is_file": path.is_file(),
        "is_dir": path.is_dir(),
        "exists": path.exists(),
        "mime_type": mimetypes.guess_type(str(path))[0],
    }


def find_files(
    directory: str | Path, pattern: str = "*", recursive: bool = True
) -> Generator[Path]:
    """Find files matching a pattern.

    Args:
        directory: Directory to search
        pattern: Glob pattern to match
        recursive: Whether to search recursively

    Yields:
        Path objects for matching files
    """
    dir_path = Path(directory)

    if recursive:
        yield from dir_path.rglob(pattern)
    else:
        yield from dir_path.glob(pattern)


def copy_file_safely(
    src: str | Path, dst: str | Path, preserve_metadata: bool = True
) -> Path:
    """Copy file with error handling.

    Args:
        src: Source file path
        dst: Destination file path
        preserve_metadata: Whether to preserve file metadata

    Returns:
        Path to copied file

    Raises:
        InvalidInputError: If source file is invalid
        OutputWriteError: If copy operation fails
    """
    src_path = Path(src)
    dst_path = Path(dst)

    # Validate source
    if not src_path.exists():
        raise InvalidInputError(f"Source file not found: {src_path}")

    if not src_path.is_file():
        raise InvalidInputError(f"Source is not a file: {src_path}")

    # Ensure destination directory exists
    dst_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        if preserve_metadata:
            shutil.copy2(src_path, dst_path)
        else:
            shutil.copy(src_path, dst_path)

        return dst_path.resolve()

    except OSError as e:
        raise OutputWriteError(f"Failed to copy file: {e}")


def move_file_safely(src: str | Path, dst: str | Path) -> Path:
    """Move file with error handling.

    Args:
        src: Source file path
        dst: Destination file path

    Returns:
        Path to moved file

    Raises:
        InvalidInputError: If source file is invalid
        OutputWriteError: If move operation fails
    """
    src_path = Path(src)
    dst_path = Path(dst)

    # Validate source
    if not src_path.exists():
        raise InvalidInputError(f"Source file not found: {src_path}")

    # Ensure destination directory exists
    dst_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        shutil.move(str(src_path), str(dst_path))
        return dst_path.resolve()

    except OSError as e:
        raise OutputWriteError(f"Failed to move file: {e}")


def cleanup_directory(
    directory: str | Path, pattern: str = "*", exclude_patterns: list[str] | None = None
) -> int:
    """Clean up files in directory matching pattern.

    Args:
        directory: Directory to clean
        pattern: Pattern for files to remove
        exclude_patterns: Patterns for files to keep

    Returns:
        Number of files removed
    """
    dir_path = Path(directory)

    if not dir_path.exists():
        return 0

    exclude_patterns = exclude_patterns or []
    removed_count = 0

    for file_path in dir_path.glob(pattern):
        if file_path.is_file():
            # Check if file should be excluded
            should_exclude = False
            for exclude_pattern in exclude_patterns:
                if file_path.match(exclude_pattern):
                    should_exclude = True
                    break

            if not should_exclude:
                try:
                    file_path.unlink()
                    removed_count += 1
                except OSError:
                    # Best effort cleanup - continue even if some files can't be removed
                    pass

    return removed_count


def get_directory_size(directory: str | Path) -> int:
    """Get total size of directory contents.

    Args:
        directory: Directory path

    Returns:
        Total size in bytes
    """
    total_size = 0
    dir_path = Path(directory)

    if not dir_path.exists():
        return 0

    for file_path in dir_path.rglob("*"):
        if file_path.is_file():
            try:
                total_size += file_path.stat().st_size
            except OSError:
                # Skip files we can't stat (permissions, etc.)
                pass

    return total_size


def create_temp_directory(prefix: str = "pdf2md_", cleanup: bool = True) -> Path:
    """Create temporary directory.

    Args:
        prefix: Prefix for directory name
        cleanup: Whether to register for cleanup on exit

    Returns:
        Path to temporary directory
    """
    temp_dir = Path(tempfile.mkdtemp(prefix=prefix))

    if cleanup:
        import atexit

        atexit.register(lambda: shutil.rmtree(temp_dir, ignore_errors=True))

    return temp_dir


def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format.

    Args:
        size_bytes: Size in bytes

    Returns:
        Formatted size string
    """
    if size_bytes == 0:
        return "0 B"

    units = ["B", "KB", "MB", "GB", "TB"]
    unit_index = 0
    size = float(size_bytes)

    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024
        unit_index += 1

    if unit_index == 0:
        return f"{int(size)} {units[unit_index]}"
    else:
        return f"{size:.1f} {units[unit_index]}"


class TempFileManager:
    """Context manager for temporary file operations."""

    def __init__(self, prefix: str = "pdf2md_"):
        """Initialize temp file manager.

        Args:
            prefix: Prefix for temporary files/directories
        """
        self.prefix = prefix
        self.temp_paths: list[Path] = []

    def create_temp_file(self, suffix: str = "", content: bytes = b"") -> Path:
        """Create temporary file.

        Args:
            suffix: File suffix
            content: Initial file content

        Returns:
            Path to temporary file
        """
        fd, temp_path = tempfile.mkstemp(prefix=self.prefix, suffix=suffix)
        temp_path_obj = Path(temp_path)

        try:
            with os.fdopen(fd, "wb") as f:
                f.write(content)
        except OSError:
            # Clean up file descriptor if write fails
            os.close(fd)
            raise

        self.temp_paths.append(temp_path_obj)
        return temp_path_obj

    def create_temp_dir(self) -> Path:
        """Create temporary directory.

        Returns:
            Path to temporary directory
        """
        temp_dir = Path(tempfile.mkdtemp(prefix=self.prefix))
        self.temp_paths.append(temp_dir)
        return temp_dir

    def cleanup(self):
        """Clean up all temporary files and directories."""
        for path in self.temp_paths:
            try:
                if path.is_file():
                    path.unlink()
                elif path.is_dir():
                    shutil.rmtree(path)
            except OSError:
                # Best effort cleanup - continue even if some paths can't be removed
                pass

        self.temp_paths.clear()

    def __enter__(self):
        """Enter context manager."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context manager with cleanup."""
        self.cleanup()
