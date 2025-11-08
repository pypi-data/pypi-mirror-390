"""Integration tests for LeapOCR SDK.

These tests require:
1. LEAPOCR_API_KEY environment variable
2. OCR API server running (default: http://localhost:8080/api/v1)
3. Optional: TEST_PDF_PATH environment variable pointing to a test PDF file

Run with: pytest tests/integration/ -v
"""

import os
from pathlib import Path

import pytest

from leapocr import (
    Format,
    JobStatusType,
    LeapOCR,
    Model,
    PollOptions,
    ProcessOptions,
)
from leapocr.config import ClientConfig


def find_test_pdf() -> Path | None:
    """Find a test PDF file in common locations."""
    # Check environment variable
    if test_path := os.getenv("TEST_PDF_PATH"):
        test_file = Path(test_path)
        if test_file.exists() and test_file.suffix.lower() == ".pdf":
            return test_file

    # Look for sample directory in repo root
    current = Path.cwd()
    for _ in range(5):  # Search up to 5 levels up
        sample_dir = current / "sample"
        if sample_dir.exists():
            # Try common test file names
            for filename in [
                "test.pdf",
                "A129of19_14.01.22.pdf",
                "A141of21_10.02.22.pdf",
            ]:
                test_file = sample_dir / filename
                if test_file.exists():
                    return test_file
        current = current.parent

    return None


def create_test_client() -> LeapOCR:
    """Create a LeapOCR client for testing."""
    api_key = os.getenv("LEAPOCR_API_KEY")
    if not api_key:
        pytest.skip("LEAPOCR_API_KEY environment variable not set")

    base_url = os.getenv("OCR_BASE_URL", "http://localhost:8080/api/v1")

    config = ClientConfig(
        base_url=base_url,
        timeout=120.0,  # 2 minutes
    )

    return LeapOCR(api_key, config)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_process_file_direct_upload():
    """Test processing a PDF file using direct upload flow."""
    test_file = find_test_pdf()
    if not test_file:
        pytest.skip("No test PDF file found. Set TEST_PDF_PATH or add files to sample/")

    async with create_test_client() as client:
        print(f"\nProcessing PDF file: {test_file.name}")

        # Step 1: Process file (initiates direct upload)
        print("Step 1: Initiating direct upload...")
        result = await client.ocr.process_file(
            test_file,
            options=ProcessOptions(
                format=Format.STRUCTURED,
                model=Model.STANDARD_V1,
                instructions="Extract all text and identify key information",
            ),
        )

        assert result.job_id
        print(f"Step 2: Upload completed. Job ID: {result.job_id}")

        # Step 2: Wait for completion
        print("Step 3: Waiting for OCR processing...")
        final_result = await client.ocr.get_results(result.job_id)

        # Verify results
        assert final_result.status == JobStatusType.COMPLETED
        assert final_result.credits_used > 0
        assert len(final_result.pages) > 0

        print("Processing completed successfully!")
        print(f"Credits used: {final_result.credits_used}")
        print(f"Processing time: {final_result.processing_time_seconds}s")
        print(f"Pages processed: {len(final_result.pages)}")

        if final_result.pages:
            first_page = final_result.pages[0]
            print(f"First page text length: {len(first_page.text)} characters")


@pytest.mark.integration
@pytest.mark.asyncio
async def test_process_and_wait():
    """Test convenience method that processes and waits for completion."""
    test_file = find_test_pdf()
    if not test_file:
        pytest.skip("No test PDF file found")

    async with create_test_client() as client:
        print(f"\nProcessing file with process_and_wait: {test_file.name}")

        # This method combines process_file + polling + get_results
        result = await client.ocr.process_and_wait(
            test_file,
            options=ProcessOptions(format=Format.MARKDOWN),
            poll_options=PollOptions(poll_interval=2.0, max_wait=180.0),
        )

        assert result.status == JobStatusType.COMPLETED
        assert len(result.pages) > 0
        print(f"Processed {len(result.pages)} pages successfully")


@pytest.mark.integration
@pytest.mark.asyncio
async def test_process_url():
    """Test processing a document from URL."""
    # Use environment variable or default test PDF
    test_url = os.getenv(
        "TEST_DOCUMENT_URL",
        "https://www.learningcontainer.com/wp-content/uploads/2019/09/sample-pdf-file.pdf",
    )

    async with create_test_client() as client:
        print(f"\nProcessing URL: {test_url}")

        # Process URL
        result = await client.ocr.process_url(
            test_url,
            options=ProcessOptions(
                format=Format.MARKDOWN,
                model=Model.STANDARD_V1,
            ),
        )

        assert result.job_id
        print(f"Job created with ID: {result.job_id}")

        # Poll for completion manually
        import asyncio

        max_attempts = 60  # 2 minutes with 2s intervals
        for attempt in range(max_attempts):
            status = await client.ocr.get_job_status(result.job_id)
            print(f"Job status: {status.status.value}, Progress: {status.progress:.1f}%")

            if status.status == JobStatusType.COMPLETED:
                final_result = await client.ocr.get_results(result.job_id)
                assert final_result.credits_used > 0
                assert len(final_result.pages) > 0
                print("URL processing completed successfully!")
                print(f"Credits used: {final_result.credits_used}")
                return

            if status.status == JobStatusType.FAILED:
                if status.error_message:
                    pytest.fail(f"Job failed: {status.error_message}")
                pytest.fail("Job failed with unknown error")

            await asyncio.sleep(2)

        pytest.fail("Timeout waiting for job completion")


