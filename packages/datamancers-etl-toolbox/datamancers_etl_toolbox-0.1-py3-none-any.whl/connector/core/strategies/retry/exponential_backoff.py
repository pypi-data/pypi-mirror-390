"""
Exponential backoff retry strategy.
"""

import time
from typing import Any, Callable, Optional

from .base_retry import BaseRetryStrategy


class ExponentialBackoff(BaseRetryStrategy):
    """
    Exponential backoff retry strategy.
    
    Retries with exponentially increasing delays between attempts.
    """

    def __init__(
        self,
        max_attempts: int = 3,
        base_delay: float = 1.0,
        max_delay: Optional[float] = None,
        multiplier: float = 2.0,
    ):
        """
        Initialize exponential backoff retry strategy.

        Args:
            max_attempts: Maximum number of retry attempts
            base_delay: Base delay in seconds
            max_delay: Maximum delay in seconds (None for no limit)
            multiplier: Multiplier for exponential backoff
        """
        if max_attempts < 1:
            raise ValueError("max_attempts must be at least 1")
        if base_delay < 0:
            raise ValueError("base_delay must be non-negative")

        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.multiplier = multiplier

    def execute_with_retry(self, operation: Callable[[], Any]) -> Any:
        """
        Execute operation with exponential backoff retry logic.

        Args:
            operation: Callable operation to execute

        Returns:
            Any: Operation result

        Raises:
            Exception: If operation fails after all retries
        """
        last_exception = None

        for attempt in range(self.max_attempts):
            try:
                return operation()
            except Exception as e:
                last_exception = e

                # Check if we should retry
                if not self.should_retry(e, attempt):
                    raise

                # Don't wait after the last attempt
                if attempt < self.max_attempts - 1:
                    delay = self.get_backoff_delay(attempt)
                    time.sleep(delay)

        # All retries exhausted
        raise last_exception

    def should_retry(self, error: Exception, attempt: int) -> bool:
        """
        Determine if operation should be retried.

        Args:
            error: Exception that occurred
            attempt: Current attempt number (0-indexed)

        Returns:
            bool: True if operation should be retried
        """
        # Don't retry on the last attempt
        if attempt >= self.max_attempts - 1:
            return False

        # Retry on network errors, timeouts, and server errors (5xx)
        error_str = str(error).lower()
        if any(
            keyword in error_str
            for keyword in ["timeout", "connection", "network", "500", "502", "503", "504"]
        ):
            return True

        # Check if error has status_code attribute (HTTP errors)
        if hasattr(error, "status_code"):
            status_code = getattr(error, "status_code", None)
            if status_code and 500 <= status_code < 600:
                return True

        return False

    def get_backoff_delay(self, attempt: int) -> float:
        """
        Get exponential backoff delay for retry attempt.

        Args:
            attempt: Current attempt number (0-indexed)

        Returns:
            float: Delay in seconds
        """
        delay = self.base_delay * (self.multiplier ** attempt)
        if self.max_delay:
            delay = min(delay, self.max_delay)
        return delay


