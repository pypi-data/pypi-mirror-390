# LeapOCR Python SDK Examples

This directory contains standalone examples demonstrating how to use the LeapOCR Python SDK.

## Prerequisites

All examples require:
- Python 3.9 or higher
- LeapOCR SDK installed (`pip install leapocr` or `uv add leapocr`)
- `LEAPOCR_API_KEY` environment variable set with your API key

```bash
export LEAPOCR_API_KEY="your-api-key-here"
```

## Running Examples

Each example is a standalone script that can be run directly:

```bash
# Using Python
python examples/basic/process_file.py

# Or using uv
uv run examples/basic/process_file.py
```

## Basic Examples

### `basic/process_file.py`
Process a local PDF file with LeapOCR.

**Features demonstrated:**
- Creating a LeapOCR client
- Processing local files
- Using `process_and_wait()` for convenience
- Accessing results and metadata

**Usage:**
```bash
# Create a sample PDF in the examples/basic directory
cd examples/basic
# Add your sample-document.pdf here
python process_file.py
```

### `basic/process_url.py`
Process a document from a URL with manual status polling.

**Features demonstrated:**
- Processing documents from URLs
- Manual status polling
- Progress tracking
- Different output formats

**Usage:**
```bash
python examples/basic/process_url.py

# Or with custom URL
TEST_DOCUMENT_URL="https://your-url.com/doc.pdf" python examples/basic/process_url.py
```

## Advanced Examples

### `advanced/batch_processing.py`
Process multiple documents concurrently using asyncio.

**Features demonstrated:**
- Concurrent processing with `asyncio.gather()`
- Batch job management
- Error tracking across multiple jobs
- Calculating total credits and processing time

**Usage:**
```bash
python examples/advanced/batch_processing.py
```

### `advanced/schema_extraction.py`
Extract structured data using custom schemas.

**Features demonstrated:**
- Custom schema definition
- Structured data extraction
- JSON schema for invoice processing
- Working with nested data structures

**Usage:**
```bash
python examples/advanced/schema_extraction.py

# Or with custom invoice URL
INVOICE_URL="https://your-url.com/invoice.pdf" python examples/advanced/schema_extraction.py
```

### `advanced/custom_config.py`
Use custom configuration and polling options.

**Features demonstrated:**
- Custom client configuration (timeout, retries, base URL)
- Custom polling options
- Progress callbacks
- API health checks
- Different output formats

**Usage:**
```bash
python examples/advanced/custom_config.py

# With custom base URL
OCR_BASE_URL="https://api-staging.example.com" python examples/advanced/custom_config.py
```

## Error Handling Examples

### `error_handling/error_types.py`
Demonstrate different error types and handling strategies.

**Features demonstrated:**
- Authentication errors
- Validation errors
- Job errors
- Error hierarchy and catching
- Error inspection and attributes
- Recovery strategies

**Usage:**
```bash
python examples/error_handling/error_types.py
```

### `error_handling/timeout_handling.py`
Handle timeouts and task cancellation.

**Features demonstrated:**
- Custom timeout configuration
- Task cancellation and cleanup
- Manual polling with timeouts
- Timeout recommendations by document size

**Usage:**
```bash
python examples/error_handling/timeout_handling.py
```

## Common Patterns

### Async Context Manager
All examples use the async context manager pattern for proper resource cleanup:

```python
async with LeapOCR(api_key) as client:
    result = await client.ocr.process_and_wait("document.pdf")
```

### Error Handling
Catch SDK-specific errors for better error handling:

```python
from leapocr import LeapOCRError, APIError, ValidationError

try:
    result = await client.ocr.process_file("document.pdf")
except ValidationError as e:
    print(f"Invalid input: {e.message}")
except APIError as e:
    print(f"API error: {e.message} (status: {e.status_code})")
except LeapOCRError as e:
    print(f"SDK error: {e.message}")
```

### Progress Tracking
Use progress callbacks for long-running operations:

```python
def progress_callback(status):
    print(f"Progress: {status.progress:.1f}%")

result = await client.ocr.process_and_wait(
    "document.pdf",
    poll_options=PollOptions(
        poll_interval=2.0,
        on_progress=progress_callback,
    ),
)
```

## Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `LEAPOCR_API_KEY` | Your LeapOCR API key | None | Yes |
| `OCR_BASE_URL` | API base URL | `https://api.leapocr.com/api/v1` | No |
| `TEST_DOCUMENT_URL` | URL for testing | Example URL | No |
| `INVOICE_URL` | Invoice URL for schema example | Example URL | No |

## Tips

1. **Start with basic examples** to understand the fundamentals
2. **Check error messages** carefully - they include helpful information
3. **Use progress callbacks** for long-running operations
4. **Set appropriate timeouts** based on document size
5. **Handle errors gracefully** in production code
6. **Use structured format** with schemas for data extraction
7. **Process in batches** for multiple documents
8. **Monitor credits usage** to optimize costs

## Troubleshooting

### "LEAPOCR_API_KEY environment variable is required"
Set your API key: `export LEAPOCR_API_KEY="your-key"`

### "File not found" errors
Ensure you're running examples from the correct directory or provide full paths.

### Timeout errors
Increase `PollOptions.max_wait` or `ClientConfig.timeout` for large documents.

### Import errors
Install the SDK: `pip install leapocr` or `uv add leapocr`

## Further Reading

- [SDK Documentation](https://docs.leapocr.com/sdk/python)
- [API Reference](https://docs.leapocr.com/api)
- [Best Practices Guide](https://docs.leapocr.com/guides/best-practices)

## Support

If you encounter issues or have questions:
- Check the [documentation](https://docs.leapocr.com)
- Open an issue on [GitHub](https://github.com/leapocr/leapocr-python/issues)
- Contact support at support@leapocr.com
