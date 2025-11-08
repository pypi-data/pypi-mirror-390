"""Data models and enums for LeapOCR SDK."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Optional


class Format(str, Enum):
    """Output format types for OCR processing."""

    MARKDOWN = "markdown"
    STRUCTURED = "structured"
    PER_PAGE_STRUCTURED = "per_page_structured"


class Model(str, Enum):
    """OCR model types."""

    STANDARD_V1 = "standard-v1"
    # Additional models will be fetched from API


class JobStatusType(str, Enum):
    """Job processing status types."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    PARTIALLY_DONE = "partially_done"
    FAILED = "failed"


@dataclass
class ProcessOptions:
    """Options for OCR processing."""

    format: Format = Format.STRUCTURED
    model: Optional[Model] = None
    schema: Optional[dict[str, Any]] = None
    instructions: Optional[str] = None
    template_id: Optional[str] = None
    metadata: dict[str, str] = field(default_factory=dict)


@dataclass
class PollOptions:
    """Options for polling job status."""

    poll_interval: float = 2.0  # seconds
    max_wait: float = 300.0  # seconds (5 minutes)
    on_progress: Optional[Callable[["JobStatus"], None]] = None


@dataclass
class ClientConfig:
    """Configuration for LeapOCR client."""

    base_url: str = "https://api.leapocr.com/api/v1"
    timeout: float = 30.0
    max_retries: int = 3
    retry_delay: float = 1.0
    retry_multiplier: float = 2.0
    debug: bool = False


@dataclass
class ProcessResult:
    """Result from initiating OCR processing."""

    job_id: str
    status: JobStatusType
    created_at: datetime
    estimated_completion: Optional[datetime] = None


@dataclass
class JobStatus:
    """Job status information."""

    job_id: str
    status: JobStatusType
    processed_pages: int
    total_pages: int
    progress: float  # 0-100
    created_at: datetime
    updated_at: datetime
    error_message: Optional[str] = None


@dataclass
class PageMetadata:
    """Metadata for a single page."""

    processing_ms: Optional[int] = None
    retry_count: Optional[int] = None
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass
class PageResult:
    """Result for a single page."""

    page_number: int
    text: str
    metadata: PageMetadata
    processed_at: datetime
    id: Optional[str] = None


@dataclass
class PaginationInfo:
    """Pagination information for results."""

    page: int
    limit: int
    total: int
    total_pages: int


@dataclass
class JobResult:
    """Complete job results."""

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
class ModelInfo:
    """OCR model information."""

    name: str
    display_name: str
    description: str
    credits_per_page: int
    priority: int


@dataclass
class BatchResult:
    """Result from batch processing."""

    batch_id: str
    jobs: list[ProcessResult]
    total_files: int
    submitted_at: datetime
