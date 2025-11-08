"""Unit tests for validation functions."""

import pytest

from leapocr._internal.validation import (
    MAX_FILE_SIZE,
    MAX_INSTRUCTIONS_LENGTH,
    SUPPORTED_EXTENSIONS,
    ValidationResult,
    guess_content_type,
    validate_file,
    validate_instructions,
)


class TestGuessContentType:
    """Tests for content type guessing."""

    def test_pdf_extension(self):
        assert guess_content_type("document.pdf") == "application/pdf"
        assert guess_content_type("document.PDF") == "application/pdf"

    def test_unknown_extension(self):
        assert guess_content_type("document.txt") == "application/octet-stream"
        assert guess_content_type("file.unknown") == "application/octet-stream"

    def test_no_extension(self):
        assert guess_content_type("document") == "application/octet-stream"

    def test_multiple_extensions(self):
        assert guess_content_type("document.backup.pdf") == "application/pdf"


class TestValidateFile:
    """Tests for file validation."""

    def test_valid_pdf_file(self, tmp_path):
        """Test validation of valid PDF file."""
        test_file = tmp_path / "test.pdf"
        test_file.write_bytes(b"%PDF-1.4\n" + b"content" * 100)

        result = validate_file(test_file)
        assert result.valid is True
        assert result.error is None

    def test_file_not_found(self, tmp_path):
        """Test validation of non-existent file."""
        test_file = tmp_path / "nonexistent.pdf"

        result = validate_file(test_file)
        assert result.valid is False
        assert "not found" in result.error.lower()

    def test_unsupported_extension(self, tmp_path):
        """Test validation of unsupported file type."""
        test_file = tmp_path / "document.txt"
        test_file.write_text("content")

        result = validate_file(test_file)
        assert result.valid is False
        assert "unsupported file type" in result.error.lower()

    def test_no_extension(self, tmp_path):
        """Test validation of file without extension."""
        test_file = tmp_path / "document"
        test_file.write_bytes(b"content")

        result = validate_file(test_file)
        assert result.valid is False
        assert "unsupported" in result.error.lower()

    def test_file_too_large(self, tmp_path):
        """Test validation of file exceeding size limit."""
        test_file = tmp_path / "large.pdf"
        # Create a file larger than MAX_FILE_SIZE
        test_file.write_bytes(b"x" * (MAX_FILE_SIZE + 1))

        result = validate_file(test_file)
        assert result.valid is False
        assert "exceeds maximum" in result.error

    def test_file_size_warning(self, tmp_path):
        """Test validation warns for files > 50MB."""
        test_file = tmp_path / "medium.pdf"
        # Create a file > 50MB but < 100MB
        test_file.write_bytes(b"x" * (51 * 1024 * 1024))

        result = validate_file(test_file)
        assert result.valid is True
        assert result.warnings is not None
        assert len(result.warnings) > 0
        assert "multipart" in result.warnings[0].lower()

    def test_empty_file(self, tmp_path):
        """Test validation of empty file."""
        test_file = tmp_path / "empty.pdf"
        test_file.write_bytes(b"")

        result = validate_file(test_file)
        assert result.valid is False
        assert "empty" in result.error.lower()

    def test_directory_instead_of_file(self, tmp_path):
        """Test validation when path is a directory."""
        test_dir = tmp_path / "testdir"
        test_dir.mkdir()

        result = validate_file(test_dir)
        assert result.valid is False
        assert "not a file" in result.error.lower()


class TestValidateInstructions:
    """Tests for instruction validation."""

    def test_empty_instructions(self):
        """Empty instructions are valid."""
        result = validate_instructions("")
        assert result.valid is True

    def test_normal_instructions(self):
        """Normal length instructions are valid."""
        instructions = "Extract all invoice details including date, amount, and vendor"
        result = validate_instructions(instructions)
        assert result.valid is True

    def test_max_length_instructions(self):
        """Instructions at max length are valid."""
        instructions = "a" * MAX_INSTRUCTIONS_LENGTH
        result = validate_instructions(instructions)
        assert result.valid is True

    def test_too_long_instructions(self):
        """Instructions exceeding max length are invalid."""
        instructions = "a" * (MAX_INSTRUCTIONS_LENGTH + 1)
        result = validate_instructions(instructions)
        assert result.valid is False
        assert "too long" in result.error.lower()

    def test_instructions_with_unicode(self):
        """Unicode characters in instructions."""
        instructions = "Extract données françaises et información española"
        result = validate_instructions(instructions)
        assert result.valid is True


class TestValidationResult:
    """Tests for ValidationResult model."""

    def test_valid_result(self):
        result = ValidationResult(valid=True)
        assert result.valid is True
        assert result.error is None
        assert result.warnings is None

    def test_invalid_result_with_error(self):
        result = ValidationResult(valid=False, error="File not found")
        assert result.valid is False
        assert result.error == "File not found"

    def test_valid_result_with_warnings(self):
        result = ValidationResult(valid=True, warnings=["Large file detected"])
        assert result.valid is True
        assert result.warnings == ["Large file detected"]


class TestConstants:
    """Test validation constants."""

    def test_max_file_size(self):
        assert MAX_FILE_SIZE == 100 * 1024 * 1024  # 100MB

    def test_max_instructions_length(self):
        assert MAX_INSTRUCTIONS_LENGTH == 10000

    def test_supported_extensions(self):
        assert ".pdf" in SUPPORTED_EXTENSIONS
        assert len(SUPPORTED_EXTENSIONS) >= 1
