"""Basic example: Process a document from URL with LeapOCR.

This example demonstrates:
- Processing a document from a URL
- Manual polling for status updates
- Retrieving final results

Requirements:
- LEAPOCR_API_KEY environment variable
"""

import asyncio
import os

from leapocr import Format, JobStatusType, LeapOCR, Model, ProcessOptions


async def main():
    # Get API key from environment
    api_key = os.getenv("LEAPOCR_API_KEY")
    if not api_key:
        print("ERROR: LEAPOCR_API_KEY environment variable is required")
        return

    # Example URL (replace with a real document URL)
    document_url = os.getenv(
        "TEST_DOCUMENT_URL",
        "https://www.learningcontainer.com/wp-content/uploads/2019/09/sample-pdf-file.pdf",
    )

    print("=== Processing File from URL ===\n")
    print(f"URL: {document_url}")

    async with LeapOCR(api_key) as client:
        # Start processing
        print("\nStarting OCR processing...")
        result = await client.ocr.process_url(
            document_url,
            options=ProcessOptions(
                format=Format.MARKDOWN,
                model=Model.STANDARD_V1,
                instructions="Extract key information",
            ),
        )

        print(f"✓ Job created with ID: {result.job_id}")
        print(f"  Status: {result.status.value}")

        # Poll for status manually (alternative to process_and_wait)
        print("\nPolling for status updates...")
        max_attempts = 60  # 2 minutes with 2s intervals

        for attempt in range(max_attempts):
            status = await client.ocr.get_job_status(result.job_id)

            status_indicator = "⏳" if status.status == JobStatusType.PROCESSING else "📝"
            print(
                f"{status_indicator} Status: {status.status.value} - Progress: {status.progress:.1f}%"
            )

            if status.status == JobStatusType.COMPLETED:
                # Get final results
                final_result = await client.ocr.get_results(result.job_id)

                print("\n✓ Processing completed successfully!")
                print(f"  Credits used: {final_result.credits_used}")
                print(f"  Processing time: {final_result.processing_time_seconds:.2f}s")
                print(f"  Pages processed: {len(final_result.pages)}")
                print(f"  Text length: {sum(len(p.text) for p in final_result.pages)} characters")

                # Print text preview from first page
                if final_result.pages:
                    text = final_result.pages[0].text
                    preview = text[:300] + "..." if len(text) > 300 else text
                    print(f"\nText preview:\n{preview}")

                return

            if status.status == JobStatusType.FAILED:
                error_msg = status.error_message or "Unknown error"
                print(f"\n✗ Processing failed: {error_msg}")
                return

            # Wait before next poll
            await asyncio.sleep(2)

        print("\n✗ Timeout: Processing did not complete in time")


if __name__ == "__main__":
    asyncio.run(main())