@pytest.mark.integration
@pytest.mark.asyncio
async def test_job_status():
    """Test getting job status."""
    test_file = find_test_pdf()
    if not test_file:
        pytest.skip("No test PDF file found")

    async with create_test_client() as client:
        # Start processing
        result = await client.ocr.process_file(
            test_file, options=ProcessOptions(format=Format.STRUCTURED)
        )

        # Get status
        status = await client.ocr.get_job_status(result.job_id)

        assert status.job_id == result.job_id
        assert status.status in [
            JobStatusType.PENDING,
            JobStatusType.PROCESSING,
            JobStatusType.COMPLETED,
        ]
        assert 0 <= status.progress <= 100
        assert status.created_at is not None

        print(f"Job status: {status.status.value}")
        print(f"Progress: {status.progress}%")
        print(f"Processed {status.processed_pages}/{status.total_pages} pages")


@pytest.mark.integration
@pytest.mark.asyncio
async def test_error_handling_invalid_url():
    """Test error handling for invalid URL."""
    async with create_test_client() as client:
        with pytest.raises(Exception):  # Should raise APIError or ValidationError
            await client.ocr.process_url("not-a-valid-url")


@pytest.mark.integration
@pytest.mark.asyncio
async def test_error_handling_nonexistent_job():
    """Test error handling for non-existent job."""
    async with create_test_client() as client:
        with pytest.raises(Exception):  # Should raise APIError
            await client.ocr.get_job_status("non-existent-job-id-12345")


@pytest.mark.integration
@pytest.mark.asyncio
async def test_client_health_check():
    """Test API health check."""
    async with create_test_client() as client:
        is_healthy = await client.health()
        assert isinstance(is_healthy, bool)
        print(f"API health status: {'healthy' if is_healthy else 'unhealthy'}")


@pytest.mark.integration
@pytest.mark.asyncio
async def test_custom_poll_options():
    """Test processing with custom polling options."""
    test_file = find_test_pdf()
    if not test_file:
        pytest.skip("No test PDF file found")

    def progress_callback(status):
        """Callback to track progress."""
        print(f"Progress update: {status.progress:.1f}% ({status.status.value})")

    async with create_test_client() as client:
        poll_opts = PollOptions(
            poll_interval=1.0,  # Poll every second
            max_wait=60.0,  # Wait up to 1 minute
            on_progress=progress_callback,
        )

        result = await client.ocr.process_and_wait(
            test_file,
            options=ProcessOptions(format=Format.STRUCTURED),
            poll_options=poll_opts,
        )

        assert result.status == JobStatusType.COMPLETED


@pytest.mark.integration
@pytest.mark.asyncio
async def test_pagination():
    """Test result pagination for large documents."""
    test_file = find_test_pdf()
    if not test_file:
        pytest.skip("No test PDF file found")

    async with create_test_client() as client:
        # Process file
        result = await client.ocr.process_and_wait(test_file)

        # Get first page of results
        page1 = await client.ocr.get_results(result.job_id, page=1, limit=1)
        assert len(page1.pages) <= 1

        if page1.pagination:
            print(f"Total pages in document: {page1.pagination.total}")
            print(f"Total result pages: {page1.pagination.total_pages}")

            # If there are multiple pages, get the second page
            if page1.pagination.total_pages > 1:
                page2 = await client.ocr.get_results(result.job_id, page=2, limit=1)
                assert len(page2.pages) <= 1


@pytest.mark.integration
@pytest.mark.asyncio
async def test_different_formats():
    """Test processing with different output formats."""
    test_file = find_test_pdf()
    if not test_file:
        pytest.skip("No test PDF file found")

    async with create_test_client() as client:
        formats_to_test = [Format.MARKDOWN, Format.STRUCTURED, Format.PER_PAGE_STRUCTURED]

        for fmt in formats_to_test:
            print(f"\nTesting format: {fmt.value}")
            result = await client.ocr.process_and_wait(
                test_file,
                options=ProcessOptions(format=fmt),
                poll_options=PollOptions(max_wait=120.0),
            )

            assert result.status == JobStatusType.COMPLETED
            assert result.result_format == fmt.value
            print(f"Format {fmt.value} completed successfully")
