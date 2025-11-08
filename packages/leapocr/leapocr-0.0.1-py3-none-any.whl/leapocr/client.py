"""Main LeapOCR client for document processing."""

from typing import Any

import httpx

from . import __version__
from .config import ClientConfig
from .errors import AuthenticationError
from .ocr import OCRService


class LeapOCR:
    """Main client for LeapOCR API.

    This is the primary entry point for using the LeapOCR SDK. It provides
    access to OCR operations and manages HTTP connections.

    Example:
        >>> async with LeapOCR("your-api-key") as client:
        ...     result = await client.ocr.process_and_wait("document.pdf")
        ...     print(f"Processed {result.total_pages} pages")
    """

    def __init__(self, api_key: str, config: ClientConfig | None = None) -> None:
        """Initialize the LeapOCR client.

        Args:
            api_key: Your LeapOCR API key
            config: Optional client configuration

        Raises:
            AuthenticationError: If API key is missing or empty
        """
        if not api_key or not api_key.strip():
            raise AuthenticationError("API key is required")

        self.api_key = api_key
        self.config = config or ClientConfig()

        # Setup HTTP client for API requests
        self._http_client = self._create_http_client()

        # Initialize services
        self.ocr = OCRService(self._http_client, self.config)

    def _create_http_client(self) -> httpx.AsyncClient:
        """Create configured HTTP client for API requests.

        Returns:
            Configured httpx AsyncClient
        """
        if self.config.http_client:
            return self.config.http_client

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "User-Agent": f"leapocr-python/{__version__}",
            "Content-Type": "application/json",
        }

        return httpx.AsyncClient(
            base_url=self.config.base_url,
            timeout=self.config.timeout,
            headers=headers,
        )

    async def close(self) -> None:
        """Close HTTP connections and cleanup resources.

        Should be called when done using the client, or use the client
        as an async context manager.
        """
        await self._http_client.aclose()
        if hasattr(self.ocr, "_uploader"):
            await self.ocr._uploader.close()

    async def __aenter__(self) -> "LeapOCR":
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        await self.close()

    async def health(self) -> bool:
        """Check API health status.

        Returns:
            True if API is healthy, False otherwise
        """
        try:
            response = await self._http_client.get("/health")
            return response.status_code == 200
        except Exception:
            return False
