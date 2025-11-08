"""Input validation utilities for LeapOCR SDK."""

import os
from dataclasses import dataclass
from pathlib import Path
from typing import BinaryIO, Union

from ..errors import FileError

# Maximum file size: 100MB
MAX_FILE_SIZE = 100 * 1024 * 1024

# Maximum instructions length
MAX_INSTRUCTIONS_LENGTH = 10000

# Supported file extensions
SUPPORTED_EXTENSIONS = {
    ".pdf",
    ".png",
    ".jpg",
    ".jpeg",
    ".tiff",
    ".tif",
}


@dataclass
class ValidationResult:
    """Result of file validation."""

    valid: bool
    error: str | None = None
    warnings: list[str] | None = None


def validate_file(
    file_path: Union[str, Path],
    max_size: int = MAX_FILE_SIZE,
    allowed_types: set[str] | None = None,
) -> ValidationResult:
    """Validate a file before upload.

    Args:
        file_path: Path to the file to validate
        max_size: Maximum file size in bytes (default: 100MB)
        allowed_types: Set of allowed file extensions (default: SUPPORTED_EXTENSIONS)

    Returns:
        ValidationResult with validation status and any errors/warnings
    """
    path = Path(file_path)
    allowed = allowed_types or SUPPORTED_EXTENSIONS
    warnings: list[str] = []

    # Check if file exists
    if not path.exists():
        return ValidationResult(valid=False, error=f"File not found: {path}")

    # Check if it's a file (not a directory)
    if not path.is_file():
        return ValidationResult(valid=False, error=f"Not a file: {path}")

    # Check if file is readable
    if not os.access(path, os.R_OK):
        return ValidationResult(valid=False, error=f"File not readable: {path}")

    # Check file size
    try:
        file_size = path.stat().st_size
    except OSError as e:
        return ValidationResult(valid=False, error=f"Cannot stat file: {e}")

    if file_size == 0:
        return ValidationResult(valid=False, error="File is empty")

    if file_size > max_size:
        return ValidationResult(
            valid=False,
            error=f"File size ({file_size:,} bytes) exceeds maximum ({max_size:,} bytes)",
        )

    # Add warning for large files (>50MB will use multipart upload)
    if file_size > 50 * 1024 * 1024:
        warnings.append(f"Large file ({file_size:,} bytes) will use multipart upload")

    # Check file extension
    ext = path.suffix.lower()
    if ext not in allowed:
        return ValidationResult(
            valid=False,
            error=f"Unsupported file type: {ext}. Supported types: {', '.join(sorted(allowed))}",
        )

    return ValidationResult(valid=True, warnings=warnings or None)


def get_file_size(file: Union[str, Path, BinaryIO]) -> int:
    """Get file size in bytes.

    Args:
        file: File path or file-like object

    Returns:
        File size in bytes

    Raises:
        FileError: If file size cannot be determined
    """
    if isinstance(file, (str, Path)):
        try:
            return Path(file).stat().st_size
        except OSError as e:
            raise FileError(f"Cannot determine file size: {e}", file_path=str(file))

    # File-like object
    if hasattr(file, "seek") and hasattr(file, "tell"):
        try:
            # Save current position
            current_pos = file.tell()
            # Seek to end
            file.seek(0, 2)
            size = file.tell()
            # Restore position
            file.seek(current_pos)
            return size
        except OSError as e:
            raise FileError(f"Cannot determine file size: {e}")

    raise FileError("Cannot determine file size - unsupported file type")


def guess_content_type(filename: str) -> str:
    """Guess content type from filename extension.

    Args:
        filename: Filename to analyze

    Returns:
        MIME type string
    """
    ext = Path(filename).suffix.lower()
    content_types = {
        ".pdf": "application/pdf",
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".tiff": "image/tiff",
        ".tif": "image/tiff",
    }
    return content_types.get(ext, "application/octet-stream")


def validate_instructions(instructions: str) -> ValidationResult:
    """Validate processing instructions.

    Args:
        instructions: Instructions text to validate

    Returns:
        ValidationResult with validation status
    """
    if not instructions:
        return ValidationResult(valid=True)

    if len(instructions) > MAX_INSTRUCTIONS_LENGTH:
        return ValidationResult(
            valid=False,
            error=f"Instructions too long ({len(instructions)} characters). "
            f"Maximum allowed is {MAX_INSTRUCTIONS_LENGTH} characters.",
        )

    return ValidationResult(valid=True)
