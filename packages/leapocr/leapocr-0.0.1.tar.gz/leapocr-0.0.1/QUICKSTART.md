# LeapOCR Python SDK - Quick Start Guide

## Installation

```bash
# Using uv (recommended)
uv add leapocr

# Using pip
pip install leapocr
```

## Basic Usage

```python
import asyncio
from leapocr import LeapOCR, ProcessOptions, Format

async def main():
    # Initialize client
    async with LeapOCR("your-api-key") as client:
        # Process a document and wait for results
        result = await client.ocr.process_and_wait(
            "document.pdf",
            options=ProcessOptions(format=Format.MARKDOWN)
        )

        # Access results
        print(f"Processed {result.total_pages} pages")
        for page in result.pages:
            print(f"Page {page.page_number}: {page.text[:100]}...")

asyncio.run(main())
```

## Direct Upload Flow

The SDK handles the 3-step upload process automatically:

```python
async with LeapOCR("api-key") as client:
    # Step 1: Client calculates file size
    # Step 2: Client initiates upload → gets presigned URLs
    # Step 3: Client uploads to S3 → gets ETags
    # Step 4: Client completes upload → triggers processing
    # Step 5: Client polls for completion
    result = await client.ocr.process_and_wait("large_file.pdf")
```

### Manual Flow (Advanced)

```python
async with LeapOCR("api-key") as client:
    # Submit file for processing
    job = await client.ocr.process_file("document.pdf")
    print(f"Job ID: {job.job_id}")

    # Poll for status manually
    while True:
        status = await client.ocr.get_job_status(job.job_id)
        print(f"Status: {status.status}, Progress: {status.progress}%")

        if status.status == "completed":
            break

        await asyncio.sleep(2)

    # Get results
    result = await client.ocr.get_results(job.job_id)
```

## URL Processing

```python
async with LeapOCR("api-key") as client:
    # Process from URL (PDF only)
    result = await client.ocr.process_and_wait(
        url="https://example.com/document.pdf",
        options=ProcessOptions(format=Format.STRUCTURED)
    )
```

## Structured Data Extraction

```python
from leapocr import ProcessOptions, Format

# Define schema for extraction
schema = {
    "type": "object",
    "properties": {
        "invoice_number": {"type": "string"},
        "total_amount": {"type": "number"},
        "vendor_name": {"type": "string"},
        "line_items": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "description": {"type": "string"},
                    "amount": {"type": "number"}
                }
            }
        }
    }
}

async with LeapOCR("api-key") as client:
    result = await client.ocr.process_and_wait(
        "invoice.pdf",
        options=ProcessOptions(
            format=Format.STRUCTURED,
            schema=schema,
            instructions="Extract invoice details"
        )
    )

    # Access structured data
    data = result.pages[0].text  # JSON string with extracted data
```

## Batch Processing

```python
async with LeapOCR("api-key") as client:
    files = ["doc1.pdf", "doc2.pdf", "doc3.pdf"]

    # Submit all files
    jobs = []
    for file in files:
        job = await client.ocr.process_file(file)
        jobs.append(job)

    # Wait for all to complete
    results = []
    for job in jobs:
        result = await client.ocr.process_and_wait(job.job_id)
        results.append(result)
```

## Error Handling

```python
from leapocr import (
    LeapOCR,
    AuthenticationError,
    RateLimitError,
    FileError,
    JobFailedError,
    JobTimeoutError
)

async with LeapOCR("api-key") as client:
    try:
        result = await client.ocr.process_and_wait("document.pdf")
    except AuthenticationError:
        print("Invalid API key")
    except RateLimitError as e:
        print(f"Rate limited, retry after {e.retry_after}s")
    except FileError as e:
        print(f"File error: {e.message}")
    except JobFailedError as e:
        print(f"Processing failed for job {e.job_id}")
    except JobTimeoutError as e:
        print(f"Job {e.job_id} timed out")
```

## Progress Tracking

```python
from leapocr import PollOptions

def on_progress(status):
    print(f"Progress: {status.progress}% - {status.processed_pages}/{status.total_pages} pages")

async with LeapOCR("api-key") as client:
    result = await client.ocr.process_and_wait(
        "large_document.pdf",
        poll_options=PollOptions(
            poll_interval=2.0,      # Check every 2 seconds
            max_wait=300.0,         # Timeout after 5 minutes
            on_progress=on_progress # Callback for progress updates
        )
    )
```

## Sync API (Simple Scripts)

```python
from leapocr import LeapOCRSync

# Synchronous wrapper for non-async code
client = LeapOCRSync("api-key")

result = client.ocr.process_and_wait("document.pdf")
print(f"Processed {result.total_pages} pages")

client.close()
```

## Configuration

```python
from leapocr import LeapOCR, ClientConfig
import httpx

config = ClientConfig(
    base_url="https://api.leapocr.com/api/v1",
    timeout=30.0,           # Request timeout in seconds
    max_retries=3,          # Number of retries for transient errors
    retry_delay=1.0,        # Initial retry delay
    retry_multiplier=2.0,   # Exponential backoff multiplier
    debug=False             # Enable debug logging
)

async with LeapOCR("api-key", config=config) as client:
    result = await client.ocr.process_file("document.pdf")
```

## Streaming Results (Advanced)

```python
async with LeapOCR("api-key") as client:
    # Submit job
    job = await client.ocr.process_file("large_document.pdf")

    # Stream results page by page as they become available
    async for page in client.ocr.stream_results(job.job_id):
        print(f"Page {page.page_number}: {page.text[:100]}...")
        # Process each page immediately without waiting for all pages
```

## Available Models

```python
async with LeapOCR("api-key") as client:
    # List available models
    models = await client.ocr.list_models()

    for model in models:
        print(f"{model.display_name}: {model.credits_per_page} credits/page")
```

## File Support

**Supported formats:**
- PDF (.pdf)
- Images: PNG (.png), JPEG (.jpg, .jpeg), TIFF (.tiff, .tif)

**File size limits:**
- Max file size: 100MB
- Files ≥50MB use multipart upload (automatic)

## Environment Variables

```bash
# Optional: Set API key via environment
export LEAPOCR_API_KEY="your-api-key"

# Optional: Override base URL
export LEAPOCR_BASE_URL="https://api.leapocr.com/api/v1"
```

```python
import os
from leapocr import LeapOCR

# Will use LEAPOCR_API_KEY from environment
client = LeapOCR(os.getenv("LEAPOCR_API_KEY"))
```

## Next Steps

- Read the [Implementation Plan](SDK_IMPLEMENTATION_PLAN.md) for architecture details
- Check [examples/](examples/) for more usage patterns
- Review [API Reference](docs/api_reference.md) for complete API documentation
