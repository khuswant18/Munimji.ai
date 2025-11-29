"""
Groq LLM client with caching, timeouts, and performance optimizations.
"""
import os
import time
from typing import Optional
from groq import Groq
from dotenv import load_dotenv

from .llm_cache import (
    get_cached_response_with_redis,
    set_cached_response_with_redis,
    get_cache_stats,
)
from decorators.timeit import timed_context

load_dotenv()

# Initialize Groq client with timeout
client = Groq(
    api_key=os.getenv("GROQ_API_KEY"),
    timeout=float(os.getenv("GROQ_TIMEOUT", "10.0")),  # 10 second default timeout
)

# Default model - can be overridden via env
DEFAULT_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

# Cache settings
ENABLE_CACHE = os.getenv("LLM_CACHE_ENABLED", "true").lower() == "true"


def groq_chat(
    prompt: str,
    temperature: float = 0.0,  # Changed from 0.1 to 0 for deterministic responses
    model: str = None,
    max_tokens: int = 512,  # Limit response size for faster generation
    use_cache: bool = True,
    timeout: float = None,
) -> str:
    """
    Call Groq LLM with caching and optimizations.
    
    Args:
        prompt: The prompt to send to the LLM
        temperature: Sampling temperature (0 for deterministic)
        model: Model to use (defaults to llama-3.1-8b-instant)
        max_tokens: Maximum tokens in response
        use_cache: Whether to use response caching
        timeout: Request timeout in seconds
    
    Returns:
        LLM response text
    """
    model = model or DEFAULT_MODEL
    
    # Check cache first (only for temperature=0 deterministic calls)
    if use_cache and ENABLE_CACHE and temperature == 0.0:
        cached = get_cached_response_with_redis(prompt, model)
        if cached:
            return cached
    
    # Make API call with timing
    with timed_context("llm_api_call"):
        try:
            res = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens,
            )
            response = res.choices[0].message.content
        except Exception as e:
            # On timeout or error, return empty string to trigger fallback
            print(f"Groq API error: {e}")
            return ""
    
    # Cache the response (only for deterministic calls)
    if use_cache and ENABLE_CACHE and temperature == 0.0 and response:
        set_cached_response_with_redis(prompt, response, model)
    
    return response


def groq_chat_batch(
    prompts: list[str],
    temperature: float = 0.0,
    model: str = None,
    max_tokens: int = 512,
) -> list[str]:
    """
    Process multiple prompts efficiently.
    
    Note: Groq doesn't support true batching, but this handles caching
    and could be extended for parallel calls in the future.
    """
    model = model or DEFAULT_MODEL
    results = []
    
    for prompt in prompts:
        result = groq_chat(
            prompt=prompt,
            temperature=temperature,
            model=model,
            max_tokens=max_tokens,
        )
        results.append(result)
    
    return results


def get_llm_stats() -> dict:
    """Get LLM and cache statistics."""
    return {
        "cache": get_cache_stats(),
        "model": DEFAULT_MODEL,
        "cache_enabled": ENABLE_CACHE,
    } 