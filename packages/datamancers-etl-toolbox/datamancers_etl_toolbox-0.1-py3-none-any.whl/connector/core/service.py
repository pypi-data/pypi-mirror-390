"""
Base Service class for all service implementations.
"""

from abc import ABC
from typing import Any, Dict, Optional

from ..services.types.rest_api.http_client import HTTPClient
from ..services.types.rest_api.exceptions import APIError, ConfigurationError


class BaseService(ABC):
    """
    Base class for all service implementations.
    
    Services define base configuration, authentication, retry, and pagination strategies
    that are inherited by all resources within the service.
    """

    def __init__(
        self,
        base_url: str,
        auth_strategy: Optional[Any] = None,
        retry_strategy: Optional[Any] = None,
        pagination_strategy: Optional[Any] = None,
        default_timeout: float = 30.0,
        default_headers: Optional[Dict[str, str]] = None,
        follow_redirects: bool = True,
        max_redirects: int = 10,
    ):
        """
        Initialize base service.

        Args:
            base_url: Base URL for the service API
            auth_strategy: Authentication strategy instance
            retry_strategy: Retry strategy instance
            pagination_strategy: Pagination strategy instance
            default_timeout: Default request timeout in seconds
            default_headers: Default headers for all requests
            follow_redirects: Whether to follow redirects
            max_redirects: Maximum number of redirects to follow
        """
        if not base_url:
            raise ConfigurationError("base_url is required")

        self.base_url = base_url.rstrip("/")
        self.auth_strategy = auth_strategy
        self.retry_strategy = retry_strategy
        self.pagination_strategy = pagination_strategy
        self.default_timeout = default_timeout
        self.default_headers = default_headers or {}
        self.follow_redirects = follow_redirects
        self.max_redirects = max_redirects

        # Initialize HTTP client
        self.http_client = HTTPClient(
            base_url=self.base_url,
            default_headers=self.default_headers,
            default_timeout=self.default_timeout,
            follow_redirects=self.follow_redirects,
            max_redirects=self.max_redirects,
        )

    def validate_config(self) -> bool:
        """
        Validate service configuration.

        Returns:
            bool: True if configuration is valid

        Raises:
            ConfigurationError: If configuration is invalid
        """
        if not self.base_url:
            raise ConfigurationError("base_url is required")

        # Validate authentication strategy if provided
        if self.auth_strategy:
            if not hasattr(self.auth_strategy, "get_auth_headers"):
                raise ConfigurationError(
                    "auth_strategy must implement get_auth_headers() method"
                )

        # Validate retry strategy if provided
        if self.retry_strategy:
            if not hasattr(self.retry_strategy, "execute_with_retry"):
                raise ConfigurationError(
                    "retry_strategy must implement execute_with_retry() method"
                )

        # Validate pagination strategy if provided
        if self.pagination_strategy:
            if not hasattr(self.pagination_strategy, "decorate_request"):
                raise ConfigurationError(
                    "pagination_strategy must implement decorate_request() method"
                )

        return True

    def test_connection(self) -> bool:
        """
        Test connection to the service.

        Returns:
            bool: True if connection is successful

        Raises:
            APIError: If connection test fails
        """
        try:
            # Make a simple GET request to test connection
            response = self.http_client.get("/", timeout=5.0)
            return response.is_success
        except Exception as e:
            raise APIError(f"Connection test failed: {e}")

    def get_auth_headers(self) -> Dict[str, str]:
        """
        Get authentication headers from auth strategy.

        Returns:
            Dict[str, str]: Authentication headers
        """
        if self.auth_strategy and hasattr(self.auth_strategy, "get_auth_headers"):
            return self.auth_strategy.get_auth_headers()
        return {}

    def close(self):
        """Close the service and cleanup resources."""
        if hasattr(self, "http_client"):
            self.http_client.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.aclose()

    async def aclose(self):
        """Close the async service and cleanup resources."""
        if hasattr(self, "http_client"):
            await self.http_client.aclose()


