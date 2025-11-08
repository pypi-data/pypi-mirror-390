"""Error handling example: Demonstrating different error types and handling.

This example demonstrates:
- Catching and handling different error types
- Error inspection and recovery
- Validation errors vs API errors

Requirements:
- LEAPOCR_API_KEY environment variable
"""

import asyncio
import os

from leapocr import (
    APIError,
    AuthenticationError,
    FileError,
    JobError,
    LeapOCR,
    LeapOCRError,
    NetworkError,
    RateLimitError,
    ValidationError,
)


async def test_authentication_error():
    """Test authentication error with invalid API key."""
    print("1. Testing Authentication Error")
    print("   Creating client with empty API key...")

    try:
        LeapOCR("")
        print("   ✗ Should have raised AuthenticationError")
    except AuthenticationError as e:
        print(f"   ✓ Caught AuthenticationError: {e.message}")
        print(f"     Status code: {e.status_code}")
        print(f"     Error code: {e.code}")
    print()


async def test_validation_error(api_key: str):
    """Test validation errors with invalid inputs."""
    print("2. Testing Validation Errors")

    async with LeapOCR(api_key) as client:
        # Test invalid URL
        print("   Testing invalid URL...")
        try:
            await client.ocr.process_url("not-a-valid-url")
            print("   ✗ Should have raised an error")
        except (ValidationError, APIError, LeapOCRError) as e:
            print(f"   ✓ Caught error: {type(e).__name__}")
            print(f"     Message: {e.message}")
        print()


async def test_job_error(api_key: str):
    """Test job-related errors."""
    print("3. Testing Job Errors")

    async with LeapOCR(api_key) as client:
        # Test non-existent job
        print("   Testing non-existent job ID...")
        try:
            await client.ocr.get_job_status("non-existent-job-12345")
            print("   ✗ Should have raised an error")
        except (JobError, APIError, LeapOCRError) as e:
            print(f"   ✓ Caught error: {type(e).__name__}")
            print(f"     Message: {e.message}")
            if hasattr(e, "status_code") and e.status_code:
                print(f"     HTTP Status: {e.status_code}")
        print()


async def test_error_hierarchy(api_key: str):
    """Demonstrate error hierarchy and catching."""
    print("4. Testing Error Hierarchy")
    print("   All errors inherit from LeapOCRError")
    print("   You can catch at different levels:\n")

    async with LeapOCR(api_key) as client:
        # Example 1: Catch specific error
        print("   Example 1: Catching specific error type")
        try:
            await client.ocr.process_url("invalid-url")
        except ValidationError as e:
            print(f"   ✓ Caught ValidationError specifically: {e.message}")
        except LeapOCRError as e:
            print(f"   ✓ Caught as LeapOCRError: {e.message}")

        print()

        # Example 2: Catch base error
        print("   Example 2: Catching any LeapOCR error")
        try:
            await client.ocr.get_job_status("fake-job")
        except LeapOCRError as e:
            print(f"   ✓ Caught as LeapOCRError: {type(e).__name__}")
            print(f"     Message: {e.message}")
            print(f"     Code: {e.code}")

        print()


async def test_error_inspection(api_key: str):
    """Demonstrate error inspection and attributes."""
    print("5. Testing Error Inspection")

    async with LeapOCR(api_key) as client:
        print("   Attempting to process invalid document...")
        try:
            await client.ocr.process_url("https://nonexistent-domain-xyz.com/doc.pdf")
        except LeapOCRError as e:
            print(f"\n   Error details:")
            print(f"     Type: {type(e).__name__}")
            print(f"     Message: {e.message}")
            print(f"     Code: {e.code}")

            if hasattr(e, "status_code") and e.status_code:
                print(f"     HTTP Status: {e.status_code}")

            if hasattr(e, "response") and e.response:
                print(f"     Response: {e.response[:100]}...")

            if hasattr(e, "field") and e.field:
                print(f"     Field: {e.field}")

            # Check if error has a cause
            if e.__cause__:
                print(f"     Underlying cause: {e.__cause__}")

        print()


async def test_error_recovery():
    """Demonstrate error recovery strategies."""
    print("6. Error Recovery Strategies")
    print()

    # Strategy 1: Retry with exponential backoff
    print("   Strategy 1: Implementing retry logic")
    print("   (Built into SDK with max_retries config)")
    print("   - Network errors: Automatically retried")
    print("   - Rate limit errors: Respect retry-after")
    print("   - Server errors (5xx): Retried with backoff")
    print()

    # Strategy 2: Graceful degradation
    print("   Strategy 2: Graceful degradation")
    print("   - Catch errors and continue processing")
    print("   - Log errors for later review")
    print("   - Return partial results when possible")
    print()

    # Strategy 3: Error-specific handling
    print("   Strategy 3: Error-specific handling")
    error_handlers = {
        "AuthenticationError": "Check API key configuration",
        "RateLimitError": "Wait and retry after specified delay",
        "ValidationError": "Fix input parameters",
        "FileError": "Check file path and permissions",
        "JobError": "Check job ID and status",
        "NetworkError": "Check network connectivity",
        "APIError": "Check API status and try again",
    }

    for error_type, action in error_handlers.items():
        print(f"   - {error_type}: {action}")

    print()


async def main():
    api_key = os.getenv("LEAPOCR_API_KEY")
    if not api_key:
        print("ERROR: LEAPOCR_API_KEY environment variable is required")
        return

    print("=== Error Handling Examples ===\n")

    # Run all tests
    await test_authentication_error()
    await test_validation_error(api_key)
    await test_job_error(api_key)
    await test_error_hierarchy(api_key)
    await test_error_inspection(api_key)
    await test_error_recovery()

    print("=" * 50)
    print("\nBest Practices:")
    print("1. Always catch LeapOCRError for SDK-specific errors")
    print("2. Inspect error attributes (code, status_code, message)")
    print("3. Log errors with context for debugging")
    print("4. Implement appropriate retry strategies")
    print("5. Provide user-friendly error messages")


if __name__ == "__main__":
    asyncio.run(main())
