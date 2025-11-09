"""
Concise API client
"""

import os
from typing import Optional
import httpx

from .types import CompressionResult, CompressionLevel
from .exceptions import (
    AuthenticationError,
    APIError,
    RateLimitError,
    NetworkError,
)


class Concise:
    """
    Official Concise API client

    Provides direct access to token compression endpoints.

    Example:
        ```python
        from concise import Concise

        client = Concise(api_key="your-api-key")

        result = client.compress(
            "Your long prompt here...",
            level="auto"
        )

        print(f"Saved {result.tokens_saved} tokens!")
        print(f"Compressed text: {result.compressed_text}")
        ```
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://api.concise.dev/v1",
        timeout: int = 30,
    ):
        """
        Initialize Concise client

        Args:
            api_key: Your Concise API key (or set CONCISE_API_KEY env var)
            base_url: API base URL (default: https://api.concise.dev/v1)
            timeout: Request timeout in seconds (default: 30)
        """
        self.api_key = api_key or os.getenv("CONCISE_API_KEY")
        if not self.api_key:
            raise AuthenticationError(
                "API key required. Pass api_key parameter or set CONCISE_API_KEY environment variable."
            )

        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.client = httpx.Client(timeout=timeout)

    def _make_request(
        self,
        method: str,
        endpoint: str,
        json: Optional[dict] = None,
    ) -> dict:
        """Make HTTP request to Concise API"""
        url = f"{self.base_url}{endpoint}"
        headers = {
            "X-API-Key": self.api_key,
            "Content-Type": "application/json",
        }

        try:
            response = self.client.request(
                method=method,
                url=url,
                headers=headers,
                json=json,
            )

            if response.status_code == 401:
                raise AuthenticationError("Invalid API key")
            elif response.status_code == 429:
                raise RateLimitError("Rate limit exceeded")
            elif response.status_code >= 400:
                error_detail = response.json().get("detail", "Unknown error")
                raise APIError(error_detail, status_code=response.status_code)

            return response.json()

        except httpx.TimeoutException:
            raise NetworkError("Request timed out")
        except httpx.RequestError as e:
            raise NetworkError(f"Network error: {str(e)}")

    def compress(
        self,
        text: str,
        level: CompressionLevel = "auto",
    ) -> CompressionResult:
        """
        Compress text to reduce token count

        Args:
            text: Text to compress (code or natural language)
            level: Compression level
                - "auto": Automatic strategy selection (recommended)
                - "aggressive": Maximum compression (50% reduction)
                - "balanced": Good trade-off (30% reduction)
                - "conservative": Light compression (20% reduction)

        Returns:
            CompressionResult with compressed text and metrics

        Example:
            ```python
            result = client.compress(
                "def fibonacci(n):\\n    if n <= 1:\\n        return n\\n    return fibonacci(n-1) + fibonacci(n-2)",
                level="auto"
            )

            print(f"Original: {result.original_tokens} tokens")
            print(f"Compressed: {result.compressed_tokens} tokens")
            print(f"Saved: {result.tokens_saved} tokens ({(1-result.compression_ratio)*100:.1f}%)")
            print(f"Time: {result.compression_time_ms:.0f}ms")
            ```
        """
        response = self._make_request(
            "POST",
            "/compress",
            json={"text": text, "level": level},
        )

        return CompressionResult(
            original_text=response["original_text"],
            compressed_text=response["compressed_text"],
            original_tokens=response["original_tokens"],
            compressed_tokens=response["compressed_tokens"],
            tokens_saved=response["tokens_saved"],
            compression_ratio=response["compression_ratio"],
            strategy=response["strategy"],
            compression_time_ms=response["compression_time_ms"],
            cache_hit=response.get("cache_hit"),
        )

    def health(self) -> dict:
        """
        Check API health status

        Returns:
            Dict with status and version info
        """
        return self._make_request("GET", "/health")

    def close(self):
        """Close HTTP client"""
        self.client.close()

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, *args):
        """Context manager exit"""
        self.close()
