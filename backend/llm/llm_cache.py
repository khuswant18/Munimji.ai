"""
LLM Response Cache with LRU in-memory cache and optional Redis fallback.

This module provides caching for LLM responses to reduce duplicate calls
and improve latency for identical prompts.

Features:
- In-memory LRU cache with TTL
- Thread-safe operations
- Cache key based on prompt hash + model name
- Optional Redis fallback for distributed caching
"""
import hashlib
import time
import threading
from typing import Optional, Dict, Any, Tuple
from collections import OrderedDict
import json
import os


class LRUCache:
    """Thread-safe LRU cache with TTL support."""
    
    def __init__(self, max_size: int = 1000, ttl_seconds: int = 300):
        """
        Initialize LRU cache.
        
        Args:
            max_size: Maximum number of items to store
            ttl_seconds: Time-to-live for cache entries (default 5 minutes)
        """
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self._cache: OrderedDict[str, Tuple[Any, float]] = OrderedDict()
        self._lock = threading.RLock()
        self._hits = 0
        self._misses = 0
    
    def _make_key(self, prompt: str, model: str = "") -> str:
        """Create cache key from prompt hash and model name."""
        content = f"{model}:{prompt}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def get(self, prompt: str, model: str = "") -> Optional[str]:
        """
        Get cached response for prompt.
        
        Returns None if not found or expired.
        """
        key = self._make_key(prompt, model)
        
        with self._lock:
            if key not in self._cache:
                self._misses += 1
                return None
            
            value, timestamp = self._cache[key]
            
            # Check TTL
            if time.time() - timestamp > self.ttl_seconds:
                del self._cache[key]
                self._misses += 1
                return None
            
            # Move to end (most recently used)
            self._cache.move_to_end(key)
            self._hits += 1
            return value
    
    def set(self, prompt: str, response: str, model: str = ""):
        """Store response in cache."""
        key = self._make_key(prompt, model)
        
        with self._lock:
            # Remove oldest if at capacity
            while len(self._cache) >= self.max_size:
                self._cache.popitem(last=False)
            
            self._cache[key] = (response, time.time())
    
    def clear(self):
        """Clear all cached entries."""
        with self._lock:
            self._cache.clear()
            self._hits = 0
            self._misses = 0
    
    def stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        with self._lock:
            total = self._hits + self._misses
            hit_rate = self._hits / total if total > 0 else 0
            return {
                "size": len(self._cache),
                "max_size": self.max_size,
                "hits": self._hits,
                "misses": self._misses,
                "hit_rate": round(hit_rate, 3),
                "ttl_seconds": self.ttl_seconds,
            }


# Global cache instance
_llm_cache = LRUCache(
    max_size=int(os.getenv("LLM_CACHE_SIZE", "1000")),
    ttl_seconds=int(os.getenv("LLM_CACHE_TTL", "300"))
)


def get_cached_response(prompt: str, model: str = "") -> Optional[str]:
    """Get cached LLM response."""
    return _llm_cache.get(prompt, model)


def set_cached_response(prompt: str, response: str, model: str = ""):
    """Cache LLM response."""
    _llm_cache.set(prompt, response, model)


def get_cache_stats() -> Dict[str, Any]:
    """Get cache statistics."""
    return _llm_cache.stats()


def clear_cache():
    """Clear the LLM cache."""
    _llm_cache.clear()


# Optional Redis fallback for distributed caching
class RedisCache:
    """Redis-based cache for distributed deployments."""
    
    def __init__(self, redis_url: str = None, ttl_seconds: int = 300):
        self.ttl_seconds = ttl_seconds
        self._redis = None
        
        if redis_url:
            try:
                import redis
                self._redis = redis.from_url(redis_url)
            except ImportError:
                pass
            except Exception:
                pass
    
    def _make_key(self, prompt: str, model: str = "") -> str:
        content = f"{model}:{prompt}"
        return f"llm_cache:{hashlib.sha256(content.encode()).hexdigest()[:16]}"
    
    def get(self, prompt: str, model: str = "") -> Optional[str]:
        if not self._redis:
            return None
        try:
            key = self._make_key(prompt, model)
            value = self._redis.get(key)
            return value.decode() if value else None
        except Exception:
            return None
    
    def set(self, prompt: str, response: str, model: str = ""):
        if not self._redis:
            return
        try:
            key = self._make_key(prompt, model)
            self._redis.setex(key, self.ttl_seconds, response)
        except Exception:
            pass


# Initialize Redis cache if URL is provided
_redis_url = os.getenv("REDIS_URL")
_redis_cache = RedisCache(_redis_url) if _redis_url else None


def get_cached_response_with_redis(prompt: str, model: str = "") -> Optional[str]:
    """Get cached response, checking memory first, then Redis."""
    # Check memory cache first
    result = _llm_cache.get(prompt, model)
    if result:
        return result
    
    # Check Redis if available
    if _redis_cache:
        result = _redis_cache.get(prompt, model)
        if result:
            # Populate memory cache
            _llm_cache.set(prompt, result, model)
            return result
    
    return None


def set_cached_response_with_redis(prompt: str, response: str, model: str = ""):
    """Cache response in both memory and Redis."""
    _llm_cache.set(prompt, response, model)
    if _redis_cache:
        _redis_cache.set(prompt, response, model)
