"""
OpenAPI adapter module.

Provides OpenAPI schema translation and client implementation.
"""

from .openapi_client import OpenAPIClient
from .translator import OpenAPITranslator

__all__ = ["OpenAPIClient", "OpenAPITranslator"]

