# Concise Python SDK

Official Python client for [Concise](https://concise.dev) - Token compression for LLMs.

**Full-stack LLM cost optimization platform**

- Input compression: 50% reduction
- Output optimization: 60-70% reduction
- **Combined: 70% total cost savings**

Works with GPT-4, Claude, Gemini, all LLMs.

## Installation

```bash
pip install concise-sdk
```

## Quick Start

### Direct Compression API

```python
from concise import Concise

client = Concise(api_key="your-api-key")

result = client.compress(
    "Your long prompt here...",
    level="auto"
)

print(f"Original: {result.original_tokens} tokens")
print(f"Compressed: {result.compressed_tokens} tokens")
print(f"Saved: {result.tokens_saved} tokens ({(1-result.compression_ratio)*100:.1f}%)")
print(f"Compressed text: {result.compressed_text}")
```

### OpenAI Drop-in Replacement

Replace your OpenAI import with Concise for automatic compression:

```python
# Before:
# from openai import OpenAI

# After:
from concise import OpenAI

client = OpenAI(api_key="your-concise-key")

response = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Explain quantum computing in simple terms"}
    ],
    compression_enabled=True,  # Automatic token compression
    compression_level="balanced"
)

print(response.choices[0].message.content)
```

## Features

### Input Optimization (Compression)
- **Direct Compression API** - Compress any text before sending to LLMs
- **OpenAI Drop-in** - Replace `from openai import OpenAI` with `from concise import OpenAI`
- **Automatic Strategy Selection** - Detects Python code vs natural language
- **GPU-Accelerated** - 285ms compression time (or instant with caching)
- **Zero Context Loss** - Preserves semantic meaning

### Output Optimization (NEW - TALE)
- **Token Budget Prompting** - Reduce output tokens by 60-70%
- **Budget Estimation** - 3 strategies: fixed, zero_shot, adaptive
- **Output Validation** - Check if LLM stayed within budget
- **LLM-Agnostic** - Works with all models (GPT-4, Claude, Gemini, etc.)
- **Quality Retention** - 95%+ accuracy maintained

### Developer Experience
- **Type Hints** - Full type annotations for better IDE support
- **Error Handling** - Comprehensive exception types

## Compression Levels

| Level | Reduction | Use Case |
|-------|-----------|----------|
| `auto` | 30-50% | Automatic strategy (recommended) |
| `aggressive` | 50% | Maximum compression, natural language |
| `balanced` | 30% | Good trade-off |
| `conservative` | 20% | Light compression, preserve structure |

## Examples

### Full-Stack Optimization (Input + Output)

Combine compression and TALE for maximum savings:

```python
from concise import Concise
import openai

client = Concise(api_key="your-api-key")

prompt = "Write a function to implement binary search"

# 1. Compress INPUT tokens (50% reduction)
compressed = client.compress(prompt, level="auto")
print(f"Input: {compressed.tokens_saved} tokens saved")

# 2. Optimize for OUTPUT tokens (60-70% reduction)
optimized = client.optimize_for_output(
    compressed.compressed_text,
    strategy="fixed"
)
print(f"Expected output budget: {optimized.estimated_budget} tokens")

# 3. Send to LLM
response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[{"role": "user", "content": optimized.optimized_prompt}]
)

# 4. Validate savings
validation = client.validate_output(
    output=response.choices[0].message.content,
    budget=optimized.estimated_budget
)
print(f"Output: {validation.tokens_saved} tokens saved")

# Result: ~70% total cost reduction!
```

### Output Optimization (TALE)

Reduce output tokens by 60-70%:

```python
from concise import Concise

client = Concise(api_key="your-api-key")

# Optimize prompt to reduce output
result = client.optimize_for_output(
    "Explain how binary search works",
    strategy="fixed"  # or "zero_shot", "adaptive"
)

print(f"Estimated budget: {result.estimated_budget} tokens")
print(f"Optimized prompt: {result.optimized_prompt}")

# Send to your LLM...
# The LLM will generate 60-70% fewer tokens while maintaining quality
```

**Strategies:**
- `fixed`: Fast heuristic (70% confidence, <10ms)
- `zero_shot`: LLM self-estimation (85% confidence, 1 extra call)
- `adaptive`: User history-based (85% confidence)

### Python Code Compression

```python
from concise import Concise

client = Concise(api_key="your-api-key")

code = """
def fibonacci(n):
    '''Calculate fibonacci number'''
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
"""

result = client.compress(code, level="auto")
# Strategy: token_compression_code
# Reduction: 39%
# Time: 27ms
```

### Natural Language Compression

```python
result = client.compress(
    "FastAPI is a modern, fast web framework for building APIs with Python 3.8+",
    level="aggressive"
)
# Strategy: token_compression_text
# Reduction: 50%
# Time: 285ms (or 0ms if cached)
```

### Using with OpenAI

```python
from concise import OpenAI

client = OpenAI(api_key="your-concise-key")

response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {
            "role": "system",
            "content": "You are a Python expert. Help users write clean, efficient code."
        },
        {
            "role": "user",
            "content": "Write a function to validate email addresses using regex"
        }
    ],
    compression_enabled=True,
    compression_level="balanced"
)

print(response.choices[0].message.content)
```

### Context Manager

```python
from concise import Concise

with Concise(api_key="your-api-key") as client:
    result = client.compress("Long text here...")
    print(f"Saved {result.tokens_saved} tokens")
```

### Environment Variable

Set `CONCISE_API_KEY` environment variable:

```bash
export CONCISE_API_KEY=your-api-key
```

```python
from concise import Concise

# API key loaded from environment
client = Concise()
```

## Error Handling

```python
from concise import Concise, AuthenticationError, APIError, RateLimitError

client = Concise(api_key="your-api-key")

try:
    result = client.compress("text")
except AuthenticationError:
    print("Invalid API key")
except RateLimitError:
    print("Rate limit exceeded")
except APIError as e:
    print(f"API error: {e} (status: {e.status_code})")
```

## Performance

| Type | Strategy | Reduction | Time |
|------|----------|-----------|------|
| Python code | python-minifier | 39% | 27ms |
| Natural language | LLMLingua-2 GPU | 50% | 285ms |
| Cached requests | Cache hit | 50% | 0ms |

### Caching

Concise automatically caches compression results:
- First request: GPU compression (285ms)
- Repeated requests: Instant (0ms)
- 240,000x speedup for cached requests

## API Reference

### `Concise`

Main client for direct compression API.

#### `__init__(api_key, base_url, timeout)`

Initialize client.

**Parameters:**
- `api_key` (str, optional): Your Concise API key
- `base_url` (str, optional): API base URL (default: https://api.concise.dev/v1)
- `timeout` (int, optional): Request timeout in seconds (default: 30)

#### `compress(text, level)`

Compress text to reduce token count.

**Parameters:**
- `text` (str): Text to compress
- `level` (str): Compression level ("auto", "aggressive", "balanced", "conservative")

**Returns:**
- `CompressionResult`: Object with compression metrics

#### `optimize_for_output(prompt, strategy, target_budget)`

Optimize prompt to reduce output tokens using TALE.

**Parameters:**
- `prompt` (str): Prompt to optimize
- `strategy` (str): Estimation strategy ("fixed", "zero_shot", "adaptive")
- `target_budget` (int, optional): Manual token budget override

**Returns:**
- `TALEOptimizeResult`: Optimized prompt and budget info

#### `validate_output(output, budget, tolerance)`

Validate that LLM output stayed within token budget.

**Parameters:**
- `output` (str): LLM's generated output
- `budget` (int): Token budget from optimize_for_output
- `tolerance` (float): Allow budget to exceed by this % (default: 0.2)

**Returns:**
- `TALEValidateResult`: Compliance status and metrics

#### `health()`

Check API health status.

**Returns:**
- `dict`: Status and version info

### `OpenAI`

OpenAI-compatible client with automatic compression.

#### `chat.completions.create()`

Create chat completion with compression.

**Additional Parameters:**
- `compression_enabled` (bool): Enable compression (default: True)
- `compression_level` (str): Compression level (default: "auto")

## Types

### `CompressionResult`

```python
@dataclass
class CompressionResult:
    original_text: str
    compressed_text: str
    original_tokens: int
    compressed_tokens: int
    tokens_saved: int
    compression_ratio: float
    strategy: str
    compression_time_ms: float
    cache_hit: Optional[bool]
```

### `TALEOptimizeResult`

```python
@dataclass
class TALEOptimizeResult:
    optimized_prompt: str
    original_prompt: str
    estimated_budget: int
    budget_metadata: dict
    prompt_additions: dict
```

### `TALEValidateResult`

```python
@dataclass
class TALEValidateResult:
    within_budget: bool
    actual_tokens: int
    budget_tokens: int
    max_allowed_tokens: int
    budget_utilization: float
    tokens_saved: int
    exceeded_by: int
```

## Requirements

- Python 3.8+
- httpx>=0.25.0

## Getting Your API Key

1. Sign up at [concise.dev](https://concise.dev)
2. Create an API key in the dashboard
3. Use the key with this SDK

## Support

- Documentation: [docs.concise.dev](https://docs.concise.dev)
- Issues: [github.com/concise/python-sdk/issues](https://github.com/concise/python-sdk/issues)
- Email: support@concise.dev

## License

MIT License - see LICENSE file for details
