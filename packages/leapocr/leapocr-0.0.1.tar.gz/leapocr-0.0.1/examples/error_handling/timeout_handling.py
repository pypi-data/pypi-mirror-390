"""Error handling example: Timeout and cancellation handling.

This example demonstrates:
- Setting custom timeouts
- Handling timeout errors
- Cancellation and cleanup

Requirements:
- LEAPOCR_API_KEY environment variable
"""

import asyncio
import os
import time

from leapocr import JobTimeoutError, LeapOCR, PollOptions


async def test_short_timeout(api_key: str):
    """Test with very short timeout."""
    print("1. Testing Short Timeout")
    print("   Setting 1 second timeout...")

    async with LeapOCR(api_key) as client:
        try:
            start = time.time()

            # Use very short poll options
            poll_opts = PollOptions(
                poll_interval=0.5,
                max_wait=1.0,  # Only wait 1 second
            )

            # This will likely timeout
            await client.ocr.process_and_wait(
                "https://example.com/document.pdf",
                poll_options=poll_opts,
            )

            print("   ✗ Should have timed out")

        except (JobTimeoutError, asyncio.TimeoutError, Exception) as e:
            duration = time.time() - start
            print(f"   ✓ Timed out after {duration:.2f}s")
            print(f"     Error: {type(e).__name__}")
            print(f"     Message: {str(e)[:100]}")

    print()


async def test_cancellation(api_key: str):
    """Test task cancellation."""
    print("2. Testing Task Cancellation")
    print("   Starting long-running task and cancelling it...")

    async with LeapOCR(api_key) as client:

        async def long_running_task():
            """Simulate a long-running OCR task."""
            try:
                await client.ocr.process_and_wait(
                    "https://example.com/large-document.pdf",
                    poll_options=PollOptions(max_wait=300.0),
                )
            except asyncio.CancelledError:
                print("   ✓ Task was cancelled cleanly")
                raise

        # Create and cancel task
        task = asyncio.create_task(long_running_task())

        # Wait a bit then cancel
        await asyncio.sleep(0.5)
        task.cancel()

        try:
            await task
        except asyncio.CancelledError:
            print("   ✓ Cancellation handled properly")

    print()


async def test_custom_wait_logic(api_key: str):
    """Test custom timeout with manual polling."""
    print("3. Testing Custom Wait Logic")
    print("   Implementing custom timeout with manual polling...")

    async with LeapOCR(api_key) as client:
        try:
            # Start processing
            result = await client.ocr.process_url("https://example.com/doc.pdf")
            job_id = result.job_id

            # Custom polling with timeout
            max_wait = 5.0  # 5 seconds max
            poll_interval = 1.0
            start_time = time.time()

            while True:
                elapsed = time.time() - start_time
                if elapsed > max_wait:
                    print(f"   ✓ Custom timeout after {elapsed:.2f}s")
                    break

                # Check status
                status = await client.ocr.get_job_status(job_id)
                print(f"   Status: {status.status.value} ({elapsed:.1f}s elapsed)")

                if status.status.value in ["completed", "failed"]:
                    print(f"   Job finished in {elapsed:.2f}s")
                    break

                await asyncio.sleep(poll_interval)

        except Exception as e:
            print(f"   Error (expected): {type(e).__name__}")

    print()


async def test_timeout_recommendations():
    """Show timeout recommendations."""
    print("4. Timeout Recommendations")
    print()

    recommendations = [
        ("Small documents (1-5 pages)", "30-60 seconds"),
        ("Medium documents (5-20 pages)", "1-3 minutes"),
        ("Large documents (20+ pages)", "3-10 minutes"),
        ("Batch processing", "10-30 minutes"),
    ]

    print("   Recommended timeouts by document size:")
    for doc_type, timeout in recommendations:
        print(f"     {doc_type:<35} {timeout}")

    print()
    print("   Tips:")
    print("     - Use PollOptions.max_wait for processing timeout")
    print("     - Use ClientConfig.timeout for HTTP request timeout")
    print("     - Implement exponential backoff for retries")
    print("     - Consider document size and complexity")
    print("     - Monitor and adjust based on actual performance")

    print()


async def main():
    api_key = os.getenv("LEAPOCR_API_KEY")
    if not api_key:
        print("ERROR: LEAPOCR_API_KEY environment variable is required")
        return

    print("=== Timeout Handling Examples ===\n")

    await test_short_timeout(api_key)
    await test_cancellation(api_key)
    await test_custom_wait_logic(api_key)
    await test_timeout_recommendations()

    print("=" * 50)
    print("\nBest Practices:")
    print("1. Set appropriate timeouts based on document size")
    print("2. Handle asyncio.TimeoutError and JobTimeoutError")
    print("3. Implement proper cleanup on cancellation")
    print("4. Use progress callbacks to monitor long operations")
    print("5. Consider using asyncio.wait_for() for custom timeouts")


if __name__ == "__main__":
    asyncio.run(main())
