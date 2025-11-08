"""OCR service for document processing operations."""

from pathlib import Path
from typing import Any, BinaryIO

import httpx

from ._internal.polling import poll_until_done
from ._internal.retry import with_retry
from ._internal.upload import MultipartUploader
from ._internal.utils import calculate_progress, parse_datetime
from ._internal.validation import get_file_size, guess_content_type, validate_file
from .config import ClientConfig
from .errors import APIError, FileError, JobError
from .models import (
    JobResult,
    JobStatus,
    JobStatusType,
    PageMetadata,
    PageResult,
    PaginationInfo,
    PollOptions,
    ProcessOptions,
    ProcessResult,
)


class OCRService:
    """OCR operations service.

    Provides methods for processing documents, checking job status,
    and retrieving results.
    """

    def __init__(self, http_client: httpx.AsyncClient, config: ClientConfig) -> None:
        """Initialize OCR service.

        Args:
            http_client: HTTP client for API requests
            config: Client configuration
        """
        self._client = http_client
        self._config = config
        self._uploader = MultipartUploader(timeout=300.0)

    async def process_file(
        self, file: str | Path | BinaryIO, options: ProcessOptions | None = None
    ) -> ProcessResult:
        """Process a file for OCR.

        Args:
            file: File path (str/Path) or file-like object (BinaryIO)
            options: Processing options (format, model, schema, etc.)

        Returns:
            ProcessResult with job_id and initial status

        Raises:
            FileError: If file validation fails
            APIError: If API request fails
        """
        options = options or ProcessOptions()

        # Handle different input types
        if isinstance(file, (str, Path)):
            file_path = Path(file)

            # Validate file
            validation = validate_file(file_path)
            if not validation.valid:
                error_msg = validation.error or "File validation failed"
                raise FileError(error_msg, file_path=str(file_path))

            # Get file size (required for API)
            file_size = file_path.stat().st_size
            file_name = file_path.name

            # Open and upload
            with open(file_path, "rb") as f:
                return await self._upload_file(f, file_name, file_size, options)
        else:
            # File-like object - must calculate size
            file_size = get_file_size(file)
            file_name = getattr(file, "name", "document.pdf")

            return await self._upload_file(file, file_name, file_size, options)

    async def process_url(self, url: str, options: ProcessOptions | None = None) -> ProcessResult:
        """Process a document from URL.

        Args:
            url: URL to the document (PDF only)
            options: Processing options

        Returns:
            ProcessResult with job_id and initial status

        Raises:
            APIError: If API request fails
        """
        options = options or ProcessOptions()

        payload: dict[str, Any] = {
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

        async def _make_request() -> httpx.Response:
            return await self._client.post("/ocr/uploads/url", json=payload)

        response = await with_retry(
            _make_request,
            max_retries=self._config.max_retries,
            retry_delay=self._config.retry_delay,
            retry_multiplier=self._config.retry_multiplier,
        )

        self._check_response(response)
        data = response.json()

        return ProcessResult(
            job_id=data["job_id"],
            status=JobStatusType(data["status"]),
            created_at=parse_datetime(data["created_at"]),
        )

    async def get_job_status(self, job_id: str) -> JobStatus:
        """Get job processing status.

        Args:
            job_id: Job ID to check

        Returns:
            JobStatus with current job state

        Raises:
            APIError: If API request fails
        """

        async def _make_request() -> httpx.Response:
            return await self._client.get(f"/ocr/status/{job_id}")

        response = await with_retry(
            _make_request,
            max_retries=self._config.max_retries,
            retry_delay=self._config.retry_delay,
            retry_multiplier=self._config.retry_multiplier,
        )

        self._check_response(response)
        data = response.json()

        return JobStatus(
            job_id=data["job_id"],
            status=JobStatusType(data["status"]),
            processed_pages=data.get("processed_pages", 0),
            total_pages=data.get("total_pages", 0),
            progress=calculate_progress(data),
            created_at=parse_datetime(data["created_at"]),
            updated_at=parse_datetime(data.get("updated_at", data["created_at"])),
            error_message=data.get("error_message"),
        )

    async def get_results(self, job_id: str, page: int = 1, limit: int = 100) -> JobResult:
        """Get job results.

        Args:
            job_id: Job ID to retrieve results for
            page: Page number for pagination (default: 1)
            limit: Items per page (default: 100)

        Returns:
            JobResult with extracted data

        Raises:
            JobError: If job is still processing
            APIError: If API request fails
        """

        async def _make_request() -> httpx.Response:
            return await self._client.get(
                f"/ocr/result/{job_id}", params={"page": page, "limit": limit}
            )

        response = await with_retry(
            _make_request,
            max_retries=self._config.max_retries,
            retry_delay=self._config.retry_delay,
            retry_multiplier=self._config.retry_multiplier,
        )

        # 202 means still processing
        if response.status_code == 202:
            raise JobError("Job is still processing", job_id=job_id)

        self._check_response(response)
        data = response.json()

        # Parse page results
        pages = [
            PageResult(
                page_number=p["page_number"],
                text=p["text"],
                metadata=PageMetadata(
                    processing_ms=p.get("metadata", {}).get("processing_ms"),
                    retry_count=p.get("metadata", {}).get("retry_count"),
                    extra=p.get("metadata", {}).get("extra", {}),
                ),
                processed_at=parse_datetime(p["processed_at"]),
                id=p.get("id"),
            )
            for p in data.get("pages", [])
        ]

        # Parse pagination
        pagination = None
        if "pagination" in data:
            p = data["pagination"]
            pagination = PaginationInfo(
                page=p["page"], limit=p["limit"], total=p["total"], total_pages=p["total_pages"]
            )

        return JobResult(
            job_id=data["job_id"],
            status=JobStatusType(data["status"]),
            pages=pages,
            file_name=data["file_name"],
            total_pages=data["total_pages"],
            processed_pages=data["processed_pages"],
            processing_time_seconds=data["processing_time_seconds"],
            credits_used=data["credits_used"],
            model=data["model"],
            result_format=data["result_format"],
            completed_at=parse_datetime(data["completed_at"]),
            pagination=pagination,
        )

    async def process_and_wait(
        self,
        file: str | Path | BinaryIO,
        options: ProcessOptions | None = None,
        poll_options: PollOptions | None = None,
    ) -> JobResult:
        """Process file and wait for completion.

        This is a convenience method that combines process_file() and polling.

        Args:
            file: File path or file-like object
            options: Processing options
            poll_options: Polling configuration

        Returns:
            JobResult when processing completes

        Raises:
            JobTimeoutError: If processing doesn't complete in time
            JobFailedError: If processing fails
        """
        # Submit job
        result = await self.process_file(file, options)

        # Poll until done
        poll_opts = poll_options or PollOptions()
        await poll_until_done(self.get_job_status, result.job_id, poll_opts)

        # Get final results
        return await self.get_results(result.job_id)

    async def _upload_file(
        self, file: BinaryIO, file_name: str, file_size: int, options: ProcessOptions
    ) -> ProcessResult:
        """Internal file upload logic.

        Implements the 3-step upload flow:
        1. Initiate upload (get presigned URLs)
        2. Upload parts to S3
        3. Complete upload (trigger processing)

        Args:
            file: File-like object
            file_name: Name of the file
            file_size: Size in bytes (REQUIRED by API)
            options: Processing options

        Returns:
            ProcessResult with job ID
        """
        # Step 1: Initiate upload and get presigned URLs
        initiate_payload: dict[str, Any] = {
            "file_name": file_name,
            "file_size": file_size,
            "content_type": guess_content_type(file_name),
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

        async def _initiate() -> httpx.Response:
            return await self._client.post("/ocr/uploads/direct", json=initiate_payload)

        response = await with_retry(
            _initiate,
            max_retries=self._config.max_retries,
            retry_delay=self._config.retry_delay,
            retry_multiplier=self._config.retry_multiplier,
        )

        self._check_response(response)
        upload_data = response.json()

        job_id = upload_data["job_id"]
        parts = upload_data["parts"]

        # Step 2: Upload file parts to S3
        completed_parts = await self._uploader.upload_multipart(file, parts)

        # Step 3: Complete the upload
        async def _complete() -> httpx.Response:
            return await self._client.post(
                f"/ocr/uploads/{job_id}/complete", json={"parts": completed_parts}
            )

        complete_response = await with_retry(
            _complete,
            max_retries=self._config.max_retries,
            retry_delay=self._config.retry_delay,
            retry_multiplier=self._config.retry_multiplier,
        )

        self._check_response(complete_response)
        complete_data = complete_response.json()

        return ProcessResult(
            job_id=job_id,
            status=JobStatusType(complete_data.get("status", "pending")),
            created_at=parse_datetime(complete_data["created_at"]),
        )

    def _check_response(self, response: httpx.Response) -> None:
        """Check response for errors and raise appropriate exceptions.

        Args:
            response: HTTP response to check

        Raises:
            APIError: If response indicates an error
        """
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            # Try to extract error message from response
            try:
                error_data = response.json()
                message = error_data.get("error", {}).get("message", str(e))
            except Exception:
                message = str(e)

            raise APIError(message, status_code=response.status_code, response=response.text)
