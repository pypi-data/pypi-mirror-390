"""Command Line Interface for PDF2MD.

This module provides the CLI interface for the PDF to Markdown converter,
handling argument parsing, validation, and orchestrating the conversion process.
"""

import argparse
import os
import sys
from pathlib import Path
from typing import NoReturn

from . import __version__
from .exceptions import (
    EncryptedPDFError,
    PDF2MDError,
    PDFProcessingError,
    ResourceConstraintError,
)
from .models.conversion_config import ConversionConfig


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser."""
    parser = argparse.ArgumentParser(
        prog="pdf2md",
        description="PDF to Markdown Converter",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic conversion
  docker run --rm -v $(pwd):/work pdf2md:latest --input doc.pdf --output ./output

  # With progress and custom image format
  docker run --rm -v $(pwd):/work pdf2md:latest --input doc.pdf --output ./output --progress --format jpeg

For more information, visit: https://github.com/carloscasalar/pdf2md
        """.strip(),
    )

    # Required arguments
    parser.add_argument("--input", type=str, required=True, help="Input PDF file path")

    parser.add_argument(
        "--output", type=str, required=True, help="Output directory path"
    )

    # Optional arguments
    parser.add_argument(
        "--progress", action="store_true", help="Show progress during conversion"
    )

    parser.add_argument(
        "--format",
        type=str,
        choices=["png", "jpeg", "webp"],
        default="png",
        help="Image format (png|jpeg|webp, default: png)",
    )

    parser.add_argument(
        "--max-pages",
        type=int,
        default=0,
        help="Maximum pages to process (default: unlimited)",
    )

    parser.add_argument(
        "--timeout",
        type=int,
        default=None,
        help="Timeout in seconds for marker conversion (default: no timeout)",
    )

    parser.add_argument(
        "--quiet", action="store_true", help="Suppress output except errors"
    )

    parser.add_argument("--version", action="version", version=get_version_info())

    return parser


def get_version_info() -> str:
    """Get detailed version information."""
    try:
        import marker

        marker_version = getattr(marker, "__version__", "unknown")
    except ImportError:
        marker_version = "not installed"

    python_version = (
        f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    )
    platform = sys.platform

    return f"""pdf2md version {__version__}
Marker library version: {marker_version}
Python version: {python_version}
Platform: {platform}"""


def parse_arguments(args: list[str] | None = None) -> argparse.Namespace:
    """Parse command line arguments.

    Args:
        args: List of arguments to parse (defaults to sys.argv)

    Returns:
        Parsed arguments namespace

    Raises:
        SystemExit: On parsing error or help/version request
    """
    parser = create_parser()

    # Parse arguments
    parsed_args = parser.parse_args(args)

    # Validate arguments
    validate_arguments(parsed_args)

    return parsed_args


