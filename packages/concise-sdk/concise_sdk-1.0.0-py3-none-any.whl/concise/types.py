"""
Type definitions for Concise SDK
"""

from typing import Literal, TypedDict, Optional
from dataclasses import dataclass


CompressionLevel = Literal["auto", "aggressive", "balanced", "conservative"]


@dataclass
class CompressionResult:
    """Result from compression operation"""
    original_text: str
    compressed_text: str
    original_tokens: int
    compressed_tokens: int
    tokens_saved: int
    compression_ratio: float
    strategy: str
    compression_time_ms: float
    cache_hit: Optional[bool] = None


class ChatMessage(TypedDict):
    """OpenAI-style chat message"""
    role: Literal["system", "user", "assistant"]
    content: str


class ChatCompletionRequest(TypedDict, total=False):
    """OpenAI-style chat completion request"""
    model: str
    messages: list[ChatMessage]
    temperature: Optional[float]
    max_tokens: Optional[int]
    stream: Optional[bool]
    compression_enabled: Optional[bool]
    compression_level: Optional[CompressionLevel]
