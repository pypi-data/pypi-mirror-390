"""
Simplified LLM utilities for image generation package
"""
import logging
from typing import Dict, Any, Optional, List, Type
from functools import wraps
import time

from openai import OpenAI
from langchain_openai import ChatOpenAI
from pydantic import BaseModel

from config import Config

logger = logging.getLogger(__name__)

# ==========================================
# Rate Limiting
# ==========================================

class RateLimiter:
    """Simple token bucket rate limiter for API calls."""

    def __init__(self, requests_per_minute: int = 60):
        self.requests_per_minute = requests_per_minute
        self.tokens = requests_per_minute
        self.last_update = time.time()

    def acquire(self):
        """Acquire a token, blocking if necessary."""
        self._refill()
        while self.tokens < 1:
            time.sleep(0.1)
            self._refill()
        self.tokens -= 1

    def _refill(self):
        """Refill tokens based on time elapsed."""
        now = time.time()
        elapsed = now - self.last_update
        self.tokens = min(
            self.requests_per_minute,
            self.tokens + elapsed * (self.requests_per_minute / 60.0)
        )
        self.last_update = now


# Global rate limiters
_rate_limiters = {
    'openai': RateLimiter(requests_per_minute=500),
}


def with_retry_and_rate_limit(max_retries: int = 3, backoff_factor: float = 2.0):
    """Decorator to add retry logic and rate limiting to LLM calls."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            provider = kwargs.get('provider', 'openai')
            rate_limiter = _rate_limiters.get(provider)

            for attempt in range(max_retries):
                try:
                    # Acquire rate limit token
                    if rate_limiter:
                        rate_limiter.acquire()

                    return func(*args, **kwargs)

                except Exception as e:
                    error_str = str(e).lower()
                    error_type = type(e).__name__.lower()

                    # Check if it's a rate limit error
                    is_rate_limit = any(x in error_str for x in [
                        'rate limit', 'too many requests', '429', 'quota'
                    ])

                    # Check if it's a retriable error (including timeouts)
                    is_retriable = is_rate_limit or any(x in error_str or x in error_type for x in [
                        'timeout', 'timed out', 'connection', 'server error', '500', '502', '503', '504',
                        'readtimeout', 'apitimeouterror'
                    ])

                    if attempt < max_retries - 1 and is_retriable:
                        # Use longer backoff for timeouts
                        if 'timeout' in error_str or 'timeout' in error_type:
                            wait_time = (backoff_factor ** attempt) * 3
                        else:
                            wait_time = backoff_factor ** attempt

                        logger.warning(
                            f"Request failed (attempt {attempt + 1}/{max_retries}): {type(e).__name__}. "
                            f"Retrying in {wait_time:.1f}s..."
                        )
                        time.sleep(wait_time)
                    else:
                        raise

            raise RuntimeError(f"Max retries ({max_retries}) exceeded")
        return wrapper
    return decorator


# ==========================================
# OpenAI LLM Configuration
# ==========================================

llm_gpt5 = ChatOpenAI(
    model="gpt-5",
    api_key=Config.OPENAI_API_KEY,
)

openai_client = OpenAI(api_key=Config.OPENAI_API_KEY, timeout=300.0)


def limit_tokens(messages: List[Dict[str, str]], requested_tokens: int, provider: str = 'openai') -> int:
    """Calculate safe max_tokens to ensure input + output doesn't exceed model's context window"""
    # Token estimate: ~4 chars per token for English, ~2.5 for Arabic (more conservative)
    total_chars = sum(len(msg.get("content", "")) for msg in messages)
    # Detect if content is primarily Arabic (contains Arabic characters)
    has_arabic = any('\u0600' <= c <= '\u06FF' for msg in messages for c in msg.get("content", ""))
    estimated_input_tokens = int(total_chars / 2.5) if has_arabic else int(total_chars / 4)

    # Model context limits
    model_limits = {
        'openai': 128000,  # GPT-4, GPT-5 models
    }

    context_limit = model_limits.get(provider, 128000)
    safe_limit = context_limit - estimated_input_tokens - 1000  # Reserve 1000 tokens as safety buffer

    return min(requested_tokens, safe_limit)


@with_retry_and_rate_limit(max_retries=3, backoff_factor=2.0)
def produce_structured_response_openai(
    messages: List[Dict[str, str]],
    structure_model: Type[BaseModel],
    model: str = "gpt-4o",
    instructions: Optional[str] = None,
    temperature: float = 0.7,
    max_output_tokens: Optional[int] = 2048,
    provider: str = "openai",
) -> Any:
    """
    Produce a structured response using OpenAI's structured output API.

    Parameters
    ----------
    messages : List[Dict[str, str]]
        List of message dicts with 'role' and 'content' keys
    structure_model : Type[BaseModel]
        Pydantic model defining the expected response structure
    model : str
        OpenAI model to use (default: gpt-4o)
    instructions : Optional[str]
        System instructions to prepend to messages
    temperature : float
        Sampling temperature (default: 0.7)
    max_output_tokens : Optional[int]
        Maximum tokens in response (default: 2048)
    provider : str
        Provider name for rate limiting (default: openai)

    Returns
    -------
    Any
        Instance of structure_model with parsed response
    """
    # Convert to OpenAI message format
    formatted_messages = [
        {"role": m["role"], "content": m["content"]} for m in messages
    ]

    # Add system instructions if provided
    if instructions:
        formatted_messages.insert(
            0, {"role": "system", "content": instructions}
        )

    api_params: Dict[str, Any] = {
        "model": model,
        "messages": formatted_messages,
        "temperature": temperature,
        "response_format": structure_model,  # OpenAI Structured Outputs
    }

    if max_output_tokens:
        api_params["max_tokens"] = limit_tokens(
            formatted_messages, max_output_tokens, 'openai'
        )

    try:
        response = openai_client.beta.chat.completions.parse(**api_params)
        return response.choices[0].message.parsed
    except Exception as e:
        logger.error(f"OpenAI structured response failed: {e}")
        raise


# Export commonly used name
_produce_structured_response_openai = produce_structured_response_openai
