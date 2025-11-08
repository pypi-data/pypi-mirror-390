"""Configuration management for LeapOCR SDK."""

import os
from dataclasses import dataclass
from typing import Optional

import httpx


@dataclass
class ClientConfig:
    """Configuration for LeapOCR client.

    Attributes:
        base_url: API base URL (default: https://api.leapocr.com/api/v1)
        timeout: Request timeout in seconds (default: 30.0)
        max_retries: Maximum number of retries for transient errors (default: 3)
        retry_delay: Initial retry delay in seconds (default: 1.0)
        retry_multiplier: Exponential backoff multiplier (default: 2.0)
        http_client: Custom httpx AsyncClient (optional)
        debug: Enable debug logging (default: False)
    """

    base_url: str = "https://api.leapocr.com/api/v1"
    timeout: float = 30.0
    max_retries: int = 3
    retry_delay: float = 1.0
    retry_multiplier: float = 2.0
    http_client: Optional[httpx.AsyncClient] = None
    debug: bool = False

    @classmethod
    def from_env(cls) -> "ClientConfig":
        """Create configuration from environment variables.

        Environment variables:
            LEAPOCR_BASE_URL: Override base URL
            LEAPOCR_TIMEOUT: Override timeout
            LEAPOCR_DEBUG: Enable debug mode (1/true/yes)

        Returns:
            ClientConfig instance with values from environment
        """
        base_url = os.getenv("LEAPOCR_BASE_URL", "https://api.leapocr.com/api/v1")

        timeout_str = os.getenv("LEAPOCR_TIMEOUT", "30.0")
        try:
            timeout = float(timeout_str)
        except ValueError:
            timeout = 30.0

        debug_str = os.getenv("LEAPOCR_DEBUG", "").lower()
        debug = debug_str in ("1", "true", "yes")

        return cls(
            base_url=base_url,
            timeout=timeout,
            debug=debug,
        )
