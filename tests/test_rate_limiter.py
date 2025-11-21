"""
Tests for rate limiter module
"""

import pytest
import time
from crypto_mcp_server.rate_limiter import RateLimiter, rate_limiter
from crypto_mcp_server.exceptions import RateLimitError


class TestRateLimiter:
    """Tests for RateLimiter class"""

    def setup_method(self):
        """Set up test rate limiter"""
        self.limiter = RateLimiter(max_requests=3, time_window=1)

    def test_rate_limiter_initialization(self):
        """Test rate limiter initialization"""
        assert self.limiter is not None
        assert self.limiter.max_requests == 3
        assert self.limiter.time_window == 1

    def test_check_limit_within_bounds(self):
        """Test check_limit returns True when within bounds"""
        assert self.limiter.check_limit("test_key") is True

    def test_record_request(self):
        """Test recording requests"""
        self.limiter.record_request("test_key")
        remaining = self.limiter.get_remaining_requests("test_key")
        assert remaining == 2

    def test_rate_limit_exceeded(self):
        """Test rate limit exceeded raises error"""
        self.limiter.record_request("test_key")
        self.limiter.record_request("test_key")
        self.limiter.record_request("test_key")

        with pytest.raises(RateLimitError) as exc_info:
            self.limiter.record_request("test_key")
        assert "Rate limit exceeded" in str(exc_info.value)

    def test_get_remaining_requests(self):
        """Test getting remaining requests"""
        assert self.limiter.get_remaining_requests("test_key") == 3

        self.limiter.record_request("test_key")
        assert self.limiter.get_remaining_requests("test_key") == 2

        self.limiter.record_request("test_key")
        assert self.limiter.get_remaining_requests("test_key") == 1

    def test_rate_limit_reset_after_window(self):
        """Test rate limit resets after time window"""
        self.limiter.record_request("test_key")
        self.limiter.record_request("test_key")
        self.limiter.record_request("test_key")

        # Wait for time window to pass
        time.sleep(1.5)

        # Should be able to record again
        self.limiter.record_request("test_key")
        remaining = self.limiter.get_remaining_requests("test_key")
        assert remaining == 2

    def test_different_keys_independent(self):
        """Test different keys have independent rate limits"""
        self.limiter.record_request("key1")
        self.limiter.record_request("key1")
        self.limiter.record_request("key1")

        # key2 should still have full quota
        assert self.limiter.get_remaining_requests("key2") == 3

    def test_reset_specific_key(self):
        """Test resetting rate limit for specific key"""
        self.limiter.record_request("test_key")
        self.limiter.record_request("test_key")

        self.limiter.reset("test_key")

        assert self.limiter.get_remaining_requests("test_key") == 3

    def test_reset_all(self):
        """Test resetting all rate limits"""
        self.limiter.record_request("key1")
        self.limiter.record_request("key2")

        self.limiter.reset_all()

        assert self.limiter.get_remaining_requests("key1") == 3
        assert self.limiter.get_remaining_requests("key2") == 3

    def test_sliding_window_behavior(self):
        """Test sliding window algorithm behavior"""
        # Record 3 requests at start
        self.limiter.record_request("test_key")
        time.sleep(0.3)
        self.limiter.record_request("test_key")
        time.sleep(0.3)
        self.limiter.record_request("test_key")

        # Should be at limit
        with pytest.raises(RateLimitError):
            self.limiter.record_request("test_key")

        # Wait for first request to expire
        time.sleep(0.5)

        # Should be able to record one more
        self.limiter.record_request("test_key")
        remaining = self.limiter.get_remaining_requests("test_key")
        assert remaining < 3  # Some requests still in window


class TestGlobalRateLimiter:
    """Tests for global rate limiter instance"""

    def test_global_rate_limiter_exists(self):
        """Test global rate limiter is initialized"""
        assert rate_limiter is not None

    def test_global_rate_limiter_operations(self):
        """Test operations on global rate limiter"""
        rate_limiter.reset_all()  # Clean start

        rate_limiter.record_request("global_test")
        remaining = rate_limiter.get_remaining_requests("global_test")
        assert remaining < rate_limiter.max_requests

        rate_limiter.reset_all()  # Clean up
