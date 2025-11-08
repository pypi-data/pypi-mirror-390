"""Unit tests for data models."""

from datetime import datetime

import pytest

from leapocr.models import (
    Format,
    JobResult,
    JobStatus,
    JobStatusType,
    Model,
    PageMetadata,
    PageResult,
    PaginationInfo,
    PollOptions,
    ProcessOptions,
    ProcessResult,
)


class TestFormatEnum:
    """Tests for Format enum."""

    def test_format_values(self):
        assert Format.MARKDOWN.value == "markdown"
        assert Format.STRUCTURED.value == "structured"
        assert Format.PER_PAGE_STRUCTURED.value == "per_page_structured"

    def test_format_comparison(self):
        assert Format.MARKDOWN == Format.MARKDOWN
        assert Format.MARKDOWN != Format.STRUCTURED

    def test_format_string_value(self):
        """Format should be usable as string."""
        assert str(Format.MARKDOWN) == "Format.MARKDOWN"
        assert Format.MARKDOWN.value == "markdown"


class TestModelEnum:
    """Tests for Model enum."""

    def test_model_values(self):
        assert Model.STANDARD_V1.value == "standard-v1"

    def test_model_comparison(self):
        assert Model.STANDARD_V1 == Model.STANDARD_V1


class TestJobStatusType:
    """Tests for JobStatusType enum."""

    def test_status_values(self):
        assert JobStatusType.PENDING.value == "pending"
        assert JobStatusType.PROCESSING.value == "processing"
        assert JobStatusType.COMPLETED.value == "completed"
        assert JobStatusType.PARTIALLY_DONE.value == "partially_done"
        assert JobStatusType.FAILED.value == "failed"

    def test_all_statuses_defined(self):
        """Ensure all expected status types exist."""
        expected = ["pending", "processing", "completed", "partially_done", "failed"]
        actual = [s.value for s in JobStatusType]
        assert set(expected) == set(actual)


class TestProcessOptions:
    """Tests for ProcessOptions dataclass."""

    def test_default_options(self):
        opts = ProcessOptions()
        assert opts.format == Format.STRUCTURED
        assert opts.model is None
        assert opts.schema is None
        assert opts.instructions is None
        assert opts.template_id is None
        assert opts.metadata == {}

    def test_custom_options(self):
        schema = {"title": "string", "amount": "number"}
        metadata = {"user_id": "123", "session_id": "abc"}

        opts = ProcessOptions(
            format=Format.MARKDOWN,
            model=Model.STANDARD_V1,
            schema=schema,
            instructions="Extract all text",
            template_id="template-123",
            metadata=metadata,
        )

        assert opts.format == Format.MARKDOWN
        assert opts.model == Model.STANDARD_V1
        assert opts.schema == schema
        assert opts.instructions == "Extract all text"
        assert opts.template_id == "template-123"
        assert opts.metadata == metadata

    def test_metadata_default_factory(self):
        """Test that each instance gets its own metadata dict."""
        opts1 = ProcessOptions()
        opts2 = ProcessOptions()

        opts1.metadata["key"] = "value1"
        opts2.metadata["key"] = "value2"

        assert opts1.metadata["key"] == "value1"
        assert opts2.metadata["key"] == "value2"


class TestPollOptions:
    """Tests for PollOptions dataclass."""

    def test_default_poll_options(self):
        opts = PollOptions()
        assert opts.poll_interval == 2.0
        assert opts.max_wait == 300.0
        assert opts.on_progress is None

    def test_custom_poll_options(self):
        def progress_callback(status):
            pass

        opts = PollOptions(poll_interval=1.0, max_wait=60.0, on_progress=progress_callback)

        assert opts.poll_interval == 1.0
        assert opts.max_wait == 60.0
        assert opts.on_progress == progress_callback


class TestProcessResult:
    """Tests for ProcessResult dataclass."""

    def test_process_result(self):
        created_at = datetime.now()
        result = ProcessResult(
            job_id="job-123", status=JobStatusType.PENDING, created_at=created_at
        )

        assert result.job_id == "job-123"
        assert result.status == JobStatusType.PENDING
        assert result.created_at == created_at
        assert result.estimated_completion is None

    def test_process_result_with_estimation(self):
        created_at = datetime.now()
        estimated = datetime.now()

        result = ProcessResult(
            job_id="job-123",
            status=JobStatusType.PENDING,
            created_at=created_at,
            estimated_completion=estimated,
        )

        assert result.estimated_completion == estimated


