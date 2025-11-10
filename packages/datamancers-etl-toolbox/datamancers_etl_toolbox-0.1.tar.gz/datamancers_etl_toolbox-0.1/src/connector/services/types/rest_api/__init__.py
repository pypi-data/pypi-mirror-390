"""
REST API Client Library

A comprehensive Python library for REST API communication that leverages OpenAPI schemas,
supports multiple configuration formats, and uses httpx under the hood.

Features:
- OpenAPI 3.0 schema integration
- Configuration via dict, JSON, or YAML
- Type-safe request/response handling
- Automatic validation and serialization
- Async and sync support
- Built-in retry and error handling
"""

from .client import APIClient
from .config import APIConfig, load_config
from .exceptions import APIError, ValidationError, ConfigurationError
from .models import RequestConfig, ResponseConfig

__version__ = "1.0.0"
__all__ = [
    "APIClient",
    "APIConfig",
    "load_config",
    "APIError",
    "ValidationError",
    "ConfigurationError",
    "RequestConfig",
    "ResponseConfig",
]



