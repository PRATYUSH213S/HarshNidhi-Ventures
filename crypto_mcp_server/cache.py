"""
Caching utilities for the Crypto MCP Server
"""

import time
from typing import Any, Optional, Callable, TypeVar
from functools import wraps
from cachetools import TTLCache
from .config import config
from .logger import logger
from .exceptions import CacheError

T = TypeVar("T")


class CacheManager:
    """Manages caching for API responses"""

    def __init__(self, maxsize: int = 1000, ttl: int = 60):
        """
        Initialize cache manager.

        Args:
            maxsize: Maximum number of items in cache
            ttl: Time-to-live in seconds
        """
        self._cache = TTLCache(maxsize=maxsize, ttl=ttl)
        self._stats = {"hits": 0, "misses": 0, "errors": 0}
        logger.info(f"Cache initialized with maxsize={maxsize}, ttl={ttl}s")

    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found
        """
        try:
            value = self._cache.get(key)
            if value is not None:
                self._stats["hits"] += 1
                logger.debug(f"Cache hit: {key}")
            else:
                self._stats["misses"] += 1
                logger.debug(f"Cache miss: {key}")
            return value
        except Exception as e:
            self._stats["errors"] += 1
            logger.error(f"Cache get error for key {key}: {e}")
            raise CacheError(f"Failed to get cache key {key}: {e}")

    def set(self, key: str, value: Any) -> None:
        """
        Set value in cache.

        Args:
            key: Cache key
            value: Value to cache
        """
        try:
            self._cache[key] = value
            logger.debug(f"Cache set: {key}")
        except Exception as e:
            self._stats["errors"] += 1
            logger.error(f"Cache set error for key {key}: {e}")
            raise CacheError(f"Failed to set cache key {key}: {e}")

    def delete(self, key: str) -> None:
        """
        Delete value from cache.

        Args:
            key: Cache key
        """
        try:
            if key in self._cache:
                del self._cache[key]
                logger.debug(f"Cache delete: {key}")
        except Exception as e:
            self._stats["errors"] += 1
            logger.error(f"Cache delete error for key {key}: {e}")
            raise CacheError(f"Failed to delete cache key {key}: {e}")

    def clear(self) -> None:
        """Clear all cache entries"""
        try:
            self._cache.clear()
            logger.info("Cache cleared")
        except Exception as e:
            self._stats["errors"] += 1
            logger.error(f"Cache clear error: {e}")
            raise CacheError(f"Failed to clear cache: {e}")

    def get_stats(self) -> dict:
        """
        Get cache statistics.

        Returns:
            Dictionary with cache statistics
        """
        total_requests = self._stats["hits"] + self._stats["misses"]
        hit_rate = (
            (self._stats["hits"] / total_requests * 100) if total_requests > 0 else 0
        )

        return {
            "hits": self._stats["hits"],
            "misses": self._stats["misses"],
            "errors": self._stats["errors"],
            "total_requests": total_requests,
            "hit_rate_percent": round(hit_rate, 2),
            "current_size": len(self._cache),
            "max_size": self._cache.maxsize,
        }

    def build_key(self, *args: Any, **kwargs: Any) -> str:
        """
        Build a cache key from arguments.

        Args:
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Cache key string
        """
        parts = [str(arg) for arg in args]
        parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
        return ":".join(parts)


# Global cache instance
cache_manager = CacheManager(maxsize=config.MAX_CACHE_SIZE, ttl=config.CACHE_TTL)


def cached(ttl: Optional[int] = None, key_prefix: str = "") -> Callable:
    """
    Decorator to cache function results.

    Args:
        ttl: Time-to-live in seconds (uses global config if None)
        key_prefix: Prefix for cache key

    Returns:
        Decorated function
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> T:
            # Build cache key
            cache_key = f"{key_prefix}:{func.__name__}:{cache_manager.build_key(*args, **kwargs)}"

            # Try to get from cache
            cached_value = cache_manager.get(cache_key)
            if cached_value is not None:
                return cached_value

            # Execute function
            result = await func(*args, **kwargs)

            # Store in cache
            cache_manager.set(cache_key, result)

            return result

        @wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> T:
            # Build cache key
            cache_key = f"{key_prefix}:{func.__name__}:{cache_manager.build_key(*args, **kwargs)}"

            # Try to get from cache
            cached_value = cache_manager.get(cache_key)
            if cached_value is not None:
                return cached_value

            # Execute function
            result = func(*args, **kwargs)

            # Store in cache
            cache_manager.set(cache_key, result)

            return result

        # Return appropriate wrapper based on function type
        import asyncio

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator
