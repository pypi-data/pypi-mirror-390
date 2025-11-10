"""
Base retry strategy interface.
"""

from abc import ABC, abstractmethod
from typing import Any, Callable, Optional


class BaseRetryStrategy(ABC):
    """
    Base class for retry strategies.
    
    Retry strategies wrap operations with retry logic and backoff delays.
    """

    @abstractmethod
    def execute_with_retry(self, operation: Callable[[], Any]) -> Any:
        """
        Execute operation with retry logic.

        Args:
            operation: Callable operation to execute

        Returns:
            Any: Operation result

        Raises:
            Exception: If operation fails after all retries
        """
        pass

    def should_retry(self, error: Exception, attempt: int) -> bool:
        """
        Determine if operation should be retried.

        Args:
            error: Exception that occurred
            attempt: Current attempt number (0-indexed)

        Returns:
            bool: True if operation should be retried
        """
        return True

    def get_backoff_delay(self, attempt: int) -> float:
        """
        Get backoff delay for retry attempt.

        Args:
            attempt: Current attempt number (0-indexed)

        Returns:
            float: Delay in seconds
        """
        return 0.0


