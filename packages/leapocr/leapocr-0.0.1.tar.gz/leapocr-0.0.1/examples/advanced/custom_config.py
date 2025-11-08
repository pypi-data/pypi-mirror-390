"""Advanced example: Custom configuration and polling options.

This example demonstrates:
- Custom client configuration (timeout, base URL, retries)
- Custom polling options with progress callbacks
- Different output formats

Requirements:
- LEAPOCR_API_KEY environment variable
"""

import asyncio
import os

from leapocr import ClientConfig, Format, LeapOCR, Model, PollOptions, ProcessOptions
from leapocr.config import ClientConfig


async def main():
    # Get API key from environment
    api_key = os.getenv("LEAPOCR_API_KEY")
    if not api_key:
        print("ERROR: LEAPOCR_API_KEY environment variable is required")
        return

    print("=== Custom Configuration Example ===\n")

    # Create custom configuration
    config = ClientConfig(
        base_url=os.getenv("OCR_BASE_URL", "https://api.leapocr.com/api/v1"),
        timeout=120.0,  # 2 minutes timeout
        max_retries=5,  # More retries for reliability
        retry_delay=2.0,  # Start with 2 second delay
        retry_multiplier=2.0,  # Exponential backoff
    )

    print("Custom configuration:")
    print(f"  Base URL: {config.base_url}")
    print(f"  Timeout: {config.timeout}s")
    print(f"  Max retries: {config.max_retries}")
    print(f"  Retry delay: {config.retry_delay}s")
    print(f"  Retry multiplier: {config.retry_multiplier}x")
    print()

    # Example document
    document_url = "https://example.com/document.pdf"

    async with LeapOCR(api_key, config) as client:
        # Check API health
        print("Checking API health...")
        is_healthy = await client.health()
        print(f"API Status: {'✓ Healthy' if is_healthy else '✗ Unhealthy'}\n")

        # Define progress callback
        def progress_callback(status):
            print(
                f"  Progress: {status.progress:.1f}% - "
                f"Processed {status.processed_pages}/{status.total_pages} pages"
            )

        # Custom polling options with progress tracking
        poll_options = PollOptions(
            poll_interval=1.0,  # Check every second
            max_wait=180.0,  # Wait up to 3 minutes
            on_progress=progress_callback,
        )

        print(f"Processing: {document_url}")
        print("Polling configuration:")
        print(f"  Interval: {poll_options.poll_interval}s")
        print(f"  Max wait: {poll_options.max_wait}s")
        print(f"  Progress callback: {'Yes' if poll_options.on_progress else 'No'}\n")

        try:
            # Process with custom options
            result = await client.ocr.process_and_wait(
                document_url,
                options=ProcessOptions(
                    format=Format.PER_PAGE_STRUCTURED,
                    model=Model.STANDARD_V1,
                    instructions="Extract content with high accuracy",
                ),
                poll_options=poll_options,
            )

            print("\n✓ Processing completed!")
            print(f"  Credits used: {result.credits_used}")
            print(f"  Processing time: {result.processing_time_seconds:.2f}s")
            print(f"  Pages: {len(result.pages)}")
            print(f"  Format: {result.result_format}")

        except Exception as e:
            print(f"\n✗ Processing failed: {e}")
            print("\nNote: This example requires a valid document URL.")

    # Example 2: Different formats
    print("\n" + "=" * 50)
    print("Testing Different Output Formats")
    print("=" * 50 + "\n")

    formats_to_test = [
        (Format.MARKDOWN, "Markdown format - best for text extraction"),
        (Format.STRUCTURED, "Structured format - JSON with schema"),
        (Format.PER_PAGE_STRUCTURED, "Per-page structured - separate JSON per page"),
    ]

    async with LeapOCR(api_key, config) as client:
        for fmt, description in formats_to_test:
            print(f"{fmt.value}: {description}")

        print("\nYou can process the same document in different formats")
        print("to get the output structure that best fits your needs.")


if __name__ == "__main__":
    asyncio.run(main())
