"""Retry logic with exponential backoff for LeapOCR SDK."""

import asyncio
from collections.abc import Awaitable
from typing import Callable, TypeVar

from ..errors import LeapOCRError, NetworkError, RateLimitError

T = TypeVar("T")


def is_retryable_error(error: Exception) -> bool:
    """Check if an error should be retried.

    Args:
        error: Exception to check

    Returns:
        True if the error is retryable, False otherwise
    """
    # Rate limit errors are retryable
    if isinstance(error, RateLimitError):
        return True

    # Network errors are retryable
    if isinstance(error, NetworkError):
        return True

    # SDK errors with 5xx status codes are retryable
    if isinstance(error, LeapOCRError):
        if error.status_code and 500 <= error.status_code < 600:
            return True

    # Check for httpx errors
    try:
        import httpx

        if isinstance(error, (httpx.TimeoutException, httpx.NetworkError)):
            return True
        if isinstance(error, httpx.HTTPStatusError):
            return error.response.status_code >= 500
    except ImportError:
        pass

    return False


async def with_retry(
    operation: Callable[[], Awaitable[T]],
    max_retries: int = 3,
    retry_delay: float = 1.0,
    retry_multiplier: float = 2.0,
    is_retryable: Callable[[Exception], bool] | None = None,
) -> T:
    """Execute an async operation with exponential backoff retry.

    Args:
        operation: Async function to execute
        max_retries: Maximum number of retry attempts (default: 3)
        retry_delay: Initial delay between retries in seconds (default: 1.0)
        retry_multiplier: Multiplier for exponential backoff (default: 2.0)
        is_retryable: Optional function to determine if error is retryable

    Returns:
        Result from the operation

    Raises:
        The last exception if all retries are exhausted
    """
    is_retryable_fn = is_retryable or is_retryable_error
    last_error: Exception | None = None

    for attempt in range(max_retries + 1):
        try:
            return await operation()
        except Exception as error:
            last_error = error

            # Don't retry on last attempt
            if attempt == max_retries:
                raise

            # Check if error is retryable
            if not is_retryable_fn(error):
                raise

            # Calculate delay with exponential backoff
            if isinstance(error, RateLimitError) and error.retry_after:
                # Use server-provided retry-after if available
                delay = float(error.retry_after)
            else:
                # Exponential backoff: delay * (multiplier ^ attempt)
                delay = retry_delay * (retry_multiplier**attempt)

            # Wait before retry
            await asyncio.sleep(delay)

    # Should never reach here, but just in case
    if last_error:
        raise last_error
    raise RuntimeError("Retry loop completed without success or error")
