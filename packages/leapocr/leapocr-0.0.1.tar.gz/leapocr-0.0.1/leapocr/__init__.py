"""LeapOCR Python SDK - Transform documents into structured data using AI-powered OCR.

Example:
    >>> import asyncio
    >>> from leapocr import LeapOCR, ProcessOptions, Format
    >>>
    >>> async def main():
    ...     async with LeapOCR("your-api-key") as client:
    ...         result = await client.ocr.process_and_wait(
    ...             "document.pdf",
    ...             options=ProcessOptions(format=Format.MARKDOWN)
    ...         )
    ...         print(f"Processed {result.total_pages} pages")
    >>>
    >>> asyncio.run(main())
"""

__version__ = "0.1.0"

# Core client
from .client import LeapOCR

# Configuration
from .config import ClientConfig

# Errors
from .errors import (
    APIError,
    AuthenticationError,
    FileError,
    InsufficientCreditsError,
    JobError,
    JobFailedError,
    JobTimeoutError,
    LeapOCRError,
    NetworkError,
    RateLimitError,
    ValidationError,
)

# Models and enums
from .models import (
    BatchResult,
    Format,
    JobResult,
    JobStatus,
    JobStatusType,
    Model,
    ModelInfo,
    PageMetadata,
    PageResult,
    PaginationInfo,
    PollOptions,
    ProcessOptions,
    ProcessResult,
)

__all__ = [
    # Version
    "__version__",
    # Client
    "LeapOCR",
    # Configuration
    "ClientConfig",
    # Models
    "Format",
    "Model",
    "JobStatusType",
    "ProcessOptions",
    "PollOptions",
    "ProcessResult",
    "JobStatus",
    "JobResult",
    "PageResult",
    "PageMetadata",
    "PaginationInfo",
    "ModelInfo",
    "BatchResult",
    # Errors
    "LeapOCRError",
    "AuthenticationError",
    "RateLimitError",
    "ValidationError",
    "FileError",
    "JobError",
    "JobFailedError",
    "JobTimeoutError",
    "NetworkError",
    "APIError",
    "InsufficientCreditsError",
]
