"""
Concise Python SDK
Official Python client for the Concise API - Token compression for LLMs
"""

from .client import Concise
from .openai_wrapper import OpenAI
from .exceptions import ConciseError, AuthenticationError, APIError, RateLimitError
from .types import CompressionResult, CompressionLevel

__version__ = "1.0.0"
__all__ = [
    "Concise",
    "OpenAI",
    "ConciseError",
    "AuthenticationError",
    "APIError",
    "RateLimitError",
    "CompressionResult",
    "CompressionLevel",
]
