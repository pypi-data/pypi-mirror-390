# LeapOCR Python SDK

[![PyPI version](https://badge.fury.io/py/leapocr.svg)](https://badge.fury.io/py/leapocr)
[![Python Support](https://img.shields.io/pypi/pyversions/leapocr.svg)](https://pypi.org/project/leapocr/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Official Python SDK for [LeapOCR](https://www.leapocr.com/) - Transform documents into structured data using AI-powered OCR.

## Overview

LeapOCR provides enterprise-grade document processing with AI-powered data extraction. This SDK offers a Python-native, async-first interface for seamless integration into your applications.

## Installation

```bash
pip install leapocr
```

Or using [uv](https://github.com/astral-sh/uv):

```bash
uv add leapocr
```

## Quick Start

### Prerequisites

- Python 3.9 or higher
- LeapOCR API key ([sign up here](https://www.leapocr.com/signup))

### Basic Example

```python
import asyncio
import os
from leapocr import LeapOCR, ProcessOptions, Format

async def main():
    # Initialize the SDK with your API key
    async with LeapOCR(os.getenv("LEAPOCR_API_KEY")) as client:
        # Process a document and wait for completion
        result = await client.ocr.process_and_wait(
            "https://example.com/document.pdf",
            options=ProcessOptions(
                format=Format.STRUCTURED,
            ),
        )

        print(f"Credits used: {result.credits_used}")
        print(f"Pages processed: {len(result.pages)}")
        print(f"Extracted text: {result.pages[0].text[:200]}...")

asyncio.run(main())
```

## Key Features

- **Async-First Design** - Built on asyncio with httpx for high-performance concurrent processing
- **Type-Safe API** - Full type hints and mypy strict mode support
- **Multiple Processing Formats** - Structured data extraction, markdown output, or per-page processing
- **Flexible Model Selection** - Choose from standard, pro, or custom AI models
- **Custom Schema Support** - Define extraction schemas for your specific use case
- **Built-in Retry Logic** - Automatic exponential backoff for transient failures
- **Context Manager Support** - Proper resource cleanup with async context managers
- **Direct File Upload** - Efficient multipart uploads for local files
- **Progress Tracking** - Real-time callbacks for long-running operations

## Processing Models

| Model               | Use Case                  | Credits/Page | Priority |
| ------------------- | ------------------------- | ------------ | -------- |
| `Model.STANDARD_V1` | General purpose (default) | 1            | 1        |

Use the `model` parameter in `ProcessOptions` to specify a model. Defaults to `Model.STANDARD_V1`.

## Usage Examples

### Processing from URL

```python
import asyncio
from leapocr import LeapOCR, ProcessOptions, Format, Model

async def process_url():
    async with LeapOCR("your-api-key") as client:
        result = await client.ocr.process_and_wait(
            "https://example.com/invoice.pdf",
            options=ProcessOptions(
                format=Format.STRUCTURED,
                model=Model.STANDARD_V1,
                instructions="Extract invoice number, date, and total amount",
            ),
        )

        print(f"Processing time: {result.processing_time_seconds:.2f}s")
        print(f"Credits used: {result.credits_used}")
        print(f"Pages: {len(result.pages)}")

asyncio.run(process_url())
```

### Processing Local Files

```python
from pathlib import Path

async def process_file():
    async with LeapOCR("your-api-key") as client:
        result = await client.ocr.process_and_wait(
            Path("invoice.pdf"),
            options=ProcessOptions(
                format=Format.STRUCTURED,
                model=Model.STANDARD_V1,
            ),
        )

        for page in result.pages:
            print(f"Page {page.page_number}: {len(page.text)} characters")

asyncio.run(process_file())
```

### Custom Schema Extraction

```python
async def extract_with_schema():
    schema = {
        "type": "object",
        "properties": {
            "patient_name": {"type": "string"},
            "date_of_birth": {"type": "string"},
            "medications": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "dosage": {"type": "string"},
                    },
                },
            },
        },
    }

    async with LeapOCR("your-api-key") as client:
        result = await client.ocr.process_and_wait(
            "medical-record.pdf",
            options=ProcessOptions(
                format=Format.STRUCTURED,
                schema=schema,
                instructions="Extract patient information and medications",
            ),
        )

        # Parse the structured data
        import json
        data = json.loads(result.pages[0].text)
        print(f"Patient: {data['patient_name']}")
        print(f"Medications: {len(data['medications'])}")

asyncio.run(extract_with_schema())
```

### Output Formats

| Format                       | Description        | Use Case                                       |
| ---------------------------- | ------------------ | ---------------------------------------------- |
| `Format.STRUCTURED`          | Single JSON object | Extract specific fields across entire document |
| `Format.MARKDOWN`            | Text per page      | Convert document to readable text              |
| `Format.PER_PAGE_STRUCTURED` | JSON per page      | Extract fields from multi-section documents    |

### Manual Job Management

```python
async def manual_polling():
    async with LeapOCR("your-api-key") as client:
        # Start processing
        job = await client.ocr.process_url(
            "https://example.com/document.pdf",
            options=ProcessOptions(format=Format.MARKDOWN),
        )

        print(f"Job created: {job.job_id}")

        # Poll for status
        import asyncio
        while True:
            status = await client.ocr.get_job_status(job.job_id)
            print(f"Status: {status.status.value} - {status.progress:.1f}%")

            if status.status.value == "completed":
                break

            await asyncio.sleep(2)

        # Get results
        result = await client.ocr.get_results(job.job_id)
        print(f"Processing complete: {len(result.pages)} pages")

asyncio.run(manual_polling())
```

### Progress Tracking

```python
from leapocr import PollOptions

async def track_progress():
    def progress_callback(status):
        print(f"Progress: {status.progress:.1f}% "
              f"({status.processed_pages}/{status.total_pages} pages)")

    async with LeapOCR("your-api-key") as client:
        result = await client.ocr.process_and_wait(
            "large-document.pdf",
            poll_options=PollOptions(
                poll_interval=2.0,
                max_wait=300.0,
                on_progress=progress_callback,
            ),
        )

asyncio.run(track_progress())
```

### Concurrent Batch Processing

```python
async def batch_process():
    urls = [
        "https://example.com/doc1.pdf",
        "https://example.com/doc2.pdf",
        "https://example.com/doc3.pdf",
    ]

    async with LeapOCR("your-api-key") as client:
        # Process all documents concurrently
        tasks = [
            client.ocr.process_and_wait(url)
            for url in urls
        ]
        results = await asyncio.gather(*tasks)

        total_credits = sum(r.credits_used for r in results)
        total_pages = sum(len(r.pages) for r in results)

        print(f"Processed {len(results)} documents")
        print(f"Total credits: {total_credits}")
        print(f"Total pages: {total_pages}")

asyncio.run(batch_process())
```

For more examples, see the [`examples/`](./examples) directory.

## Configuration

### Custom Configuration

```python
from leapocr import LeapOCR, ClientConfig

config = ClientConfig(
    base_url="https://api.leapocr.com/api/v1",
    timeout=120.0,
    max_retries=5,
    retry_delay=2.0,
    retry_multiplier=2.0,
)

async with LeapOCR("your-api-key", config) as client:
    # Use client with custom configuration
    pass
```

### Environment Variables

```bash
export LEAPOCR_API_KEY="your-api-key"
export OCR_BASE_URL="https://api.leapocr.com/api/v1"  # optional
```

## Error Handling

The SDK provides a comprehensive error hierarchy for robust error handling:

```python
from leapocr import (
    LeapOCRError,
    AuthenticationError,
    ValidationError,
    APIError,
    JobError,
    NetworkError,
)

async def handle_errors():
    try:
        async with LeapOCR("your-api-key") as client:
            result = await client.ocr.process_and_wait("document.pdf")

    except AuthenticationError as e:
        print(f"Authentication failed: {e.message}")

    except ValidationError as e:
        print(f"Invalid input: {e.message}")
        if e.field:
            print(f"  Field: {e.field}")

    except JobError as e:
        print(f"Job failed: {e.message}")
        print(f"  Job ID: {e.job_id}")

    except NetworkError as e:
        print(f"Network error: {e.message}")
        # Implement retry logic

    except APIError as e:
        print(f"API error: {e.message}")
        print(f"  Status code: {e.status_code}")

    except LeapOCRError as e:
        print(f"SDK error: {e.message}")

asyncio.run(handle_errors())
```

### Error Types

- `LeapOCRError` - Base class for all SDK errors
- `AuthenticationError` - Invalid or missing API key
- `RateLimitError` - Rate limit exceeded
- `ValidationError` - Invalid input parameters
- `FileError` - File-related errors (not found, too large, etc.)
- `JobError` - Job processing errors
- `JobFailedError` - Job processing failed
- `JobTimeoutError` - Job processing timed out
- `NetworkError` - Network connectivity issues
- `APIError` - API returned an error response
- `InsufficientCreditsError` - Not enough credits

## API Reference

### Core Classes

#### `LeapOCR`

Main client class for interacting with the LeapOCR API.

```python
class LeapOCR:
    def __init__(self, api_key: str, config: ClientConfig | None = None)
    async def close(self) -> None
    async def health(self) -> bool

    # Use as async context manager
    async with LeapOCR(api_key) as client:
        ...
```

#### `OCRService`

OCR operations service accessible via `client.ocr`.

```python
# Process and wait for completion (convenience method)
async def process_and_wait(
    file: str | Path | BinaryIO,
    options: ProcessOptions | None = None,
    poll_options: PollOptions | None = None,
) -> JobResult

# Process file or URL
async def process_file(
    file: str | Path | BinaryIO,
    options: ProcessOptions | None = None,
) -> ProcessResult

async def process_url(
    url: str,
    options: ProcessOptions | None = None,
) -> ProcessResult

# Job management
async def get_job_status(job_id: str) -> JobStatus
async def get_results(job_id: str, page: int = 1, limit: int = 100) -> JobResult
```

### Data Models

#### `ProcessOptions`

```python
@dataclass
class ProcessOptions:
    format: Format = Format.STRUCTURED
    model: Model | None = None
    schema: dict[str, Any] | None = None
    instructions: str | None = None
    template_id: str | None = None
    metadata: dict[str, str] = field(default_factory=dict)
```

#### `PollOptions`

```python
@dataclass
class PollOptions:
    poll_interval: float = 2.0  # seconds
    max_wait: float = 300.0  # seconds (5 minutes)
    on_progress: Callable[[JobStatus], None] | None = None
```

#### `ClientConfig`

```python
@dataclass
class ClientConfig:
    base_url: str = "https://api.leapocr.com/api/v1"
    timeout: float = 30.0
    max_retries: int = 3
    retry_delay: float = 1.0
    retry_multiplier: float = 2.0
```

## Development

### Prerequisites

- Python 3.9+
- [uv](https://github.com/astral-sh/uv) (recommended) or pip
- [OpenAPI Generator](https://openapi-generator.tech/) (for code generation)
- Java 21+ (for OpenAPI Generator)

### Setup

```bash
# Clone the repository
git clone https://github.com/leapocr/leapocr-python.git
cd leapocr-python

# Install dependencies
make dev-install

# Or using uv directly
uv sync
```

### Common Tasks

```bash
make test               # Run unit tests
make test-cov           # Run tests with coverage
make test-integration   # Run integration tests (requires API key)
make lint               # Run linters
make format             # Format code
make type-check         # Run type checking
make check              # Run all checks (format, lint, type-check)
```

### Code Generation

The SDK includes generated client code from the OpenAPI specification:

```bash
make fetch-spec         # Download OpenAPI spec
make generate           # Generate client code
make regenerate         # Fetch + generate (full refresh)
```

### Running Tests

```bash
# Unit tests only
pytest tests/unit/

# Integration tests (requires API key)
export LEAPOCR_API_KEY="your-api-key"
pytest tests/integration/

# All tests with coverage
pytest tests/ --cov=leapocr --cov-report=html
```

### Project Structure

```
leapocr-python/
   leapocr/               # Main package
      __init__.py        # Public API
      client.py          # Main client class
      ocr.py             # OCR service
      models.py          # Data models
      errors.py          # Error classes
      config.py          # Configuration
      _internal/         # Internal utilities
         retry.py       # Retry logic
         upload.py      # File upload
         polling.py     # Status polling
         validation.py  # Input validation
         utils.py       # Common utilities
      generated/         # Generated OpenAPI client
   tests/
      unit/              # Unit tests
      integration/       # Integration tests
   examples/              # Usage examples
   scripts/               # Development scripts
   Makefile               # Common development tasks
```

## Contributing

We welcome contributions! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Code Standards

- Follow PEP 8 style guide
- Add type hints for all functions
- Write docstrings for public APIs
- Add tests for new features
- Update documentation as needed

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support & Resources

- **Documentation**: [docs.leapocr.com](https://docs.leapocr.com)
- **API Reference**: [API Documentation](https://docs.leapocr.com/api)
- **Issues**: [GitHub Issues](https://github.com/leapocr/leapocr-python/issues)
- **Examples**: [examples/](./examples)
- **Website**: [leapocr.com](https://www.leapocr.com)
- **Support**: support@leapocr.com

---

**Version**: 0.1.0
