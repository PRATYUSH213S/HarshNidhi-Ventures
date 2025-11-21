"""
Tests for cache module
"""

import pytest
import time
from crypto_mcp_server.cache import CacheManager, cache_manager
from crypto_mcp_server.exceptions import CacheError


class TestCacheManager:
    """Tests for CacheManager class"""

    def setup_method(self):
        """Set up test cache manager"""
        self.cache = CacheManager(maxsize=10, ttl=1)

    def test_cache_initialization(self):
        """Test cache manager initialization"""
        assert self.cache is not None
        assert self.cache._cache.maxsize == 10

    def test_set_and_get(self):
        """Test setting and getting cache values"""
        self.cache.set("key1", "value1")
        result = self.cache.get("key1")
        assert result == "value1"

    def test_cache_miss(self):
        """Test cache miss returns None"""
        result = self.cache.get("nonexistent_key")
        assert result is None

    def test_cache_hit_increments_stats(self):
        """Test cache hit increments statistics"""
        self.cache.set("key1", "value1")
        self.cache.get("key1")
        stats = self.cache.get_stats()
        assert stats["hits"] == 1
        assert stats["misses"] == 0

    def test_cache_miss_increments_stats(self):
        """Test cache miss increments statistics"""
        self.cache.get("nonexistent")
        stats = self.cache.get_stats()
        assert stats["hits"] == 0
        assert stats["misses"] == 1

    def test_cache_delete(self):
        """Test deleting cache entries"""
        self.cache.set("key1", "value1")
        self.cache.delete("key1")
        result = self.cache.get("key1")
        assert result is None

    def test_cache_clear(self):
        """Test clearing all cache entries"""
        self.cache.set("key1", "value1")
        self.cache.set("key2", "value2")
        self.cache.clear()
        assert self.cache.get("key1") is None
        assert self.cache.get("key2") is None

    def test_cache_ttl_expiration(self):
        """Test cache entries expire after TTL"""
        self.cache.set("key1", "value1")
        time.sleep(1.5)  # Wait for TTL to expire
        result = self.cache.get("key1")
        assert result is None

    def test_cache_max_size(self):
        """Test cache respects max size"""
        cache = CacheManager(maxsize=3, ttl=60)
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.set("key3", "value3")
        cache.set("key4", "value4")  # Should evict oldest

        stats = cache.get_stats()
        assert stats["current_size"] <= 3

    def test_build_key(self):
        """Test building cache keys from arguments"""
        key = self.cache.build_key("arg1", "arg2", kwarg1="value1", kwarg2="value2")
        assert "arg1" in key
        assert "arg2" in key
        assert "kwarg1=value1" in key

    def test_get_stats(self):
        """Test getting cache statistics"""
        self.cache.set("key1", "value1")
        self.cache.get("key1")  # Hit
        self.cache.get("key2")  # Miss

        stats = self.cache.get_stats()
        assert stats["hits"] == 1
        assert stats["misses"] == 1
        assert stats["total_requests"] == 2
        assert stats["hit_rate_percent"] == 50.0
        assert stats["current_size"] == 1

    def test_cache_different_types(self):
        """Test caching different data types"""
        # String
        self.cache.set("str_key", "string_value")
        assert self.cache.get("str_key") == "string_value"

        # Integer
        self.cache.set("int_key", 42)
        assert self.cache.get("int_key") == 42

        # Dictionary
        self.cache.set("dict_key", {"nested": "data"})
        assert self.cache.get("dict_key") == {"nested": "data"}

        # List
        self.cache.set("list_key", [1, 2, 3])
        assert self.cache.get("list_key") == [1, 2, 3]


class TestGlobalCacheManager:
    """Tests for global cache manager instance"""

    def test_global_cache_exists(self):
        """Test global cache manager is initialized"""
        assert cache_manager is not None

    def test_global_cache_operations(self):
        """Test operations on global cache manager"""
        cache_manager.clear()  # Clean start
        cache_manager.set("test_key", "test_value")
        result = cache_manager.get("test_key")
        assert result == "test_value"
        cache_manager.clear()  # Clean up
