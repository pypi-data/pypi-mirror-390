"""
Concise API client
"""

import os
from typing import Optional
import httpx

from .types import (
    CompressionResult,
    CompressionLevel,
    EstimationStrategy,
    TALEOptimizeResult,
    TALEValidateResult,
)
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

    def optimize_for_output(
        self,
        prompt: str,
        strategy: EstimationStrategy = "fixed",
        target_budget: Optional[int] = None,
    ) -> TALEOptimizeResult:
        """
        Optimize prompt to reduce output tokens using TALE

        TALE (Token-Budget-Aware LLM Reasoning) reduces output tokens by 60-70%
        by estimating optimal token budgets and constraining LLM generation.

        Args:
            prompt: The prompt to optimize
            strategy: Budget estimation strategy:
                - "fixed": Fast heuristic-based estimation (default, 70% confidence)
                - "zero_shot": LLM estimates its own budget (85% confidence, 1 extra call)
                - "adaptive": Uses user history (85% confidence with history)
            target_budget: Manual token budget override (skips estimation)

        Returns:
            TALEOptimizeResult with optimized prompt and budget info

        Example:
            ```python
            # Optimize prompt to reduce output tokens
            result = client.optimize_for_output(
                "Explain how binary search works",
                strategy="fixed"
            )

            print(f"Estimated budget: {result.estimated_budget} tokens")
            print(f"Optimized prompt: {result.optimized_prompt}")

            # Send optimized prompt to LLM
            llm_response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": result.optimized_prompt}]
            )

            # Expected: 60-70% fewer output tokens!
            ```
        """
        request_data = {"prompt": prompt, "strategy": strategy}
        if target_budget is not None:
            request_data["target_budget"] = target_budget

        response = self._make_request("POST", "/tale/optimize", json=request_data)

        return TALEOptimizeResult(
            optimized_prompt=response["optimized_prompt"],
            original_prompt=response["original_prompt"],
            estimated_budget=response["estimated_budget"],
            budget_metadata=response["budget_metadata"],
            prompt_additions=response["prompt_additions"],
        )

    def validate_output(
        self,
        output: str,
        budget: int,
        tolerance: float = 0.2,
    ) -> TALEValidateResult:
        """
        Validate that LLM output stayed within token budget

        Use this after receiving an LLM response to check if the model
        respected the token budget from optimize_for_output().

        Args:
            output: The LLM's generated output
            budget: The token budget (from optimize_for_output)
            tolerance: Allow budget to exceed by this % (default: 0.2 = 20%)

        Returns:
            TALEValidateResult with compliance status and metrics

        Example:
            ```python
            # 1. Optimize prompt
            optimized = client.optimize_for_output("Explain recursion")

            # 2. Get LLM response
            response = llm.complete(optimized.optimized_prompt)

            # 3. Validate output
            validation = client.validate_output(
                output=response,
                budget=optimized.estimated_budget
            )

            if validation.within_budget:
                print(f"✅ Saved {validation.tokens_saved} tokens!")
            else:
                print(f"❌ Exceeded budget by {validation.exceeded_by} tokens")
            ```
        """
        response = self._make_request(
            "POST",
            "/tale/validate",
            json={"output": output, "budget": budget, "tolerance": tolerance},
        )

        return TALEValidateResult(
            within_budget=response["within_budget"],
            actual_tokens=response["actual_tokens"],
            budget_tokens=response["budget_tokens"],
            max_allowed_tokens=response["max_allowed_tokens"],
            budget_utilization=response["budget_utilization"],
            tokens_saved=response["tokens_saved"],
            exceeded_by=response["exceeded_by"],
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
