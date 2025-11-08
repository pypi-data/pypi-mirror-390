# LeapOCR Python SDK - Implementation Summary

## Overview

Complete implementation plan for a production-ready Python SDK for LeapOCR, based on the Go SDK architecture and API analysis.

## Key Design Decisions

### 1. Package Manager: uv

**Decision**: Use `uv` instead of Poetry

**Rationale**:
- Faster dependency resolution and installation
- Modern, actively developed
- Simple CLI interface
- Better for CI/CD pipelines

**Commands**:
```bash
uv init leapocr-python
uv add httpx pydantic typing-extensions
uv add --dev pytest pytest-asyncio ruff mypy
```

### 2. Minimal Dependencies (3 core + dev tools)

**Core Dependencies**:
1. **httpx** - Async HTTP client
2. **pydantic v1** - Data validation (required by openapi-generator)
3. **typing-extensions** - Python 3.9 compatibility

**What we're NOT using**:
- ❌ requests (use httpx instead)
- ❌ python-dateutil (use stdlib datetime)
- ❌ attrs (use stdlib dataclasses)
- ❌ tenacity (implement custom retry)
- ❌ loguru (use stdlib logging)

### 3. Direct Upload Flow (Critical Implementation)

**3-Step Process**:

```
1. Initiate Upload
   POST /ocr/uploads/direct
   Body: {file_name, file_size (REQUIRED), content_type, format, ...}
   Returns: {job_id, parts: [{part_number, start_byte, end_byte, upload_url}]}

2. Upload to S3
   For each part:
   - Read bytes from start_byte to end_byte
   - PUT to upload_url (presigned URL, direct to S3)
   - Extract ETag from response headers
   - Store {part_number, etag}

3. Complete Upload
   POST /ocr/uploads/{job_id}/complete
   Body: {parts: [{part_number, etag}]}
   Triggers processing workflow
```

**Critical Details**:
- File size MUST be provided upfront
- Use raw PUT to presigned URLs (not multipart/form-data)
- Extract ETag from headers and strip quotes
- Handle URL expiration (403 errors)

### 4. Two-Layer Architecture

```
Public API (leapocr/__init__.py)
    ↓
Wrapper Layer (leapocr/client.py, ocr.py)
    ↓
Generated Layer (leapocr/generated/)
```

**Benefits**:
- Users never touch generated code
- Can regenerate without breaking changes
- Idiomatic Python API on top
- Easy to add convenience methods

### 5. Async-First with Sync Wrapper

**Primary API**: Async (using httpx + asyncio)
```python
async with LeapOCR("api-key") as client:
    result = await client.ocr.process_and_wait("doc.pdf")
```

**Sync Wrapper**: For simple scripts
```python
client = LeapOCRSync("api-key")
result = client.ocr.process_and_wait("doc.pdf")
client.close()
```

### 6. Pythonic Patterns

**Type hints everywhere**:
```python
async def process_file(
    self,
    file: Union[str, Path, BinaryIO],
    options: Optional[ProcessOptions] = None
) -> ProcessResult:
```

**Dataclasses for config**:
```python
@dataclass
class ProcessOptions:
    format: Format = Format.STRUCTURED
    model: Optional[Model] = None
```

**Enums for constants**:
```python
class Format(str, Enum):
    MARKDOWN = "markdown"
    STRUCTURED = "structured"
```

**Context managers**:
```python
async with LeapOCR("api-key") as client:
    # Automatic cleanup
```

**Async generators for streaming**:
```python
async def stream_results(self, job_id: str) -> AsyncIterator[PageResult]:
    ...
```

## Project Structure

```
leapocr-python/
├── leapocr/
│   ├── __init__.py          # Public exports
│   ├── client.py            # LeapOCR client
│   ├── ocr.py               # OCRService
│   ├── models.py            # Enums, dataclasses
│   ├── errors.py            # Exception hierarchy
│   ├── config.py            # Configuration
│   ├── generated/           # OpenAPI generated (never edit)
│   └── _internal/
│       ├── retry.py         # Retry logic
│       ├── upload.py        # S3 upload handler
│       ├── polling.py       # Status polling
│       └── validation.py    # Input validation
├── tests/
│   ├── test_*.py            # Unit tests
│   └── integration/         # Integration tests
├── examples/
│   ├── basic_usage.py
│   ├── batch_processing.py
│   └── ...
├── scripts/
│   ├── filter_sdk_endpoints.py
│   └── generate_client.sh
├── pyproject.toml           # uv configuration
├── SDK_IMPLEMENTATION_PLAN.md
├── QUICKSTART.md
└── README.md
```

## SDK-Tagged API Endpoints

From OpenAPI analysis, these endpoints have "SDK" tag:

1. **GET /ocr/result/{job_id}** - Get results (with pagination)
2. **GET /ocr/status/{job_id}** - Get status
3. **POST /ocr/uploads/direct** - Initiate direct upload
4. **POST /ocr/uploads/url** - Process from URL
5. **POST /ocr/uploads/{job_id}/complete** - Complete upload

Additional (tagged OCR):
- **GET /ocr/models** - List available models

## Implementation Phases (10 days)

