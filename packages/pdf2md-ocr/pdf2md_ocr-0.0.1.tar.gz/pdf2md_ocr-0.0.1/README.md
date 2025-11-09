# PDF2MD Docker

Docker-based PDF to Markdown converter using Marker AI.

## Features

- Convert PDF documents to high-quality Markdown
- Extract images and preserve document structure
- Multi-architecture Docker support (amd64, arm64)
- Security-first design with non-root execution
- Optimized uv-based image for fast builds and minimal attack surface

## Development Status

This project is currently in active development. Core functionality is implemented but some features are still being finalized. The Docker image and basic PDF conversion capabilities are functional, while comprehensive testing and advanced features are being completed.

## Installation Options

You can use pdf2md in three ways:

### Option 1: Global Installation with uvx (Recommended for Simple Use)

```bash
# Install and run in one command (no local setup needed)
uvx pdf2md-ocr --version

# Convert a PDF
uvx pdf2md-ocr --input document.pdf --output ./output
```

**Advantages**: No Docker required, no local installation needed, automatic version management, isolated environment.

### Option 2: Local Installation with pip

```bash
# Install globally
pip install pdf2md-ocr

# Now use the command directly
pdf2md-ocr --version
pdf2md-ocr --input document.pdf --output ./output
```

**Requirements**: Python 3.13+

### Option 3: Docker Container (Best for Production)

```bash
# Build the image
make build

# Run with Docker
docker run --rm \
  -v $(pwd):/work \
  pdf2md:latest \
  --input /work/document.pdf \
  --output /work/output/
```

**Advantages**: Consistent environment, reproducible builds, no Python version conflicts, works on any OS.

## Quick Start

```bash
# Build the Docker image
make build

# Convert a PDF (basic usage)
docker run --rm \
  -v $(pwd)/sample:/app/sample \
  pdf2md:latest \
  --input sample/document.pdf \
  --output sample/

# Convert with model cache (recommended for multiple runs)
make run-with-cache
```

## Model Cache (Recommended)

The marker library downloads large ML models (~1.5GB) on first run. To avoid re-downloading:

```bash
# Use persistent model cache (saves time on subsequent runs)
make run-with-cache

# Or manually with Docker:
mkdir -p model-cache
docker run --rm \
  -v $(pwd)/sample:/app/sample \
  -v $(pwd)/model-cache:/home/appuser/.cache \
  pdf2md:latest \
  --input sample/document.pdf \
  --output sample/

# Clean model cache when needed (frees ~1.5GB)
make clean-models
```

## Docker Image

The project provides a single optimized Docker image built with uv and Python 3.13 for fast builds and optimal performance:

- **Base**: `ghcr.io/astral-sh/uv:python3.13-bookworm-slim`
- **Size**: Optimized with uv's efficient dependency management
- **Security**: Non-root execution (UID 1000)
- **Architecture**: Multi-platform (amd64, arm64)
- **Performance**: Latest Python 3.13 with uv for fast startup

### Available Commands

```bash
# Show version information
docker run --rm pdf2md:latest --version

# Show help
docker run --rm pdf2md:latest --help

# Convert PDF with model cache
make run-with-cache

# Development with shell access
make dev-with-cache
```

## CLI Options

### Required Arguments

- `--input`: Input PDF file path
- `--output`: Output directory path (where markdown and images will be saved)

### Optional Arguments

- `--progress`: Show progress bar during conversion
- `--format`: Image format for extracted images (png|jpeg|webp, default: png)
- `--max-pages`: Maximum number of pages to process (default: unlimited, 0 = no limit)
- `--quiet`: Suppress all output except errors
- `--version`: Show detailed version information
- `--help`: Display help message and usage examples

### Usage Examples

```bash
# Basic conversion with progress
docker run --rm \
  -v $(pwd)/sample:/app/sample \
  pdf2md:latest \
  --input sample/document.pdf \
  --output sample/ \
  --progress

# Convert with custom image format and page limit
docker run --rm \
  -v $(pwd)/sample:/app/sample \
  pdf2md:latest \
  --input sample/document.pdf \
  --output sample/ \
  --format jpeg \
  --max-pages 10

# Quiet conversion (minimal output)
docker run --rm \
  -v $(pwd)/sample:/app/sample \
  pdf2md:latest \
  --input sample/document.pdf \
  --output sample/ \
  --quiet
```

### Makefile Commands

```bash
make help              # Show all available commands
make build             # Build Docker image
make run-with-cache    # Run with persistent model cache
make dev-with-cache    # Development container with cache
make clean-models      # Remove cached models (frees ~1.5GB)
make clean-all         # Clean everything including models
```

## Development

### Building Locally

```bash
# Build standard image
make build

# Run tests
make test

# Clean up
make clean

# Clean everything including models
make clean-all
```

### Testing

```bash
# Run all tests
make test

# Test locally with uv
make test-local

# Check image size
make size-check
```

### Continuous Integration

