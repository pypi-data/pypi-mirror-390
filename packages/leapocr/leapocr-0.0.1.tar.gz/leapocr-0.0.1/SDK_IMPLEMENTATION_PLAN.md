# LeapOCR Python SDK - Implementation Plan

## Overview

This document outlines the complete implementation plan for the LeapOCR Python SDK based on the Go SDK architecture and API analysis.

## Table of Contents

1. [SDK-Tagged Endpoints Analysis](#sdk-tagged-endpoints-analysis)
2. [Architecture Design](#architecture-design)
3. [Project Structure](#project-structure)
4. [API Design](#api-design)
5. [Implementation Phases](#implementation-phases)
6. [Code Generation Strategy](#code-generation-strategy)
7. [Testing Strategy](#testing-strategy)
8. [Documentation Plan](#documentation-plan)

---

## SDK-Tagged Endpoints Analysis

Based on the OpenAPI spec analysis, the following endpoints are tagged with "SDK":

### Core OCR Operations

1. **GET /ocr/result/{job_id}**
   - Get OCR job results
   - Returns structured data or markdown based on format
   - Supports pagination (page, limit)
   - Status: 200 (completed), 202 (processing), 404 (not found)

2. **GET /ocr/status/{job_id}**
   - Get job processing status
   - Returns: status, progress, error details
   - Simple status check without full results

3. **POST /ocr/uploads/direct**
   - Initiate direct file upload (multipart)
   - Returns presigned URLs for S3 upload
   - Supports: structured, markdown, per_page_structured formats
   - Parameters: file_name, file_size, content_type, format, model, schema, instructions

4. **POST /ocr/uploads/url**
   - Process document from remote URL
   - PDF only support
   - Same format options as direct upload
   - Returns job_id immediately

5. **POST /ocr/uploads/{job_id}/complete**
   - Complete multipart upload
   - Provide ETags for all uploaded parts
   - Triggers processing workflow

### Additional Operations

- **GET /ocr/models** - List available OCR models (tagged OCR, Models)

### Key Insights

**Direct Upload Flow (Detailed):**
```
Step 1: Initiate Upload
POST /ocr/uploads/direct
Body: {
  "file_name": "document.pdf",
  "file_size": 1048576,           # MUST provide actual file size in bytes
  "content_type": "application/pdf",
  "format": "markdown",           # or "structured", "per_page_structured"
  "model": "standard-v1",         # optional
  "instructions": "...",          # optional, max 100 chars
  "schema": {...},                # optional, for structured format
  "template_id": "uuid"           # optional, use existing template
}

Response: {
  "job_id": "uuid",
  "upload_id": "s3-upload-id",
  "parts": [
    {
      "part_number": 1,
      "start_byte": 0,
      "end_byte": 5242879,        # For files <50MB, single part
      "upload_url": "https://r2.example.com/..."  # Presigned URL
    }
    # Multiple parts for files ≥50MB
  ],
  "chunk_size": 5242880,          # 5MB chunks
  "total_chunks": 1,
  "complete_url": "/api/v1/ocr/uploads/{job_id}/complete",
  "expires_at": "2023-12-25T10:45:00Z"
}

Step 2: Upload File Parts to S3
For each part:
  - Read bytes from start_byte to end_byte from file
  - PUT to upload_url with file chunk as body
  - Extract ETag from response headers (strip quotes)
  - Store {part_number, etag} for completion

Important: Use raw PUT requests to presigned URLs, NOT multipart/form-data

Step 3: Complete Upload
POST /ocr/uploads/{job_id}/complete
Body: {
  "parts": [
    {"part_number": 1, "etag": "9bb58f26192e4ba00f01e2e7b136bbd8"},
    {"part_number": 2, "etag": "..."},
    ...
  ]
}

Response: {
  "job_id": "uuid",
  "status": "pending",
  "message": "Upload completed successfully, processing started",
  "created_at": "2023-12-25T10:30:00Z"
}

Step 4: Poll Status
GET /ocr/status/{job_id}
Poll every 2s until status is "completed" or "failed"

Step 5: Get Results
GET /ocr/result/{job_id}?page=1&limit=100
```

**URL Flow:**
```
1. Call /ocr/uploads/url → Get job_id immediately
2. Poll /ocr/status/{job_id} for progress
3. Get results from /ocr/result/{job_id}
```

**Critical Implementation Notes:**

1. **File Size is Required**: Must calculate file size before calling `/ocr/uploads/direct`
2. **Multipart for All Files**: API uses multipart even for small files (1 part if <50MB)
3. **ETag Extraction**: Must extract ETag header from S3 response and remove quotes
4. **Direct S3 Upload**: Upload directly to presigned URLs with PUT, not through API
5. **Chunk Boundaries**: Respect exact byte ranges (start_byte to end_byte inclusive)
6. **Error Handling**: Presigned URLs expire, handle 403/expired URL errors

---

## Architecture Design

### Two-Layer Architecture

```
┌─────────────────────────────────────────┐
│  Public API (leapocr/__init__.py)       │  ← Clean exports
├─────────────────────────────────────────┤
│  Wrapper Layer (leapocr/client.py)      │  ← Idiomatic Python
│  - LeapOCR client class                 │  ← Async/sync support
│  - OCRService                           │  ← Retry logic
│  - Convenience methods                  │  ← Type hints
│  - Error handling                       │  ← Context managers
├─────────────────────────────────────────┤
│  Generated Layer (leapocr/generated/)   │  ← Never manually edit
│  - OpenAPI-generated client            │  ← Auto-regenerated
│  - Models and schemas                   │  ← Pydantic models
└─────────────────────────────────────────┘
```

### Key Design Principles

1. **Async-First with Sync Support**
   - Primary API is async (using httpx)
   - Sync wrapper for simple scripts
   - Context manager support for both

2. **Type-Safe with Pydantic**
   - Use pydantic-v1 for OpenAPI generation
   - Runtime validation
   - IDE autocomplete support

3. **Pythonic API**
   - Snake_case naming
   - Type hints everywhere
   - Dataclasses/Enums for options
   - Generator pattern for streaming

4. **Error Handling**
   - Custom exception hierarchy
   - Preserve error context
   - Automatic retry for transient errors

---

## Project Structure

```
leapocr-python/
├── leapocr/
│   ├── __init__.py              # Public exports
│   ├── client.py                # Main LeapOCR client
│   ├── ocr.py                   # OCRService implementation
│   ├── models.py                # Custom models and enums
│   ├── types.py                 # Type aliases and protocols
│   ├── errors.py                # Exception classes
│   ├── config.py                # Configuration management
│   ├── generated/               # OpenAPI generated code
│   │   ├── __init__.py
│   │   ├── api/
│   │   ├── models/
│   │   └── client.py
│   └── _internal/               # Internal utilities
│       ├── __init__.py
│       ├── retry.py             # Retry logic
│       ├── upload.py            # File upload helpers
│       ├── polling.py           # Status polling
│       └── validation.py        # Input validation
├── tests/
│   ├── __init__.py
│   ├── test_client.py
│   ├── test_ocr.py
│   ├── test_errors.py
│   ├── test_retry.py
│   ├── test_upload.py
│   ├── integration/
│   │   ├── __init__.py
│   │   ├── test_e2e.py
│   │   └── test_real_api.py
│   └── fixtures/
│       ├── sample.pdf
│       ├── large.pdf
│       └── responses/
│           └── *.json
├── examples/
│   ├── basic_usage.py
│   ├── async_processing.py
│   ├── batch_processing.py
│   ├── custom_schema.py
│   ├── sync_wrapper.py
│   └── error_handling.py
├── scripts/
│   ├── generate_client.sh       # Generate from OpenAPI
│   ├── filter_sdk_endpoints.py  # Filter SDK endpoints
│   └── update_docs.sh           # Generate documentation
├── docs/
│   ├── quickstart.md
│   ├── api_reference.md
│   ├── error_handling.md
│   └── advanced_usage.md
├── pyproject.toml               # uv config
├── README.md
├── CHANGELOG.md
├── LICENSE
└── .gitignore
```

---

## API Design

### Client Initialization

```python
from leapocr import LeapOCR, ClientConfig
import httpx

# Simple usage
client = LeapOCR("your-api-key")

# With configuration
config = ClientConfig(
    base_url="https://api.leapocr.com",
    timeout=30.0,
    max_retries=3,
    retry_delay=1.0,
    retry_multiplier=2.0,
    http_client=None,  # Custom httpx.AsyncClient
    debug=False
)
client = LeapOCR("your-api-key", config=config)

# Context manager (async)
async with LeapOCR("your-api-key") as client:
    result = await client.ocr.process_file("document.pdf")

# Sync version
from leapocr import LeapOCRSync

client = LeapOCRSync("your-api-key")
result = client.ocr.process_file("document.pdf")
```

### OCR Service API

```python
from leapocr.models import Format, Model, ProcessOptions, PollOptions
from pathlib import Path
from typing import BinaryIO, Union, AsyncIterator

class OCRService:
    """OCR operations service"""

    # Core operations
    async def process_file(
        self,
        file: Union[str, Path, BinaryIO],
        options: Optional[ProcessOptions] = None
    ) -> ProcessResult:
        """Process a file from path or file-like object"""

    async def process_url(
        self,
        url: str,
        options: Optional[ProcessOptions] = None
    ) -> ProcessResult:
        """Process a document from URL"""

    async def get_job_status(
        self,
        job_id: str
    ) -> JobStatus:
        """Get job processing status"""

    async def get_results(
        self,
        job_id: str,
        page: int = 1,
        limit: int = 100
    ) -> JobResult:
        """Get job results with pagination"""

    async def cancel_job(
        self,
        job_id: str
    ) -> None:
        """Cancel a running job"""

    # Convenience methods
    async def process_and_wait(
        self,
        file: Union[str, Path, BinaryIO],
        options: Optional[ProcessOptions] = None,
        poll_options: Optional[PollOptions] = None
    ) -> JobResult:
        """Process and wait for completion"""

    async def process_batch(
        self,
        files: list[Union[str, Path, BinaryIO]],
        options: Optional[ProcessOptions] = None
    ) -> BatchResult:
        """Process multiple files"""

    async def stream_results(
        self,
        job_id: str
    ) -> AsyncIterator[PageResult]:
        """Stream results page by page"""

    # Model information
    async def list_models(self) -> list[ModelInfo]:
        """List available OCR models"""
```

### Models and Types

```python
from enum import Enum
from dataclasses import dataclass, field
from typing import Optional, Any, Literal

# Enums
class Format(str, Enum):
    """Output format types"""
    MARKDOWN = "markdown"
    STRUCTURED = "structured"
    PER_PAGE_STRUCTURED = "per_page_structured"

class Model(str, Enum):
    """OCR model types"""
    STANDARD_V1 = "standard-v1"
    # Add other models from /ocr/models endpoint

class JobStatusType(str, Enum):
    """Job status types"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    PARTIALLY_DONE = "partially_done"
    FAILED = "failed"

# Options
@dataclass
class ProcessOptions:
    """Options for OCR processing"""
    format: Format = Format.STRUCTURED
    model: Optional[Model] = None
    schema: Optional[dict[str, Any]] = None
    instructions: Optional[str] = None
    template_id: Optional[str] = None
    metadata: dict[str, str] = field(default_factory=dict)

@dataclass
class PollOptions:
    """Options for polling job status"""
    poll_interval: float = 2.0  # seconds
    max_wait: float = 300.0     # seconds (5 minutes)
    on_progress: Optional[Callable[[JobStatus], None]] = None

@dataclass
class ClientConfig:
    """Client configuration"""
    base_url: str = "https://api.leapocr.com/api/v1"
    timeout: float = 30.0
    max_retries: int = 3
    retry_delay: float = 1.0
    retry_multiplier: float = 2.0
    http_client: Optional[httpx.AsyncClient] = None
    debug: bool = False

# Results
@dataclass
class ProcessResult:
    """Result from initiating processing"""
    job_id: str
    status: JobStatusType
    created_at: datetime
    estimated_completion: Optional[datetime] = None

@dataclass
class JobStatus:
    """Job status information"""
    job_id: str
    status: JobStatusType
    processed_pages: int
    total_pages: int
    progress: float  # 0-100
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime

@dataclass
class PageResult:
    """Result for a single page"""
    page_number: int
    text: str
    metadata: dict[str, Any]
    processed_at: datetime

@dataclass
class JobResult:
    """Complete job results"""
    job_id: str
    status: JobStatusType
    pages: list[PageResult]
    file_name: str
    total_pages: int
    processed_pages: int
    processing_time_seconds: float
    credits_used: int
    model: str
    result_format: str
    completed_at: datetime
    pagination: Optional[PaginationInfo] = None

@dataclass
class PaginationInfo:
    """Pagination information"""
    page: int
    limit: int
    total: int
    total_pages: int

@dataclass
class ModelInfo:
    """OCR model information"""
    name: str
    display_name: str
    description: str
    credits_per_page: int
    priority: int
```

### Error Hierarchy

```python
class LeapOCRError(Exception):
    """Base exception for all LeapOCR errors"""

    def __init__(
        self,
        message: str,
        code: Optional[str] = None,
        status_code: Optional[int] = None,
        details: Optional[Any] = None,
        cause: Optional[Exception] = None
    ):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details
        self.__cause__ = cause

class AuthenticationError(LeapOCRError):
    """Authentication failed - invalid API key"""
    pass

class RateLimitError(LeapOCRError):
    """Rate limit exceeded"""

    def __init__(self, message: str, retry_after: Optional[int] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.retry_after = retry_after

class ValidationError(LeapOCRError):
    """Validation error - invalid input"""

    def __init__(self, message: str, fields: Optional[dict[str, list[str]]] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.fields = fields or {}

class FileError(LeapOCRError):
    """File-related error"""

    def __init__(
        self,
        message: str,
        file_path: Optional[str] = None,
        file_size: Optional[int] = None,
        **kwargs
    ):
        super().__init__(message, **kwargs)
        self.file_path = file_path
        self.file_size = file_size

class JobError(LeapOCRError):
    """Job-related error"""

    def __init__(self, message: str, job_id: str, **kwargs):
        super().__init__(message, **kwargs)
        self.job_id = job_id

class JobFailedError(JobError):
    """Job processing failed"""
    pass

class JobTimeoutError(JobError):
    """Job processing timeout"""
    pass

class NetworkError(LeapOCRError):
    """Network connectivity error"""
    pass

class APIError(LeapOCRError):
    """API returned an error"""

    def __init__(
        self,
        message: str,
        status_code: int,
        response: Optional[Any] = None,
        **kwargs
    ):
        super().__init__(message, status_code=status_code, **kwargs)
        self.response = response

class InsufficientCreditsError(LeapOCRError):
    """Insufficient credits to process"""
    pass
```

### Utility Functions

```python
# Validation
def validate_file(
    file_path: Union[str, Path],
    max_size: int = 100 * 1024 * 1024,  # 100MB
    allowed_types: Optional[list[str]] = None
) -> ValidationResult:
    """Validate file before upload"""

# Retry decorator
async def with_retry(
    operation: Callable[..., Awaitable[T]],
    max_retries: int = 3,
    retry_delay: float = 1.0,
    retry_multiplier: float = 2.0,
    is_retryable: Optional[Callable[[Exception], bool]] = None
) -> T:
    """Execute operation with exponential backoff retry"""
```

---

## Implementation Phases

### Phase 1: Project Setup (Day 1)

**Tasks:**
- [ ] Initialize uv project
- [ ] Setup pyproject.toml with minimal dependencies
- [ ] Create project structure
- [ ] Setup pre-commit hooks (ruff for linting+formatting)
- [ ] Configure CI/CD (GitHub Actions)
- [ ] Create initial README

**Initialize with uv:**
```bash
# Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Initialize project
uv init leapocr-python
cd leapocr-python

# Add dependencies (minimal set)
uv add httpx          # HTTP client with async support
uv add pydantic       # For generated models (will use v1 compat)
uv add typing-extensions  # For Python 3.9 compatibility

# Add dev dependencies
uv add --dev pytest pytest-asyncio pytest-cov
uv add --dev ruff     # Linting + formatting (replaces black + flake8)
uv add --dev mypy     # Type checking
```

**Minimal Dependencies:**
```toml
[project]
name = "leapocr"
version = "0.1.0"
description = "Official Python SDK for LeapOCR"
requires-python = ">=3.9"
dependencies = [
    "httpx>=0.25.0",           # Async HTTP client
    "pydantic>=1.10.13,<2.0",  # v1 for OpenAPI generator compatibility
    "typing-extensions>=4.8.0", # Backports for Python 3.9
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.3",
    "pytest-asyncio>=0.21.1",
    "pytest-cov>=4.1.0",
    "ruff>=0.1.6",
    "mypy>=1.7.0",
]

[tool.ruff]
line-length = 100
target-version = "py39"

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W", "UP"]

[tool.mypy]
python_version = "3.9"
strict = true
warn_return_any = true
warn_unused_configs = true

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
```

**Why these minimal dependencies?**
- **httpx**: Industry standard async HTTP client, well-maintained
- **pydantic v1**: Required for openapi-generator compatibility
- **typing-extensions**: Backport modern type hints to Python 3.9
- **ruff**: Fast all-in-one linter+formatter (replaces black+flake8+isort)
- **No extras**: No poetry, no unnecessary tooling

### Phase 2: OpenAPI Client Generation (Day 1-2)

**Tasks:**
- [ ] Install openapi-generator-cli
- [ ] Create filter script for SDK endpoints
- [ ] Generate Python client with pydantic-v1
- [ ] Review generated code
- [ ] Test generated models

**Script: scripts/filter_sdk_endpoints.py**
```python
#!/usr/bin/env python3
"""Filter OpenAPI spec to include only SDK-tagged endpoints"""

import json
import sys
from pathlib import Path

def filter_sdk_endpoints(spec: dict) -> dict:
    """Keep only SDK-tagged endpoints and their schemas"""

    filtered_paths = {}
    used_schemas = set()

    # Filter paths
    for path, methods in spec.get("paths", {}).items():
        for method, operation in methods.items():
            if isinstance(operation, dict):
                tags = operation.get("tags", [])
                if "SDK" in tags:
                    if path not in filtered_paths:
                        filtered_paths[path] = {}
                    filtered_paths[path][method] = operation

                    # Collect referenced schemas
                    collect_schemas(operation, used_schemas)

    # Build filtered spec
    filtered_spec = {
        "openapi": spec["openapi"],
        "info": spec["info"],
        "servers": spec["servers"],
        "paths": filtered_paths,
        "components": {
            "schemas": {},
            "securitySchemes": spec.get("components", {}).get("securitySchemes", {})
        },
        "tags": [t for t in spec.get("tags", []) if t["name"] in ["OCR", "SDK"]]
    }

    # Include only used schemas
    all_schemas = spec.get("components", {}).get("schemas", {})
    for schema_name in used_schemas:
        if schema_name in all_schemas:
            filtered_spec["components"]["schemas"][schema_name] = all_schemas[schema_name]

    return filtered_spec

def collect_schemas(obj: Any, schemas: set, visited: set = None):
    """Recursively collect schema references"""
    if visited is None:
        visited = set()

    if isinstance(obj, dict):
        obj_id = id(obj)
        if obj_id in visited:
            return
        visited.add(obj_id)

        if "$ref" in obj:
            ref = obj["$ref"]
            if ref.startswith("#/components/schemas/"):
                schema_name = ref.split("/")[-1]
                schemas.add(schema_name)

        for value in obj.values():
            collect_schemas(value, schemas, visited)

    elif isinstance(obj, list):
        for item in obj:
            collect_schemas(item, schemas, visited)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: filter_sdk_endpoints.py <input.json> <output.json>")
        sys.exit(1)

    input_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])

    with open(input_path) as f:
        spec = json.load(f)

    filtered = filter_sdk_endpoints(spec)

    with open(output_path, "w") as f:
        json.dump(filtered, f, indent=2)

    print(f"Filtered {len(filtered['paths'])} SDK endpoints")
```

**Script: scripts/generate_client.sh**
```bash
#!/bin/bash
set -e

echo "Fetching OpenAPI spec..."
curl -o openapi.json http://localhost:8080/api/v1/docs/openapi.json

echo "Filtering SDK endpoints..."
python scripts/filter_sdk_endpoints.py openapi.json openapi-sdk.json

echo "Generating Python client..."
openapi-generator-cli generate \
  -i openapi-sdk.json \
  -g python-pydantic-v1 \
  -o leapocr/generated \
  --additional-properties=\
packageName=leapocr.generated,\
projectName=leapocr-sdk,\
packageVersion=0.1.0,\
useOneOfDiscriminatorLookup=true,\
generateSourceCodeOnly=true

echo "Formatting generated code..."
black leapocr/generated/
ruff check --fix leapocr/generated/

echo "Done! Generated client in leapocr/generated/"
```

### Phase 3: Core Client Implementation (Day 2-3)

**Files to implement:**
- `leapocr/config.py` - Configuration management
- `leapocr/client.py` - Main LeapOCR client
- `leapocr/_internal/retry.py` - Retry logic
- `leapocr/errors.py` - Exception hierarchy

**Key implementation:**

```python
# leapocr/client.py
import httpx
from typing import Optional
from .config import ClientConfig
from .ocr import OCRService
from .errors import AuthenticationError

class LeapOCR:
    """Main LeapOCR client"""

    def __init__(
        self,
        api_key: str,
        config: Optional[ClientConfig] = None
    ):
        if not api_key:
            raise AuthenticationError("API key is required")

        self.api_key = api_key
        self.config = config or ClientConfig()

        # Setup HTTP client
        self._http_client = self.config.http_client or httpx.AsyncClient(
            base_url=self.config.base_url,
            timeout=self.config.timeout,
            headers={
                "Authorization": f"Bearer {api_key}",
                "User-Agent": f"leapocr-python/{__version__}",
            }
        )

        # Services
        self.ocr = OCRService(self._http_client, self.config)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def close(self):
        """Close HTTP connections"""
        await self._http_client.aclose()

    async def health(self) -> bool:
        """Check API health"""
        try:
            response = await self._http_client.get("/health")
            return response.status_code == 200
        except Exception:
            return False
```

### Phase 4: OCR Service Implementation (Day 3-5)

**Files to implement:**
- `leapocr/ocr.py` - OCRService class
- `leapocr/_internal/upload.py` - File upload helpers
- `leapocr/_internal/polling.py` - Status polling
- `leapocr/_internal/validation.py` - Input validation

**Key methods:**

```python
# leapocr/ocr.py
from pathlib import Path
from typing import Union, BinaryIO, Optional
import httpx
from ._internal.upload import MultipartUploader
from ._internal.polling import poll_until_done
from ._internal.validation import validate_file
from .models import ProcessOptions, ProcessResult, JobStatus, JobResult
from .errors import FileError, ValidationError

class OCRService:
    """OCR operations"""

    def __init__(self, http_client: httpx.AsyncClient, config: ClientConfig):
        self._client = http_client
        self._config = config
        self._uploader = MultipartUploader(http_client, config)

    async def process_file(
        self,
        file: Union[str, Path, BinaryIO],
        options: Optional[ProcessOptions] = None
    ) -> ProcessResult:
        """
        Process file from path or file-like object

        Args:
            file: File path (str/Path) or file-like object (BinaryIO)
            options: Processing options (format, model, schema, etc.)

        Returns:
            ProcessResult with job_id and initial status
        """
        options = options or ProcessOptions()

        # Handle different input types
        if isinstance(file, (str, Path)):
            file_path = Path(file)

            # Validate file exists and is readable
            validation = validate_file(file_path)
            if not validation.valid:
                raise FileError(validation.error, file_path=str(file_path))

            # Get file size (REQUIRED for API)
            file_size = file_path.stat().st_size

            # Open and upload
            with open(file_path, "rb") as f:
                return await self._upload_file(
                    f,
                    file_path.name,
                    file_size,
                    options
                )
        else:
            # File-like object - must calculate size
            file_size = self._uploader.get_file_size(file)
            file_name = getattr(file, "name", "document.pdf")

            return await self._upload_file(
                file,
                file_name,
                file_size,
                options
            )

    async def process_url(
        self,
        url: str,
        options: Optional[ProcessOptions] = None
    ) -> ProcessResult:
        """Process from URL"""

        options = options or ProcessOptions()

        payload = {
            "url": url,
            "format": options.format.value,
        }

        if options.model:
            payload["model"] = options.model.value
        if options.schema:
            payload["schema"] = options.schema
        if options.instructions:
            payload["instructions"] = options.instructions
        if options.template_id:
            payload["template_id"] = options.template_id

        response = await self._client.post(
            "/ocr/uploads/url",
            json=payload
        )
        response.raise_for_status()

        data = response.json()
        return ProcessResult(
            job_id=data["job_id"],
            status=JobStatusType(data["status"]),
            created_at=parse_datetime(data["created_at"])
        )

    async def get_job_status(self, job_id: str) -> JobStatus:
        """Get job status"""
        response = await self._client.get(f"/ocr/status/{job_id}")
        response.raise_for_status()
        data = response.json()

        return JobStatus(
            job_id=data["job_id"],
            status=JobStatusType(data["status"]),
            processed_pages=data.get("processed_pages", 0),
            total_pages=data.get("total_pages", 0),
            progress=calculate_progress(data),
            error_message=data.get("error_message"),
            created_at=parse_datetime(data["created_at"]),
            updated_at=parse_datetime(data.get("updated_at", data["created_at"]))
        )

    async def get_results(
        self,
        job_id: str,
        page: int = 1,
        limit: int = 100
    ) -> JobResult:
        """Get job results"""
        response = await self._client.get(
            f"/ocr/result/{job_id}",
            params={"page": page, "limit": limit}
        )

        if response.status_code == 202:
            # Still processing
            raise JobError(
                "Job is still processing",
                job_id=job_id
            )

        response.raise_for_status()
        data = response.json()

        return JobResult(
            job_id=data["job_id"],
            status=JobStatusType(data["status"]),
            pages=[parse_page_result(p) for p in data.get("pages", [])],
            file_name=data["file_name"],
            total_pages=data["total_pages"],
            processed_pages=data["processed_pages"],
            processing_time_seconds=data["processing_time_seconds"],
            credits_used=data["credits_used"],
            model=data["model"],
            result_format=data["result_format"],
            completed_at=parse_datetime(data["completed_at"]),
            pagination=parse_pagination(data.get("pagination"))
        )

    async def process_and_wait(
        self,
        file: Union[str, Path, BinaryIO],
        options: Optional[ProcessOptions] = None,
        poll_options: Optional[PollOptions] = None
    ) -> JobResult:
        """Process and wait for completion"""

        # Submit job
        result = await self.process_file(file, options)

        # Poll until done
        poll_opts = poll_options or PollOptions()
        await poll_until_done(
            self,
            result.job_id,
            poll_opts
        )

        # Get results
        return await self.get_results(result.job_id)

    async def _upload_file(
        self,
        file: BinaryIO,
        file_name: str,
        file_size: int,  # REQUIRED - must be calculated before calling
        options: ProcessOptions
    ) -> ProcessResult:
        """
        Internal file upload logic following the 3-step flow:
        1. Initiate upload (get presigned URLs)
        2. Upload parts to S3
        3. Complete upload (trigger processing)
        """

        # Step 1: Initiate upload and get presigned URLs
        initiate_payload = {
            "file_name": file_name,
            "file_size": file_size,  # REQUIRED by API
            "content_type": self._uploader.guess_content_type(file_name),
            "format": options.format.value,
        }

        # Add optional fields
        if options.model:
            initiate_payload["model"] = options.model.value
        if options.schema:
            initiate_payload["schema"] = options.schema
        if options.instructions:
            initiate_payload["instructions"] = options.instructions
        if options.template_id:
            initiate_payload["template_id"] = options.template_id

        response = await self._client.post(
            "/ocr/uploads/direct",
            json=initiate_payload
        )
        response.raise_for_status()

        upload_data = response.json()
        job_id = upload_data["job_id"]
        parts = upload_data["parts"]  # List of presigned URLs with byte ranges

        # Step 2: Upload file parts to S3 via presigned URLs
        # Returns list of {part_number, etag} for each uploaded part
        completed_parts = await self._uploader.upload_multipart(file, parts)

        # Step 3: Complete the upload (signals API to start processing)
        complete_response = await self._client.post(
            f"/ocr/uploads/{job_id}/complete",
            json={"parts": completed_parts}
        )
        complete_response.raise_for_status()

        complete_data = complete_response.json()

        return ProcessResult(
            job_id=job_id,
            status=JobStatusType(complete_data.get("status", "pending")),
            created_at=parse_datetime(complete_data["created_at"])
        )
```

### Phase 5: Internal Utilities (Day 5-6)

**Retry Logic:**
```python
# leapocr/_internal/retry.py
import asyncio
from typing import TypeVar, Callable, Awaitable, Optional
from ..errors import LeapOCRError, RateLimitError, NetworkError

T = TypeVar('T')

def is_retryable_error(error: Exception) -> bool:
    """Check if error is retryable"""
    if isinstance(error, RateLimitError):
        return True
    if isinstance(error, NetworkError):
        return True
    if isinstance(error, LeapOCRError):
        status_code = error.status_code
        if status_code and status_code >= 500:
            return True
    return False

async def with_retry(
    operation: Callable[..., Awaitable[T]],
    max_retries: int = 3,
    retry_delay: float = 1.0,
    retry_multiplier: float = 2.0,
    is_retryable: Optional[Callable[[Exception], bool]] = None
) -> T:
    """Execute with exponential backoff retry"""

    is_retryable = is_retryable or is_retryable_error
    last_error = None

    for attempt in range(max_retries + 1):
        try:
            return await operation()
        except Exception as error:
            last_error = error

            if attempt == max_retries:
                raise

            if not is_retryable(error):
                raise

            # Calculate delay
            if isinstance(error, RateLimitError) and error.retry_after:
                delay = error.retry_after
            else:
                delay = retry_delay * (retry_multiplier ** attempt)

            await asyncio.sleep(delay)

    raise last_error
```

**Upload Helper:**
```python
# leapocr/_internal/upload.py
import httpx
from typing import BinaryIO, Union
from pathlib import Path
import os
from ..errors import FileError, NetworkError

class MultipartUploader:
    """Handle multipart file uploads to S3 via presigned URLs"""

    def __init__(self, config):
        self._config = config
        # Separate client for S3 uploads (no auth needed, different domain)
        self._s3_client = httpx.AsyncClient(timeout=300.0)  # 5min timeout for large files

    async def close(self):
        """Close S3 client"""
        await self._s3_client.aclose()

    def get_file_size(self, file: Union[str, Path, BinaryIO]) -> int:
        """Get file size in bytes (required for initiating upload)"""
        if isinstance(file, (str, Path)):
            return os.path.getsize(file)
        elif hasattr(file, 'seek') and hasattr(file, 'tell'):
            # File-like object
            current_pos = file.tell()
            file.seek(0, 2)  # Seek to end
            size = file.tell()
            file.seek(current_pos)  # Restore position
            return size
        else:
            raise FileError("Cannot determine file size")

    async def upload_multipart(
        self,
        file: BinaryIO,
        parts: list[dict]
    ) -> list[dict]:
        """
        Upload file parts to S3 presigned URLs and return ETags

        Args:
            file: File-like object (must support seek/read)
            parts: List of part dicts with part_number, start_byte, end_byte, upload_url

        Returns:
            List of dicts with part_number and etag for completion request
        """
        completed_parts = []

        for part in parts:
            part_number = part["part_number"]
            upload_url = part["upload_url"]
            start_byte = part["start_byte"]
            end_byte = part["end_byte"]

            # Calculate chunk size (end_byte is inclusive)
            chunk_size = end_byte - start_byte + 1

            # Read chunk from file
            file.seek(start_byte)
            chunk_data = file.read(chunk_size)

            if len(chunk_data) != chunk_size:
                raise FileError(
                    f"Failed to read expected chunk size: got {len(chunk_data)}, expected {chunk_size}",
                    file_path=getattr(file, 'name', None)
                )

            # Upload to S3 via presigned URL (raw PUT, not multipart/form-data)
            try:
                response = await self._s3_client.put(
                    upload_url,
                    content=chunk_data,
                    headers={
                        "Content-Length": str(len(chunk_data)),
                        # Note: Content-Type is typically set in presigned URL params
                    }
                )
                response.raise_for_status()
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 403:
                    raise NetworkError(
                        f"Presigned URL expired or invalid for part {part_number}",
                        cause=e
                    )
                raise NetworkError(
                    f"Failed to upload part {part_number} to S3",
                    cause=e
                )
            except httpx.RequestError as e:
                raise NetworkError(
                    f"Network error uploading part {part_number}",
                    cause=e
                )

            # Extract ETag from response headers
            # S3 returns ETag with quotes like: "9bb58f26192e4ba00f01e2e7b136bbd8"
            etag = response.headers.get("ETag", "").strip('"')
            if not etag:
                raise NetworkError(
                    f"Missing ETag in S3 response for part {part_number}"
                )

            completed_parts.append({
                "part_number": part_number,
                "etag": etag
            })

        return completed_parts

    def guess_content_type(self, filename: str) -> str:
        """Guess content type from filename"""
        ext = Path(filename).suffix.lower()
        content_types = {
            '.pdf': 'application/pdf',
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.tiff': 'image/tiff',
            '.tif': 'image/tiff',
        }
        return content_types.get(ext, 'application/octet-stream')
```

**Polling:**
```python
# leapocr/_internal/polling.py
import asyncio
from datetime import datetime, timedelta
from ..models import PollOptions, JobStatusType
from ..errors import JobTimeoutError, JobFailedError

async def poll_until_done(
    ocr_service,
    job_id: str,
    options: PollOptions
):
    """Poll job status until complete"""

    start_time = datetime.now()
    max_wait_td = timedelta(seconds=options.max_wait)

    while True:
        # Check timeout
        if datetime.now() - start_time > max_wait_td:
            raise JobTimeoutError(
                f"Job {job_id} did not complete within {options.max_wait}s",
                job_id=job_id
            )

        # Get status
        status = await ocr_service.get_job_status(job_id)

        # Call progress callback
        if options.on_progress:
            options.on_progress(status)

        # Check completion
        if status.status == JobStatusType.COMPLETED:
            return

        if status.status == JobStatusType.FAILED:
            raise JobFailedError(
                status.error_message or "Job processing failed",
                job_id=job_id
            )

        # Wait before next poll
        await asyncio.sleep(options.poll_interval)
```

### Phase 6: Testing (Day 6-7)

**Unit Tests:**
- Test client initialization
- Test configuration
- Test error handling
- Test retry logic
- Mock HTTP responses

**Integration Tests:**
- Test against real API
- Test file upload flow
- Test URL processing
- Test status polling
- Test batch processing

**Test Configuration:**
```python
# tests/conftest.py
import pytest
import httpx
from leapocr import LeapOCR, ClientConfig

@pytest.fixture
def api_key():
    return "test-api-key"

@pytest.fixture
def mock_client(api_key):
    config = ClientConfig(
        base_url="http://localhost:8080/api/v1",
        http_client=httpx.AsyncClient()
    )
    return LeapOCR(api_key, config=config)

@pytest.fixture
def sample_pdf_path():
    return "tests/fixtures/sample.pdf"
```

### Phase 7: Documentation (Day 7-8)

**Documentation files:**
- README.md with quickstart
- API reference (auto-generated)
- Examples for common use cases
- Error handling guide
- Contributing guide

### Phase 8: Sync Wrapper (Day 8)

**Create sync wrapper for simple scripts:**

```python
# leapocr/sync.py
import asyncio
from typing import Union, Optional, BinaryIO
from pathlib import Path
from .client import LeapOCR
from .models import ProcessOptions, PollOptions, JobResult

class LeapOCRSync:
    """Synchronous wrapper for LeapOCR"""

    def __init__(self, api_key: str, config=None):
        self._async_client = LeapOCR(api_key, config)

    def process_file(
        self,
        file: Union[str, Path, BinaryIO],
        options: Optional[ProcessOptions] = None
    ) -> str:
        """Process file synchronously"""
        return asyncio.run(
            self._async_client.ocr.process_file(file, options)
        )

    def process_and_wait(
        self,
        file: Union[str, Path, BinaryIO],
        options: Optional[ProcessOptions] = None,
        poll_options: Optional[PollOptions] = None
    ) -> JobResult:
        """Process and wait synchronously"""
        return asyncio.run(
            self._async_client.ocr.process_and_wait(
                file, options, poll_options
            )
        )

    def close(self):
        """Close connections"""
        asyncio.run(self._async_client.close())
```

### Phase 9: Polish & Release (Day 9-10)

**Final tasks:**
- [ ] Complete test coverage (>80%)
- [ ] Run linters and type checkers
- [ ] Generate documentation
- [ ] Create examples
- [ ] Write CHANGELOG
- [ ] Tag v0.1.0
- [ ] Publish to PyPI

---

## Code Generation Strategy

### OpenAPI Generator Configuration

**Generator:** `python-pydantic-v1`

**Options:**
```yaml
packageName: leapocr.generated
projectName: leapocr-sdk
packageVersion: 0.1.0
useOneOfDiscriminatorLookup: true
generateSourceCodeOnly: true
library: asyncio
```

### Post-Generation Steps

1. **Format generated code**
   ```bash
   black leapocr/generated/
   ruff check --fix leapocr/generated/
   ```

2. **Add __init__.py exports**
   ```python
   # leapocr/generated/__init__.py
   # Only export what's needed
   ```

3. **Wrapper imports**
   ```python
   # leapocr/client.py
   from .generated.api import OCRApi
   from .generated.models import *
   ```

---

## Testing Strategy

### Unit Tests

**Coverage targets:**
- Client initialization: 100%
- Error handling: 100%
- Retry logic: 100%
- Configuration: 100%
- Utilities: >90%

**Test structure:**
```python
# tests/test_client.py
import pytest
from leapocr import LeapOCR, ClientConfig
from leapocr.errors import AuthenticationError

@pytest.mark.asyncio
async def test_client_init():
    client = LeapOCR("test-key")
    assert client.api_key == "test-key"
    await client.close()

@pytest.mark.asyncio
async def test_client_no_api_key():
    with pytest.raises(AuthenticationError):
        LeapOCR("")

@pytest.mark.asyncio
async def test_client_context_manager():
    async with LeapOCR("test-key") as client:
        assert client.api_key == "test-key"
```

### Integration Tests

**Test against real API:**
```python
# tests/integration/test_e2e.py
import pytest
import os
from leapocr import LeapOCR, ProcessOptions, Format

@pytest.mark.integration
@pytest.mark.asyncio
async def test_process_real_file():
    api_key = os.getenv("LEAPOCR_API_KEY")
    if not api_key:
        pytest.skip("LEAPOCR_API_KEY not set")

    async with LeapOCR(api_key) as client:
        result = await client.ocr.process_and_wait(
            "tests/fixtures/sample.pdf",
            options=ProcessOptions(format=Format.MARKDOWN)
        )

        assert result.status == JobStatusType.COMPLETED
        assert len(result.pages) > 0
        assert result.pages[0].text
```

### Mock Testing

```python
# tests/test_ocr.py
import pytest
from httpx import AsyncClient, Response
from leapocr import LeapOCR
from leapocr.models import JobStatusType

@pytest.mark.asyncio
async def test_get_status_success(httpx_mock):
    httpx_mock.add_response(
        url="http://localhost:8080/api/v1/ocr/status/job-123",
        json={
            "job_id": "job-123",
            "status": "completed",
            "processed_pages": 10,
            "total_pages": 10,
            "created_at": "2024-01-01T00:00:00Z"
        }
    )

    async with LeapOCR("test-key") as client:
        status = await client.ocr.get_job_status("job-123")
        assert status.job_id == "job-123"
        assert status.status == JobStatusType.COMPLETED
```

---

## Documentation Plan

### README.md Structure

```markdown
# LeapOCR Python SDK

[![PyPI](https://img.shields.io/pypi/v/leapocr)](https://pypi.org/project/leapocr/)
[![Python](https://img.shields.io/pypi/pyversions/leapocr)](https://pypi.org/project/leapocr/)
[![License](https://img.shields.io/github/license/leapocr/leapocr-python)](https://github.com/leapocr/leapocr-python/blob/main/LICENSE)

Official Python SDK for LeapOCR - Transform documents into structured data using AI-powered OCR.

## Features

- 🚀 **Async-first design** with sync wrapper
- 📝 **Type-safe** with full type hints
- 🔄 **Automatic retries** with exponential backoff
- 📦 **Multiple formats** - Structured, Markdown, Per-page
- 🎯 **Custom schemas** for data extraction
- 🔧 **Flexible configuration**
- ✨ **Pythonic API**

## Installation

```bash
pip install leapocr
```

## Quick Start

```python
import asyncio
from leapocr import LeapOCR

async def main():
    async with LeapOCR("your-api-key") as client:
        # Process a document
        result = await client.ocr.process_and_wait("document.pdf")

        # Access extracted text
        for page in result.pages:
            print(f"Page {page.page_number}: {page.text}")

asyncio.run(main())
```

## Usage Examples

[Continue with examples...]
```

### API Reference

Auto-generate with Sphinx or mkdocs:

```bash
pip install sphinx sphinx-autodoc-typehints
sphinx-quickstart docs
sphinx-build -b html docs docs/_build
```

---

## Python Best Practices & Minimal Dependencies

### Why Minimal Dependencies?

**Philosophy**: Only add dependencies that provide significant value. Prefer stdlib when possible.

**Core Dependencies (3 only):**
1. **httpx** - Async HTTP client, industry standard, well-maintained
2. **pydantic v1** - Required by openapi-generator, provides validation
3. **typing-extensions** - Backport modern type hints to Python 3.9

**What we're NOT adding:**
- ❌ **requests** - Use httpx (supports async)
- ❌ **urllib3** - httpx handles connection pooling
- ❌ **aiohttp** - httpx is simpler and more modern
- ❌ **python-dateutil** - Use stdlib `datetime.fromisoformat()` (Python 3.7+)
- ❌ **attrs** - Use stdlib `dataclasses`
- ❌ **click/typer** - No CLI in v1, can add later
- ❌ **loguru** - Use stdlib `logging`
- ❌ **tenacity** - Implement simple retry ourselves (~50 lines)

### Python Standards We're Following

**1. Type Hints Everywhere**
```python
# Good
async def process_file(
    self,
    file: Union[str, Path, BinaryIO],
    options: Optional[ProcessOptions] = None
) -> ProcessResult:
    ...

# Bad (no type hints)
async def process_file(self, file, options=None):
    ...
```

**2. Use Dataclasses for Configuration**
```python
from dataclasses import dataclass, field

@dataclass
class ProcessOptions:
    format: Format = Format.STRUCTURED
    model: Optional[Model] = None
    schema: Optional[dict[str, Any]] = None
```

**3. Use Enums for Constants**
```python
from enum import Enum

class Format(str, Enum):
    MARKDOWN = "markdown"
    STRUCTURED = "structured"
    PER_PAGE_STRUCTURED = "per_page_structured"
```

**4. Use Context Managers**
```python
async with LeapOCR("api-key") as client:
    result = await client.ocr.process_file("doc.pdf")
# Automatic cleanup
```

**5. Use Async Generators for Streaming**
```python
async def stream_results(self, job_id: str) -> AsyncIterator[PageResult]:
    page = 1
    while True:
        result = await self._get_page(job_id, page)
        if not result:
            break
        yield result
        page += 1
```

**6. Proper Error Hierarchy**
```python
class LeapOCRError(Exception):
    """Base exception"""

class AuthenticationError(LeapOCRError):
    """API key invalid"""

class RateLimitError(LeapOCRError):
    """Rate limited"""
```

**7. Use pathlib for File Paths**
```python
from pathlib import Path

file_path = Path(file)
file_size = file_path.stat().st_size
```

**8. No Global State**
```python
# Good - client holds state
client = LeapOCR("api-key")

# Bad - global variables
GLOBAL_API_KEY = "..."
```

**9. Explicit is Better Than Implicit**
```python
# Good - clear what's required
async def process_file(
    file: Union[str, Path, BinaryIO],
    options: Optional[ProcessOptions] = None
) -> ProcessResult:

# Bad - unclear what file can be
async def process_file(file, **kwargs):
```

**10. Use Standard Library When Possible**
```python
# Date parsing - NO external library needed
from datetime import datetime

def parse_datetime(s: str) -> datetime:
    # RFC3339: "2023-12-25T10:30:00Z"
    return datetime.fromisoformat(s.replace('Z', '+00:00'))

# File operations - use pathlib
from pathlib import Path
file_size = Path("file.pdf").stat().st_size

# JSON - use stdlib
import json
data = json.loads(response.text)
```

### Dependency Decision Matrix

| Need | Solution | Rationale |
|------|----------|-----------|
| HTTP requests | httpx | Best async support, modern API |
| Data validation | pydantic v1 | Required by openapi-generator |
| Type hints | typing-extensions | Backport for Python 3.9 |
| Date parsing | stdlib datetime | `.fromisoformat()` works for RFC3339 |
| File handling | stdlib pathlib | Built-in, modern API |
| JSON | stdlib json | Built-in, fast |
| Async | stdlib asyncio | Built-in |
| Retry logic | Custom (~50 lines) | Simple, no need for library |
| Logging | stdlib logging | Built-in, flexible |

### Code Quality Tools (Dev Only)

**1. ruff** - Linting + formatting (replaces black, flake8, isort, pyupgrade)
```bash
uv add --dev ruff
ruff check .
ruff format .
```

**2. mypy** - Type checking
```bash
uv add --dev mypy
mypy leapocr/
```

**3. pytest** - Testing
```bash
uv add --dev pytest pytest-asyncio pytest-cov
pytest tests/
```

### Why This Matters

**Benefits:**
- ✅ Faster installation (`uv add leapocr` installs in seconds)
- ✅ Smaller attack surface (fewer dependencies to audit)
- ✅ Fewer breaking changes (stdlib is stable)
- ✅ Better performance (less overhead)
- ✅ Easier maintenance (less to update)
- ✅ Clear what code does (less "magic")

**Trade-offs:**
- ⚠️ Must implement retry logic ourselves (~50 lines)
- ⚠️ Must write date parsing helper (~5 lines)
- ✅ But we get full control and understanding

---

## Success Metrics

**Code Quality:**
- [ ] 80%+ test coverage
- [ ] All type hints pass mypy strict
- [ ] No linting errors
- [ ] All examples work

**Documentation:**
- [ ] Complete API reference
- [ ] 5+ working examples
- [ ] Migration guide
- [ ] Contributing guide

**Performance:**
- [ ] Upload speed matches Go SDK
- [ ] Retry logic works correctly
- [ ] Memory usage is reasonable

**Developer Experience:**
- [ ] Easy installation (1 command)
- [ ] Clear error messages
- [ ] Good IDE support (autocomplete)
- [ ] Fast iteration (no manual edits to generated code)

---

## Next Steps

1. **Review this plan** with the team
2. **Setup project structure** (Phase 1)
3. **Generate OpenAPI client** (Phase 2)
4. **Implement core functionality** (Phases 3-5)
5. **Test thoroughly** (Phase 6)
6. **Document everything** (Phase 7)
7. **Release v0.1.0** (Phase 9)

## Questions & Decisions

1. **Python version support?** → Recommend 3.9+ (for modern type hints)
2. **Sync wrapper?** → Yes, for simple scripts
3. **CLI tool?** → Optional, can be added later
4. **Streaming results?** → Yes, via async generator
5. **Batch operations?** → Yes, for multiple files

---

*Last updated: 2024-11-07*
