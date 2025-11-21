"""
Rate limiting utilities for API calls
"""

import time
from collections import deque
from typing import Dict
from .config import config
from .logger import logger
from .exceptions import RateLimitError


class RateLimiter:
    """Rate limiter using sliding window algorithm"""

    def __init__(self, max_requests: int = 10, time_window: int = 60):
        """
        Initialize rate limiter.

        Args:
            max_requests: Maximum number of requests allowed
            time_window: Time window in seconds
        """
        self.max_requests = max_requests
        self.time_window = time_window
        self._requests: Dict[str, deque] = {}
        logger.info(
            f"Rate limiter initialized: {max_requests} requests per {time_window}s"
        )

    def _clean_old_requests(self, key: str, current_time: float) -> None:
        """Remove requests outside the time window"""
        if key in self._requests:
            while (
                self._requests[key]
                and self._requests[key][0] < current_time - self.time_window
            ):
                self._requests[key].popleft()

    def check_limit(self, key: str) -> bool:
        """
        Check if request is within rate limit.

        Args:
            key: Identifier for the rate limit (e.g., exchange name)

        Returns:
            True if within limit, False otherwise
        """
        current_time = time.time()

        # Initialize if key doesn't exist
        if key not in self._requests:
            self._requests[key] = deque()

        # Clean old requests
        self._clean_old_requests(key, current_time)

        # Check if limit reached
        return len(self._requests[key]) < self.max_requests

    def record_request(self, key: str) -> None:
        """
        Record a new request.

        Args:
            key: Identifier for the rate limit

        Raises:
            RateLimitError: If rate limit exceeded
        """
        if not self.check_limit(key):
            logger.warning(f"Rate limit exceeded for {key}")
            raise RateLimitError(
                f"Rate limit exceeded for {key}. "
                f"Maximum {self.max_requests} requests per {self.time_window}s"
            )

        current_time = time.time()
        if key not in self._requests:
            self._requests[key] = deque()

        self._requests[key].append(current_time)
        logger.debug(
            f"Request recorded for {key}. "
            f"Current count: {len(self._requests[key])}/{self.max_requests}"
        )

    def get_remaining_requests(self, key: str) -> int:
        """
        Get number of remaining requests for a key.

        Args:
            key: Identifier for the rate limit

        Returns:
            Number of remaining requests
        """
        current_time = time.time()
        if key not in self._requests:
            return self.max_requests

        self._clean_old_requests(key, current_time)
        return max(0, self.max_requests - len(self._requests[key]))

    def reset(self, key: str) -> None:
        """Reset rate limit for a key"""
        if key in self._requests:
            self._requests[key].clear()
            logger.info(f"Rate limit reset for {key}")

    def reset_all(self) -> None:
        """Reset all rate limits"""
        self._requests.clear()
        logger.info("All rate limits reset")


# Global rate limiter instance
rate_limiter = RateLimiter(
    max_requests=config.RATE_LIMIT_REQUESTS, time_window=config.RATE_LIMIT_PERIOD
)
