"""Unit tests for error classes."""

import pytest

from leapocr.errors import (
    APIError,
    AuthenticationError,
    FileError,
    InsufficientCreditsError,
    JobError,
    JobFailedError,
    JobTimeoutError,
    LeapOCRError,
    NetworkError,
    RateLimitError,
    ValidationError,
)


class TestLeapOCRError:
    """Tests for base LeapOCRError."""

    def test_basic_error(self):
        err = LeapOCRError("Test error")
        assert str(err) == "Test error"
        assert err.message == "Test error"
        assert err.code is None
        assert err.status_code is None
        assert err.details is None

    def test_error_with_code(self):
        err = LeapOCRError("Test error", code="test_error")
        assert err.code == "test_error"

    def test_error_with_status_code(self):
        err = LeapOCRError("Test error", status_code=400)
        assert err.status_code == 400

    def test_error_with_details(self):
        details = {"field": "value"}
        err = LeapOCRError("Test error", details=details)
        assert err.details == details

    def test_error_with_cause(self):
        cause = ValueError("original error")
        err = LeapOCRError("Test error", cause=cause)
        assert err.__cause__ == cause


class TestAuthenticationError:
    """Tests for AuthenticationError."""

    def test_authentication_error(self):
        err = AuthenticationError("Invalid API key")
        assert isinstance(err, LeapOCRError)
        assert str(err) == "Invalid API key"
        assert err.code == "authentication_error"
        assert err.status_code == 401

    def test_authentication_error_inheritance(self):
        err = AuthenticationError("Test")
        assert isinstance(err, LeapOCRError)


class TestRateLimitError:
    """Tests for RateLimitError."""

    def test_rate_limit_error(self):
        err = RateLimitError("Rate limit exceeded", retry_after=60)
        assert isinstance(err, LeapOCRError)
        assert err.retry_after == 60
        assert err.code == "rate_limit_error"
        assert err.status_code == 429

    def test_rate_limit_without_retry_after(self):
        err = RateLimitError("Rate limit exceeded")
        assert err.retry_after is None


class TestValidationError:
    """Tests for ValidationError."""

    def test_validation_error_with_field(self):
        err = ValidationError("Invalid value", field="email")
        assert isinstance(err, LeapOCRError)
        assert err.field == "email"
        assert err.code == "validation_error"
        assert err.status_code == 400

    def test_validation_error_without_field(self):
        err = ValidationError("Invalid request")
        assert err.field is None


class TestFileError:
    """Tests for FileError."""

    def test_file_error(self):
        err = FileError("File not found", file_path="/path/to/file.pdf")
        assert isinstance(err, LeapOCRError)
        assert err.file_path == "/path/to/file.pdf"
        assert err.code == "file_error"

    def test_file_error_with_size(self):
        err = FileError("File too large", file_path="/file.pdf", file_size=100000000)
        assert err.file_size == 100000000


class TestJobError:
    """Tests for JobError and subclasses."""

    def test_job_error(self):
        err = JobError("Job error", job_id="job-123")
        assert isinstance(err, LeapOCRError)
        assert err.job_id == "job-123"
        assert err.code == "job_error"

    def test_job_error_with_custom_code(self):
        err = JobError("Job error", job_id="job-123", code="custom_error")
        assert err.code == "custom_error"

    def test_job_failed_error(self):
        err = JobFailedError("Processing failed", job_id="job-123")
        assert isinstance(err, JobError)
        assert isinstance(err, LeapOCRError)
        assert err.job_id == "job-123"
        assert err.code == "job_failed"
        assert err.error_details is None

    def test_job_failed_with_details(self):
        err = JobFailedError(
            "Processing failed", job_id="job-123", error_details="Invalid PDF format"
        )
        assert err.error_details == "Invalid PDF format"

    def test_job_timeout_error(self):
        err = JobTimeoutError("Job timed out", job_id="job-456")
        assert isinstance(err, JobError)
        assert err.job_id == "job-456"
        assert err.code == "job_timeout"


class TestNetworkError:
    """Tests for NetworkError."""

    def test_network_error(self):
        err = NetworkError("Connection timeout")
        assert isinstance(err, LeapOCRError)
        assert err.code == "network_error"

    def test_network_error_with_cause(self):
        original = ConnectionError("Failed to connect")
        err = NetworkError("Connection timeout", cause=original)
        assert err.__cause__ == original


class TestAPIError:
    """Tests for APIError."""

    def test_api_error(self):
        err = APIError("Internal server error", status_code=500, response="Server error")
        assert isinstance(err, LeapOCRError)
        assert err.status_code == 500
        assert err.response == "Server error"
        assert err.code == "api_error"

    def test_api_error_without_response(self):
        err = APIError("Server error", status_code=500)
        assert err.response is None


class TestInsufficientCreditsError:
    """Tests for InsufficientCreditsError."""

    def test_insufficient_credits(self):
        err = InsufficientCreditsError(
            "Not enough credits", credits_available=10, credits_required=50
        )
        assert isinstance(err, LeapOCRError)
        assert err.credits_available == 10
        assert err.credits_required == 50
        assert err.code == "insufficient_credits"
        assert err.status_code == 402

    def test_insufficient_credits_without_amounts(self):
        err = InsufficientCreditsError("Not enough credits")
        assert err.credits_available is None
        assert err.credits_required is None


class TestErrorHierarchy:
    """Tests for error inheritance and hierarchy."""

    def test_all_errors_inherit_from_base(self):
        """All custom errors should inherit from LeapOCRError."""
        errors = [
            AuthenticationError("test"),
            RateLimitError("test"),
            ValidationError("test"),
            FileError("test", file_path="/test"),
            JobError("test", job_id="123"),
            JobFailedError("test", job_id="123"),
            JobTimeoutError("test", job_id="123"),
            NetworkError("test"),
            APIError("test", status_code=500),
            InsufficientCreditsError("test"),
        ]

        for err in errors:
            assert isinstance(err, LeapOCRError)
            assert isinstance(err, Exception)

    def test_job_subclass_hierarchy(self):
        """JobFailedError and JobTimeoutError should inherit from JobError."""
        failed = JobFailedError("test", job_id="123")
        timeout = JobTimeoutError("test", job_id="456")

        assert isinstance(failed, JobError)
        assert isinstance(timeout, JobError)

    def test_error_catching(self):
        """Test that errors can be caught at different hierarchy levels."""
        # Can catch specific error
        with pytest.raises(ValidationError):
            raise ValidationError("test")

        # Can catch as base error
        with pytest.raises(LeapOCRError):
            raise ValidationError("test")

        # Can catch job subclass as JobError
        with pytest.raises(JobError):
            raise JobFailedError("test", job_id="123")