class TestJobStatus:
    """Tests for JobStatus dataclass."""

    def test_job_status(self):
        created_at = datetime.now()
        updated_at = datetime.now()

        status = JobStatus(
            job_id="job-123",
            status=JobStatusType.PROCESSING,
            processed_pages=5,
            total_pages=10,
            progress=50.0,
            created_at=created_at,
            updated_at=updated_at,
        )

        assert status.job_id == "job-123"
        assert status.status == JobStatusType.PROCESSING
        assert status.processed_pages == 5
        assert status.total_pages == 10
        assert status.progress == 50.0
        assert status.created_at == created_at
        assert status.updated_at == updated_at
        assert status.error_message is None

    def test_job_status_with_error(self):
        created_at = datetime.now()
        updated_at = datetime.now()

        status = JobStatus(
            job_id="job-123",
            status=JobStatusType.FAILED,
            processed_pages=3,
            total_pages=10,
            progress=30.0,
            created_at=created_at,
            updated_at=updated_at,
            error_message="Processing failed: Invalid PDF",
        )

        assert status.error_message == "Processing failed: Invalid PDF"


class TestPageMetadata:
    """Tests for PageMetadata dataclass."""

    def test_page_metadata_empty(self):
        metadata = PageMetadata()
        assert metadata.processing_ms is None
        assert metadata.retry_count is None
        assert metadata.extra == {}

    def test_page_metadata_with_values(self):
        extra = {"confidence": 0.95, "language": "en"}
        metadata = PageMetadata(processing_ms=1500, retry_count=2, extra=extra)

        assert metadata.processing_ms == 1500
        assert metadata.retry_count == 2
        assert metadata.extra == extra

    def test_metadata_extra_default_factory(self):
        """Each instance should get its own extra dict."""
        meta1 = PageMetadata()
        meta2 = PageMetadata()

        meta1.extra["key1"] = "value1"
        meta2.extra["key2"] = "value2"

        assert "key1" in meta1.extra
        assert "key1" not in meta2.extra


class TestPageResult:
    """Tests for PageResult dataclass."""

    def test_page_result(self):
        processed_at = datetime.now()
        metadata = PageMetadata(processing_ms=1200)

        page = PageResult(
            page_number=1,
            text="Page 1 content",
            metadata=metadata,
            processed_at=processed_at,
        )

        assert page.page_number == 1
        assert page.text == "Page 1 content"
        assert page.metadata == metadata
        assert page.processed_at == processed_at
        assert page.id is None

    def test_page_result_with_id(self):
        processed_at = datetime.now()
        metadata = PageMetadata()

        page = PageResult(
            page_number=1,
            text="Content",
            metadata=metadata,
            processed_at=processed_at,
            id="page-abc123",
        )

        assert page.id == "page-abc123"


class TestPaginationInfo:
    """Tests for PaginationInfo dataclass."""

    def test_pagination_info(self):
        pagination = PaginationInfo(page=2, limit=50, total=250, total_pages=5)

        assert pagination.page == 2
        assert pagination.limit == 50
        assert pagination.total == 250
        assert pagination.total_pages == 5


class TestJobResult:
    """Tests for JobResult dataclass."""

    def test_job_result_complete(self):
        completed_at = datetime.now()
        processed_at = datetime.now()

        pages = [
            PageResult(
                page_number=1,
                text="Page 1",
                metadata=PageMetadata(processing_ms=1000),
                processed_at=processed_at,
            ),
            PageResult(
                page_number=2,
                text="Page 2",
                metadata=PageMetadata(processing_ms=1100),
                processed_at=processed_at,
            ),
        ]

        pagination = PaginationInfo(page=1, limit=100, total=2, total_pages=1)

        result = JobResult(
            job_id="job-123",
            status=JobStatusType.COMPLETED,
            pages=pages,
            file_name="document.pdf",
            total_pages=2,
            processed_pages=2,
            processing_time_seconds=2.5,
            credits_used=4,
            model="standard-v1",
            result_format="structured",
            completed_at=completed_at,
            pagination=pagination,
        )

        assert result.job_id == "job-123"
        assert result.status == JobStatusType.COMPLETED
        assert len(result.pages) == 2
        assert result.file_name == "document.pdf"
        assert result.total_pages == 2
        assert result.processed_pages == 2
        assert result.processing_time_seconds == 2.5
        assert result.credits_used == 4
        assert result.model == "standard-v1"
        assert result.result_format == "structured"
        assert result.completed_at == completed_at
        assert result.pagination == pagination

    def test_job_result_without_pagination(self):
        completed_at = datetime.now()
        processed_at = datetime.now()

        result = JobResult(
            job_id="job-123",
            status=JobStatusType.COMPLETED,
            pages=[
                PageResult(
                    page_number=1,
                    text="Content",
                    metadata=PageMetadata(),
                    processed_at=processed_at,
                )
            ],
            file_name="test.pdf",
            total_pages=1,
            processed_pages=1,
            processing_time_seconds=1.2,
            credits_used=2,
            model="standard-v1",
            result_format="markdown",
            completed_at=completed_at,
        )

        assert result.pagination is None