The project uses GitHub Actions for comprehensive CI/CD:

#### Pipeline Features

- **Python 3.13 Testing**: Comprehensive testing with pinned dependencies
- **Code Quality**: Linting with Ruff, format checking, and optional type checking
- **Test Coverage**: Comprehensive coverage reporting with Codecov integration
- **Docker Validation**: Automated Docker image builds and testing
- **Dependency Security**: Consistency checks and vulnerability scanning
- **Constitutional Compliance**: Enforces dependency pinning and test coverage policies

#### Triggers

- **Push to main/master**: Full pipeline on every commit
- **Pull Requests**: Complete validation before merge
- **Dependency Changes**: Automatic lockfile validation

#### Local CI Validation

```bash
# Run the same checks as CI locally
uv run ruff check .
uv run ruff format --check .
uv run pytest --cov=src/pdf2md --cov-report=term-missing
cd docker && ./build.sh && ./test.sh
```

The CI pipeline ensures all changes maintain code quality, test coverage, and Docker functionality before integration.

### Performance Tests (opt-in)

Performance tests are skipped by default. To enable locally:

```bash
PDF2MD_PERF=1 uv run pytest -m performance -v
```

### Exit Codes

- 0: Success
- 1: General error (invalid arguments, file errors)
- 2: PDF processing error (corrupted/unsupported)
- 3: Encrypted PDF (not supported)
- 4: Resource constraints (memory/disk)

### Quickstart Validation

After building, validate quickstart:

```bash
docker run --rm pdf2md:latest --help
docker run --rm pdf2md:latest --version
```

## Requirements

- Docker Engine 20.10+ or Docker Desktop
- **At least 6GB RAM available to Docker** (marker models require ~4-5GB)
- Sufficient disk space for input/output files and model cache (~1.5GB)

### Memory Requirements

The marker library loads large ML models (~1.4GB) that require significant memory during processing:

- **Docker Memory**: Increase Docker Desktop memory to at least 6GB
- **System Memory**: 8GB+ total RAM recommended
- **Model Cache**: ~1.5GB disk space for cached models

To increase Docker memory on macOS:

1. Open Docker Desktop
2. Go to Settings → Resources → Memory
3. Increase to 6GB or higher
4. Apply & Restart

## Development Roadmap

This project follows a **quarterly release schedule**. Here's what's planned:

### Current Phase: Pre-Release (v0.0.1)

**Status**: Active development  
**Release**: October 2025

- ✅ PyPI distribution via pip and uvx
- ✅ Semantic versioning system established
- ✅ GitHub Actions CI/CD automation
- ✅ Docker multi-architecture support

### v0.0.2 (Planned: Q1 2026 - January 31)

**Focus**: Enhanced CLI and observability

- [ ] Add `--verbose` option for debugging output
- [ ] Improve progress reporting with detailed metrics
- [ ] Add batch processing capability
- [ ] Enhanced error messages with solutions

### v0.1.0 (Planned: Q2 2026 - April 30)

**Focus**: Stable foundation

- [ ] Stable feature set and CLI interface
- [ ] Comprehensive documentation
- [ ] Performance optimizations
- [ ] Extended test coverage (>80%)

### v1.0.0 (Planned: Q3 2026 - July 31)

**Focus**: Production-ready release

- [ ] Guaranteed backward compatibility (semver)
- [ ] Long-term support commitment
- [ ] Performance benchmarks
- [ ] Production deployment guide

## Known Limitations

The following limitations are planned for future improvements:

- **PDF Analysis**: Currently uses basic page count detection; advanced analysis planned
- **Observability**: No `--verbose` flag; detailed debugging planned for v0.0.2
- **Image Extraction**: Basic implementation; enhanced format support planned
- **Progress Reporting**: Needs refinement; improved metrics planned for v0.0.2
- **Batch Processing**: Single-file at a time; bulk processing planned for v0.0.2

## Resources & Links

- **PyPI Package**: https://pypi.org/project/pdf2md-ocr/
- **GitHub Releases**: https://github.com/carloscasalar/pdf2md/releases
- **Changelog**: [CHANGELOG.md](CHANGELOG.md)
- **Release Process**: [RELEASE_PROCESS.md](RELEASE_PROCESS.md)
- **Report Issues**: https://github.com/carloscasalar/pdf2md/issues

## Licensing

- Source code in this repository: MIT License (see `LICENSE`).
- Docker image distribution: includes GPL-licensed software (Marker / marker-pdf). Distribution of the image must comply with GPL requirements. See `licenses/GPL-3.0.txt` and `THIRD_PARTY_NOTICES.md`.
- Model weights used by Marker are subject to a modified OpenRAIL-M license, which may restrict commercial use beyond certain revenue/funding thresholds. Ensure your usage complies with those terms.

If you prefer to avoid GPL obligations in your own distribution, do not redistribute a container that bundles Marker; instead, instruct users to install Marker themselves or call a separate service.
