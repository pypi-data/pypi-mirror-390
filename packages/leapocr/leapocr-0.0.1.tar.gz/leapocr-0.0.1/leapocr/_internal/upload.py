"""File upload utilities for multipart S3 uploads."""

from typing import Any, BinaryIO

import httpx

from ..errors import FileError, NetworkError
from .validation import get_file_size, guess_content_type


class MultipartUploader:
    """Handle multipart file uploads to S3 via presigned URLs.

    This class manages the upload of file parts to S3 using presigned URLs
    returned from the LeapOCR API.
    """

    def __init__(self, timeout: float = 300.0):
        """Initialize the uploader.

        Args:
            timeout: Timeout for upload requests in seconds (default: 5 minutes)
        """
        # Separate HTTP client for S3 uploads (no auth needed, different domain)
        self._s3_client = httpx.AsyncClient(timeout=timeout)

    async def close(self) -> None:
        """Close the S3 HTTP client."""
        await self._s3_client.aclose()

    async def __aenter__(self) -> "MultipartUploader":
        """Context manager entry."""
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit."""
        await self.close()

    async def upload_multipart(
        self, file: BinaryIO, parts: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Upload file parts to S3 presigned URLs and return ETags.

        Args:
            file: File-like object (must support seek/read)
            parts: List of part dicts with part_number, start_byte, end_byte, upload_url

        Returns:
            List of dicts with part_number and etag for completion request

        Raises:
            FileError: If file reading fails
            NetworkError: If upload fails
        """
        completed_parts: list[dict[str, Any]] = []

        for part in parts:
            part_number = part["part_number"]
            upload_url = part["upload_url"]
            start_byte = part["start_byte"]
            end_byte = part["end_byte"]

            # Calculate chunk size (end_byte is inclusive)
            chunk_size = end_byte - start_byte + 1

            # Read chunk from file
            try:
                file.seek(start_byte)
                chunk_data = file.read(chunk_size)
            except OSError as e:
                raise FileError(
                    f"Failed to read file chunk for part {part_number}: {e}",
                    file_path=getattr(file, "name", None),
                )

            if len(chunk_data) != chunk_size:
                raise FileError(
                    f"Failed to read expected chunk size for part {part_number}: "
                    f"got {len(chunk_data)} bytes, expected {chunk_size} bytes",
                    file_path=getattr(file, "name", None),
                )

            # Upload to S3 via presigned URL (raw PUT, not multipart/form-data)
            try:
                response = await self._s3_client.put(
                    upload_url,
                    content=chunk_data,
                    headers={
                        "Content-Length": str(len(chunk_data)),
                    },
                )
                response.raise_for_status()
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 403:
                    raise NetworkError(
                        f"Presigned URL expired or invalid for part {part_number}",
                        cause=e,
                    )
                raise NetworkError(
                    f"Failed to upload part {part_number} to S3: HTTP {e.response.status_code}",
                    cause=e,
                )
            except httpx.RequestError as e:
                raise NetworkError(f"Network error uploading part {part_number}: {e}", cause=e)

            # Extract ETag from response headers
            # S3 returns ETag with quotes like: "9bb58f26192e4ba00f01e2e7b136bbd8"
            etag = response.headers.get("ETag", "").strip('"')
            if not etag:
                raise NetworkError(f"Missing ETag in S3 response for part {part_number}")

            completed_parts.append({"part_number": part_number, "etag": etag})

        return completed_parts


# Re-export utility functions
__all__ = ["MultipartUploader", "get_file_size", "guess_content_type"]