### Phase 1: Setup (Day 1)
- [x] Initialize uv project
- [x] Create plan documentation
- [ ] Setup pyproject.toml
- [ ] Create directory structure
- [ ] Configure ruff, mypy

### Phase 2: Code Generation (Day 1-2)
- [ ] Write filter_sdk_endpoints.py script
- [ ] Generate Python client from OpenAPI
- [ ] Review generated code
- [ ] Create wrapper exports

### Phase 3: Core Client (Day 2-3)
- [ ] Implement LeapOCR client class
- [ ] Implement ClientConfig
- [ ] Setup HTTP client with auth
- [ ] Context manager support

### Phase 4: OCR Service (Day 3-5)
- [ ] Implement process_file()
- [ ] Implement process_url()
- [ ] Implement get_job_status()
- [ ] Implement get_results()
- [ ] Implement process_and_wait()

### Phase 5: Internal Utilities (Day 5-6)
- [ ] Retry logic with exponential backoff
- [ ] MultipartUploader for S3
- [ ] Status polling helper
- [ ] Input validation

### Phase 6: Testing (Day 6-7)
- [ ] Unit tests (80%+ coverage)
- [ ] Integration tests
- [ ] Mock HTTP responses
- [ ] Test fixtures

### Phase 7: Documentation (Day 7-8)
- [ ] Complete README
- [ ] API reference
- [ ] Usage examples
- [ ] Error handling guide

### Phase 8: Sync Wrapper (Day 8)
- [ ] LeapOCRSync class
- [ ] Sync version of all methods

### Phase 9: Polish & Release (Day 9-10)
- [ ] Code review
- [ ] Run all linters
- [ ] Type check with mypy
- [ ] Generate changelog
- [ ] Tag v0.1.0

## Quick Start Commands

```bash
# Setup
curl -LsSf https://astral.sh/uv/install.sh | sh
uv init leapocr-python
cd leapocr-python

# Add dependencies
uv add httpx pydantic typing-extensions
uv add --dev pytest pytest-asyncio pytest-cov ruff mypy

# Generate OpenAPI client
curl -o openapi.json http://localhost:8080/api/v1/docs/openapi.json
python scripts/filter_sdk_endpoints.py openapi.json openapi-sdk.json
openapi-generator-cli generate -i openapi-sdk.json -g python-pydantic-v1 -o leapocr/generated

# Format & lint
ruff format .
ruff check .
mypy leapocr/

# Test
pytest tests/ -v --cov=leapocr

# Run example
python examples/basic_usage.py
```

## Success Criteria

**Must Have (v0.1.0)**:
- ✅ Process file from path
- ✅ Process file from URL
- ✅ Get job status
- ✅ Get results
- ✅ Process and wait (poll until done)
- ✅ Automatic retry on transient errors
- ✅ Proper error handling
- ✅ 80%+ test coverage
- ✅ Type hints everywhere (mypy strict passes)
- ✅ Complete documentation

**Nice to Have (v0.2.0)**:
- Batch processing helper
- Streaming results
- CLI tool
- Progress callbacks
- Template management
- Credit balance checking

## Key Differences from Go SDK

| Aspect | Go SDK | Python SDK |
|--------|--------|------------|
| Async | Goroutines + channels | async/await |
| Config | Functional options | Dataclass |
| Types | Structs | Dataclasses + Pydantic |
| Errors | error interface | Exception hierarchy |
| HTTP | net/http | httpx |
| Files | io.Reader | BinaryIO |
| Enums | const string | Enum(str, Enum) |
| Context | context.Context | Built into asyncio |

## Critical Implementation Notes

### File Upload
1. **Always calculate file size first** - Required by API
2. **Use raw PUT to S3** - Not multipart/form-data
3. **Extract ETag correctly** - Strip quotes from header
4. **Handle expired URLs** - Retry with new presigned URL

### Error Handling
- 401/403: Don't retry (auth error)
- 429: Retry with backoff (rate limit)
- 5xx: Retry with backoff (server error)
- Network errors: Retry with backoff

### Retry Logic
```python
max_retries = 3
base_delay = 1.0
multiplier = 2.0

for attempt in range(max_retries + 1):
    try:
        return await operation()
    except RetriableError:
        delay = base_delay * (multiplier ** attempt)
        await asyncio.sleep(delay)
```

### Polling Strategy
```python
poll_interval = 2.0  # seconds
max_wait = 300.0     # 5 minutes

while elapsed < max_wait:
    status = await get_status(job_id)
    if status.completed:
        return results
    await asyncio.sleep(poll_interval)
```

## Resources

- **Plan**: [SDK_IMPLEMENTATION_PLAN.md](SDK_IMPLEMENTATION_PLAN.md)
- **Quick Start**: [QUICKSTART.md](QUICKSTART.md)
- **Go SDK Reference**: [github.com/leapocr/leapocr-go](https://github.com/leapocr/leapocr-go)
- **OpenAPI Spec**: http://localhost:8080/api/v1/docs/openapi.json

## Questions?

Review the detailed implementation plan in `SDK_IMPLEMENTATION_PLAN.md` for:
- Complete API design
- Code examples for all methods
- Testing strategy
- Error handling patterns
- Python best practices
- Dependency rationale

Ready to start implementation!
