"""Exception hierarchy for LeapOCR SDK."""

from typing import Any, Optional


class LeapOCRError(Exception):
    """Base exception for all LeapOCR SDK errors."""

    def __init__(
        self,
        message: str,
        code: Optional[str] = None,
        status_code: Optional[int] = None,
        details: Optional[Any] = None,
        cause: Optional[Exception] = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details
        if cause is not None:
            self.__cause__ = cause


class AuthenticationError(LeapOCRError):
    """Authentication failed - invalid or missing API key."""

    def __init__(
        self,
        message: str = "Authentication failed - invalid or missing API key",
        **kwargs: Any,
    ) -> None:
        super().__init__(message, code="authentication_error", status_code=401, **kwargs)


class RateLimitError(LeapOCRError):
    """Rate limit exceeded."""

    def __init__(
        self,
        message: str,
        retry_after: Optional[int] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, code="rate_limit_error", status_code=429, **kwargs)
        self.retry_after = retry_after


class ValidationError(LeapOCRError):
    """Validation error - invalid input parameters."""

    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, code="validation_error", status_code=400, **kwargs)
        self.field = field


class FileError(LeapOCRError):
    """File-related error (not found, too large, invalid type, etc)."""

    def __init__(
        self,
        message: str,
        file_path: Optional[str] = None,
        file_size: Optional[int] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, code="file_error", **kwargs)
        self.file_path = file_path
        self.file_size = file_size


class JobError(LeapOCRError):
    """Base class for job-related errors."""

    def __init__(
        self,
        message: str,
        job_id: str,
        code: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, code=code or "job_error", **kwargs)
        self.job_id = job_id


class JobFailedError(JobError):
    """Job processing failed."""

    def __init__(
        self,
        message: str,
        job_id: str,
        error_details: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, job_id, code="job_failed", **kwargs)
        self.error_details = error_details


class JobTimeoutError(JobError):
    """Job processing timeout."""

    def __init__(
        self,
        message: str,
        job_id: str,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, job_id, code="job_timeout", **kwargs)


class NetworkError(LeapOCRError):
    """Network connectivity error."""

    def __init__(
        self,
        message: str,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, code="network_error", **kwargs)


class APIError(LeapOCRError):
    """API returned an error response."""

    def __init__(
        self,
        message: str,
        status_code: int,
        response: Optional[Any] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, code="api_error", status_code=status_code, **kwargs)
        self.response = response


class InsufficientCreditsError(LeapOCRError):
    """Insufficient credits to process the request."""

    def __init__(
        self,
        message: str = "Insufficient credits to process this request",
        credits_available: Optional[int] = None,
        credits_required: Optional[int] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, code="insufficient_credits", status_code=402, **kwargs)
        self.credits_available = credits_available
        self.credits_required = credits_required
