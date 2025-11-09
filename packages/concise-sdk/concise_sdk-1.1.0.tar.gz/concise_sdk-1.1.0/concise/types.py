"""
Type definitions for Concise SDK
"""

from typing import Literal, TypedDict, Optional
from dataclasses import dataclass


CompressionLevel = Literal["auto", "aggressive", "balanced", "conservative"]
EstimationStrategy = Literal["fixed", "zero_shot", "adaptive"]


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


@dataclass
class TALEOptimizeResult:
    """Result from TALE prompt optimization"""
    optimized_prompt: str
    original_prompt: str
    estimated_budget: int
    budget_metadata: dict
    prompt_additions: dict


@dataclass
class TALEValidateResult:
    """Result from TALE output validation"""
    within_budget: bool
    actual_tokens: int
    budget_tokens: int
    max_allowed_tokens: int
    budget_utilization: float
    tokens_saved: int
    exceeded_by: int
