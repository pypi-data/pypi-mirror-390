"""Basic example: Process a local PDF file with LeapOCR.

This example demonstrates:
- Creating a LeapOCR client
- Processing a local PDF file
- Waiting for completion
- Accessing results

Requirements:
- LEAPOCR_API_KEY environment variable
- A sample PDF file (or it will be skipped)
"""

import asyncio
import os
from pathlib import Path

from leapocr import Format, LeapOCR, Model, ProcessOptions


async def main():
    # Get API key from environment
    api_key = os.getenv("LEAPOCR_API_KEY")
    if not api_key:
        print("ERROR: LEAPOCR_API_KEY environment variable is required")
        return

    # Check for sample file
    sample_file = Path("sample-document.pdf")
    if not sample_file.exists():
        print(f"Sample file {sample_file} not found")
        print("Create a sample-document.pdf file in this directory to run this example")
        return

    print("=== Processing Local File ===\n")
    print(f"File: {sample_file}")

    # Create LeapOCR client
    async with LeapOCR(api_key) as client:
        # Process the file with options
        print("\nStarting OCR processing...")
        result = await client.ocr.process_and_wait(
            sample_file,
            options=ProcessOptions(
                format=Format.STRUCTURED,
                model=Model.STANDARD_V1,
                instructions="Extract all text and identify key information",
            ),
        )

        # Print results
        print("\n✓ Processing completed successfully!")
        print(f"  Credits used: {result.credits_used}")
        print(f"  Processing time: {result.processing_time_seconds:.2f}s")
        print(f"  Pages processed: {len(result.pages)}")
        print(f"  File name: {result.file_name}")
        print(f"  Model used: {result.model}")

        # Print first page text (truncated)
        if result.pages:
            first_page = result.pages[0]
            text_preview = (
                first_page.text[:200] + "..." if len(first_page.text) > 200 else first_page.text
            )
            print(f"\nFirst page text preview:\n{text_preview}")

            if first_page.metadata.processing_ms:
                print(f"\nFirst page processing time: {first_page.metadata.processing_ms}ms")


if __name__ == "__main__":
    asyncio.run(main())
