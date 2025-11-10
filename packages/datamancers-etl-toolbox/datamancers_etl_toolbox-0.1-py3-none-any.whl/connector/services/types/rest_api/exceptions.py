"""
Custom exceptions for the API client library.
"""

from typing import Any, Dict, Optional


class APIError(Exception):
    """Base exception for API-related errors."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response_data: Optional[Dict[str, Any]] = None,
        operation_id: Optional[str] = None,
    ):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.response_data = response_data
        self.operation_id = operation_id


class ValidationError(APIError):
    """Raised when request/response validation fails."""

    def __init__(
        self, message: str, validation_errors: Optional[Dict[str, Any]] = None, **kwargs
    ):
        super().__init__(message, **kwargs)
        self.validation_errors = validation_errors or {}


class ConfigurationError(APIError):
    """Raised when configuration is invalid or missing."""

    pass


class SchemaError(APIError):
    """Raised when OpenAPI schema processing fails."""

    pass


class HTTPError(APIError):
    """Raised when HTTP request fails."""

    pass