def validate_arguments(args: argparse.Namespace) -> None:
    """Validate parsed command line arguments.

    Args:
        args: Parsed arguments to validate

    Raises:
        SystemExit: On validation error
    """
    # Check for conflicting options
    if args.progress and args.quiet:
        print("Error: --progress and --quiet cannot be used together", file=sys.stderr)
        sys.exit(1)

    # Validate max-pages
    if args.max_pages < 0:
        print("Error: --max-pages must be >= 0", file=sys.stderr)
        sys.exit(1)

    # Validate timeout
    if args.timeout is not None and args.timeout <= 0:
        print("Error: --timeout must be > 0 (or omit for no timeout)", file=sys.stderr)
        sys.exit(1)

    # Convert relative paths to absolute
    # Only use /work prefix if we're running in a Docker container
    is_docker = (
        os.path.exists("/.dockerenv")
        or os.environ.get("CONTAINER", "").lower() == "true"
    )

    if not os.path.isabs(args.input):
        if is_docker:
            args.input = os.path.join("/work", args.input)
        else:
            args.input = os.path.abspath(args.input)

    if not os.path.isabs(args.output):
        if is_docker:
            args.output = os.path.join("/work", args.output)
        else:
            args.output = os.path.abspath(args.output)

    # Validate input file
    input_path = Path(args.input)

    if not input_path.exists():
        print(f"Error: Input file not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    if not input_path.is_file():
        print(f"Error: Input path is not a file: {args.input}", file=sys.stderr)
        sys.exit(1)

    if input_path.stat().st_size == 0:
        print(f"Error: Input file is empty: {args.input}", file=sys.stderr)
        sys.exit(1)

    if not input_path.suffix.lower() == ".pdf":
        print(
            f"Error: Input file must have .pdf extension: {args.input}", file=sys.stderr
        )
        sys.exit(1)


def create_conversion_config(args: argparse.Namespace) -> ConversionConfig:
    """Create ConversionConfig from parsed arguments.

    Args:
        args: Parsed command line arguments

    Returns:
        ConversionConfig object
    """
    # Auto-detect progress if not explicitly set
    progress_enabled = args.progress
    if not args.progress and not args.quiet:
        # Auto-enable progress if stderr is a TTY
        progress_enabled = sys.stderr.isatty()

    return ConversionConfig(
        input_path=args.input,
        output_dir=args.output,
        progress_enabled=progress_enabled and not args.quiet,
        image_format=args.format,
        max_pages=args.max_pages,
        quiet=args.quiet,
        extract_images=True,
        include_metadata=True,
        marker_timeout=args.timeout,
    )


def handle_conversion_error(error: Exception) -> NoReturn:
    """Handle conversion errors and exit with appropriate code.

    Args:
        error: Exception that occurred during conversion
    """
    if isinstance(error, EncryptedPDFError):
        print("Error: PDF is password-protected or encrypted", file=sys.stderr)
        print("This tool does not support encrypted PDFs.", file=sys.stderr)
        print("Please decrypt the PDF before processing.", file=sys.stderr)
        sys.exit(3)

    elif isinstance(error, ResourceConstraintError):
        print("Error: Insufficient resources", file=sys.stderr)
        if "memory" in error.message.lower():
            print("Out of memory during processing", file=sys.stderr)
        elif "disk" in error.message.lower():
            print("Insufficient disk space for output", file=sys.stderr)
        else:
            print(error.message, file=sys.stderr)
        sys.exit(4)

    elif isinstance(error, PDFProcessingError):
        print("Error: PDF processing failed", file=sys.stderr)
        print(error.message, file=sys.stderr)
        sys.exit(2)

    elif isinstance(error, PDF2MDError):
        print(f"Error: {error.message}", file=sys.stderr)
        sys.exit(error.exit_code)

    else:
        print("Error: Unexpected error occurred", file=sys.stderr)
        print(str(error), file=sys.stderr)
        sys.exit(1)


def print_success_summary(result, config: ConversionConfig) -> None:
    """Print conversion success summary.

    Args:
        result: Conversion result object
        config: Conversion configuration
    """
    if config.quiet:
        return

    # Print generated files
    print("Generated Files:")
    print(f"- {result.output_path} (main markdown content)")

    for image in result.images:
        print(f"- {image.output_path} ({image.alt_text or 'extracted image'})")

    if config.include_metadata:
        metadata_path = Path(config.output_dir) / "metadata.json"
        print(f"- {metadata_path} (processing statistics)")

    print()
    print("Processing completed successfully.")

    # Print processing statistics
    if result.metadata:
        metadata = result.metadata
        print(
            f"✓ Processed {metadata.pages_processed} pages in {metadata.processing_time:.1f}s"
        )
        if metadata.images_extracted > 0:
            print(f"✓ Extracted {metadata.images_extracted} images")
        if metadata.tables_found > 0 or metadata.equations_found > 0:
            print(
                f"✓ Converted {metadata.tables_found} tables and {metadata.equations_found} equations"
            )


def main(args: list[str] | None = None) -> NoReturn:
    """Main entry point for the CLI application.

    Args:
        args: Command line arguments (defaults to sys.argv)
    """
    try:
        # Parse arguments
        parsed_args = parse_arguments(args)

        # Create configuration
        config = create_conversion_config(parsed_args)

        # Import conversion components (delay import to avoid startup overhead)
        from .converter import PDFConverter
        from .progress import ProgressIndicator

        # Create progress indicator
        progress = None
        if config.progress_enabled:
            progress = ProgressIndicator.create(show_progress=True, quiet=config.quiet)

        # Create converter
        converter = PDFConverter(
            progress_callback=progress.update if progress else None,
            image_format=config.image_format,
            max_pages=config.max_pages,
            extract_images=config.extract_images,
            marker_timeout=config.marker_timeout,
        )

        # Perform conversion
        result = converter.convert(config.input_path, config.output_dir)

        # Clean up progress indicator
        if progress:
            if result.success:
                progress.finish("Conversion completed")
            else:
                progress.cleanup()

        # Handle result
        if result.success:
            print_success_summary(result, config)
            sys.exit(0)
        else:
            if result.error:
                handle_conversion_error(result.error)
            else:
                print(f"Error: {result.error_message}", file=sys.stderr)
                sys.exit(2)

    except KeyboardInterrupt:
        print("\nError: Process interrupted by user", file=sys.stderr)
        sys.exit(1)

    except Exception as e:
        handle_conversion_error(e)


if __name__ == "__main__":
    main()
