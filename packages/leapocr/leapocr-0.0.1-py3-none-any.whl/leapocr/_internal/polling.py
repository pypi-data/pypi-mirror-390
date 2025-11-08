"""Status polling utilities for long-running OCR jobs."""

import asyncio
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Callable

from ..errors import JobFailedError, JobTimeoutError
from ..models import JobStatusType, PollOptions

if TYPE_CHECKING:
    from ..models import JobStatus


async def poll_until_done(
    get_status_fn: Callable[[str], "JobStatus"],
    job_id: str,
    options: PollOptions | None = None,
) -> None:
    """Poll job status until completion or failure.

    Args:
        get_status_fn: Async function to get job status (takes job_id, returns JobStatus)
        job_id: Job ID to poll
        options: Polling options (interval, timeout, callbacks)

    Raises:
        JobTimeoutError: If job doesn't complete within max_wait
        JobFailedError: If job processing fails
    """
    opts = options or PollOptions()
    start_time = datetime.now()
    max_wait_td = timedelta(seconds=opts.max_wait)

    while True:
        # Check timeout
        elapsed = datetime.now() - start_time
        if elapsed > max_wait_td:
            raise JobTimeoutError(
                f"Job {job_id} did not complete within {opts.max_wait} seconds",
                job_id=job_id,
            )

        # Get current status
        status = await get_status_fn(job_id)

        # Call progress callback if provided
        if opts.on_progress:
            try:
                opts.on_progress(status)
            except Exception:
                # Don't let callback errors stop polling
                pass

        # Check if job is complete
        if status.status == JobStatusType.COMPLETED:
            return

        # Check if job failed
        if status.status == JobStatusType.FAILED:
            error_msg = status.error_message or "Job processing failed"
            raise JobFailedError(error_msg, job_id=job_id, error_details=status.error_message)

        # Wait before next poll
        await asyncio.sleep(opts.poll_interval)


async def poll_with_backoff(
    get_status_fn: Callable[[str], "JobStatus"],
    job_id: str,
    initial_interval: float = 1.0,
    max_interval: float = 30.0,
    backoff_multiplier: float = 1.5,
    max_wait: float = 300.0,
    on_progress: Callable[["JobStatus"], None] | None = None,
) -> None:
    """Poll job status with exponential backoff.

    Starts with short intervals and gradually increases delay to reduce
    API load for long-running jobs.

    Args:
        get_status_fn: Async function to get job status
        job_id: Job ID to poll
        initial_interval: Starting poll interval in seconds (default: 1.0)
        max_interval: Maximum poll interval in seconds (default: 30.0)
        backoff_multiplier: Interval multiplier after each poll (default: 1.5)
        max_wait: Maximum total wait time in seconds (default: 300.0)
        on_progress: Optional callback for progress updates

    Raises:
        JobTimeoutError: If job doesn't complete within max_wait
        JobFailedError: If job processing fails
    """
    start_time = datetime.now()
    max_wait_td = timedelta(seconds=max_wait)
    current_interval = initial_interval

    while True:
        # Check timeout
        elapsed = datetime.now() - start_time
        if elapsed > max_wait_td:
            raise JobTimeoutError(
                f"Job {job_id} did not complete within {max_wait} seconds",
                job_id=job_id,
            )

        # Get current status
        status = await get_status_fn(job_id)

        # Call progress callback if provided
        if on_progress:
            try:
                on_progress(status)
            except Exception:
                pass

        # Check if job is complete
        if status.status == JobStatusType.COMPLETED:
            return

        # Check if job failed
        if status.status == JobStatusType.FAILED:
            error_msg = status.error_message or "Job processing failed"
            raise JobFailedError(error_msg, job_id=job_id, error_details=status.error_message)

        # Wait with current interval
        await asyncio.sleep(current_interval)

        # Increase interval for next iteration (exponential backoff)
        current_interval = min(current_interval * backoff_multiplier, max_interval)
