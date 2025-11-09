"""
OpenAI-compatible wrapper with automatic compression

Drop-in replacement for the OpenAI Python SDK
"""

import os
from typing import Optional, Union, List, Dict, Any
import httpx

from .types import ChatMessage, ChatCompletionRequest, CompressionLevel
from .exceptions import (
    AuthenticationError,
    APIError,
    RateLimitError,
    NetworkError,
)


class ChatCompletion:
    """Namespace for chat completion methods"""

    def __init__(self, client: "OpenAI"):
        self.client = client

    def create(
        self,
        model: str,
        messages: List[ChatMessage],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        stream: bool = False,
        compression_enabled: bool = True,
        compression_level: CompressionLevel = "auto",
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Create a chat completion with automatic compression

        This is a drop-in replacement for openai.ChatCompletion.create()
        with automatic token compression.

        Args:
            model: OpenAI model name (e.g., "gpt-4", "gpt-3.5-turbo")
            messages: List of chat messages
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum tokens to generate
            stream: Whether to stream the response
            compression_enabled: Enable compression (default: True)
            compression_level: Compression level (default: "auto")
            **kwargs: Additional OpenAI parameters

        Returns:
            OpenAI-compatible response dict

        Example:
            ```python
            from concise import OpenAI

            client = OpenAI(api_key="your-concise-key")

            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": "Explain quantum computing"}
                ],
                compression_enabled=True,
                compression_level="balanced"
            )

            print(response.choices[0].message.content)
            ```
        """
        request_data: ChatCompletionRequest = {
            "model": model,
            "messages": messages,
        }

        if temperature is not None:
            request_data["temperature"] = temperature
        if max_tokens is not None:
            request_data["max_tokens"] = max_tokens
        if stream:
            request_data["stream"] = stream
        if compression_enabled is not None:
            request_data["compression_enabled"] = compression_enabled
        if compression_level:
            request_data["compression_level"] = compression_level

        request_data.update(kwargs)

        return self.client._make_request(
            "POST",
            "/chat/completions",
            json=request_data,
        )


class Chat:
    """Namespace for chat endpoints"""

    def __init__(self, client: "OpenAI"):
        self.completions = ChatCompletion(client)


class OpenAI:
    """
    OpenAI-compatible client with automatic compression

    Drop-in replacement for the OpenAI Python SDK that automatically
    compresses prompts to save tokens and reduce costs.

    Example:
        ```python
        # Instead of:
        # from openai import OpenAI
        # client = OpenAI(api_key="sk-...")

        # Use:
        from concise import OpenAI
        client = OpenAI(api_key="your-concise-key")

        # Everything else works the same!
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": "Hello!"}]
        )
        ```
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://api.concise.dev/v1",
        timeout: int = 60,
    ):
        """
        Initialize OpenAI-compatible client

        Args:
            api_key: Your Concise API key (or set CONCISE_API_KEY env var)
            base_url: API base URL (default: https://api.concise.dev/v1)
            timeout: Request timeout in seconds (default: 60)
        """
        self.api_key = api_key or os.getenv("CONCISE_API_KEY")
        if not self.api_key:
            raise AuthenticationError(
                "API key required. Pass api_key parameter or set CONCISE_API_KEY environment variable."
            )

        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.client = httpx.Client(timeout=timeout)

        self.chat = Chat(self)

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

    def close(self):
        """Close HTTP client"""
        self.client.close()

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, *args):
        """Context manager exit"""
        self.close()
