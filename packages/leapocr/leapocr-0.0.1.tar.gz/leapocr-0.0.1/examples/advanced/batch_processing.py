"""Advanced example: Concurrent batch processing with LeapOCR.

This example demonstrates:
- Processing multiple documents concurrently
- Using asyncio.gather for parallel processing
- Tracking results and errors
- Calculating total credits used

Requirements:
- LEAPOCR_API_KEY environment variable
"""

import asyncio
import os
from typing import List

from leapocr import JobResult, LeapOCR, ProcessOptions, PollOptions


async def process_document(
    client: LeapOCR, url: str, document_id: int
) -> tuple[int, JobResult | None, Exception | None]:
    """Process a single document and return results or error."""
    try:
        print(f"[{document_id}] Starting processing: {url}")

        result = await client.ocr.process_and_wait(
            url,
            poll_options=PollOptions(poll_interval=2.0, max_wait=180.0),
        )

        print(
            f"[{document_id}] ✓ Completed - {len(result.pages)} pages, {result.credits_used} credits"
        )
        return document_id, result, None

    except Exception as error:
        print(f"[{document_id}] ✗ Failed: {error}")
        return document_id, None, error


async def main():
    # Get API key from environment
    api_key = os.getenv("LEAPOCR_API_KEY")
    if not api_key:
        print("ERROR: LEAPOCR_API_KEY environment variable is required")
        return

    # Example URLs to process (replace with real URLs)
    documents = [
        "https://example.com/document1.pdf",
        "https://example.com/document2.pdf",
        "https://example.com/document3.pdf",
    ]

    print("=== Concurrent Batch Processing ===\n")
    print(f"Processing {len(documents)} documents concurrently...")
    print()

    async with LeapOCR(api_key) as client:
        # Process all documents concurrently
        tasks = [process_document(client, url, i + 1) for i, url in enumerate(documents)]

        # Wait for all tasks to complete
        results = await asyncio.gather(*tasks, return_exceptions=False)

        # Analyze results
        successful: List[tuple[int, JobResult]] = []
        failed: List[tuple[int, Exception]] = []

        for doc_id, result, error in results:
            if error:
                failed.append((doc_id, error))
            elif result:
                successful.append((doc_id, result))

        # Print summary
        print("\n" + "=" * 50)
        print("BATCH PROCESSING SUMMARY")
        print("=" * 50)
        print(f"Total documents: {len(documents)}")
        print(f"Successful: {len(successful)}")
        print(f"Failed: {len(failed)}")

        if successful:
            total_credits = sum(result.credits_used for _, result in successful)
            total_pages = sum(len(result.pages) for _, result in successful)
            total_time = sum(result.processing_time_seconds for _, result in successful)

            print(f"\nTotal credits used: {total_credits}")
            print(f"Total pages processed: {total_pages}")
            print(f"Total processing time: {total_time:.2f}s")
            print(f"Average time per document: {total_time / len(successful):.2f}s")

        if failed:
            print("\nFailed documents:")
            for doc_id, error in failed:
                print(f"  [{doc_id}] {error}")


if __name__ == "__main__":
    asyncio.run(main())
