"""
Main API client that integrates all components.
"""

import asyncio
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from .config import APIConfig, load_config
from .exceptions import APIError, ValidationError, SchemaError
from .http_client import HTTPClient
from .models import RequestConfig, ResponseConfig, HTTPMethod
from .schema import OpenAPISchema


class APIClient:
    """
    Main API client that integrates OpenAPI schema validation with HTTP requests.
    """

    def __init__(self, config: Union[APIConfig, str, Path, Dict[str, Any]]):
        """
        Initialize API client.

        Args:
            config: API configuration (APIConfig, file path, or dict)
        """
        if isinstance(config, APIConfig):
            self.config = config
        else:
            self.config = load_config(config)

        # Initialize HTTP client
        self.http_client = HTTPClient(
            base_url=self.config.base_url,
            default_headers=self.config.default_headers,
            default_timeout=self.config.default_timeout,
            default_retries=self.config.default_retries,
            default_retry_delay=self.config.default_retry_delay,
            follow_redirects=self.config.follow_redirects,
            max_redirects=self.config.max_redirects,
        )

        # Initialize OpenAPI schema
        self.schema: Optional[OpenAPISchema] = None
        if self.config.openapi_schema:
            self.schema = OpenAPISchema(self.config.openapi_schema)
        elif self.config.schema_path:
            self.schema = OpenAPISchema.from_file(self.config.schema_path)

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()

    def close(self):
        """Close the API client."""
        self.http_client.close()

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.aclose()

    async def aclose(self):
        """Close the async API client."""
        await self.http_client.aclose()

    def call_operation(
        self,
        operation_id: str,
        path_params: Optional[Dict[str, Any]] = None,
        query_params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        body: Optional[Union[Dict[str, Any], str, bytes]] = None,
        files: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None,
        retries: Optional[int] = None,
        validate_request: Optional[bool] = None,
        validate_response: Optional[bool] = None,
    ) -> ResponseConfig:
        """
        Call an API operation by ID.

        Args:
            operation_id: OpenAPI operation ID
            path_params: Path parameters
            query_params: Query parameters
            headers: Request headers
            body: Request body
            files: File uploads
            timeout: Request timeout
            retries: Number of retries
            validate_request: Whether to validate request
            validate_response: Whether to validate response

        Returns:
            ResponseConfig: Response configuration object
        """
        if not self.schema:
            raise SchemaError("No OpenAPI schema loaded")

        # Get operation configuration
        operation = self.schema.get_operation(operation_id)
        if not operation:
            raise APIError(f"Operation '{operation_id}' not found in schema")

        # Prepare request data
        request_data = {}
        if path_params:
            request_data.update(path_params)
        if query_params:
            request_data.update(query_params)
        if body is not None:
            request_data["body"] = body

        # Validate request if enabled
        validate_request = (
            validate_request
            if validate_request is not None
            else self.config.validate_requests
        )
        if validate_request:
            is_valid, errors = self.schema.validate_request(operation_id, request_data)
            if not is_valid:
                raise ValidationError(f"Request validation failed: {', '.join(errors)}")

        # Build URL
        url = self.schema.build_url(
            operation_id=operation_id,
            base_url=self.config.base_url,
            path_params=path_params,
            query_params=query_params,
        )

        # Prepare headers
        request_headers = self.config.default_headers.copy()
        if headers:
            request_headers.update(headers)

        # Add security headers
        self._add_security_headers(request_headers)

        # Make request
        response = self.http_client.request(
            method=operation.method,
            url=url,
            headers=request_headers,
            params=query_params,
            data=body if not isinstance(body, dict) else None,
            json=body if isinstance(body, dict) else None,
            files=files,
            timeout=timeout or self.config.default_timeout,
            retries=retries or self.config.default_retries,
        )

        # Validate response if enabled
        validate_response = (
            validate_response
            if validate_response is not None
            else self.config.validate_responses
        )
        if validate_response and response.is_success:
            is_valid, errors = self.schema.validate_response(
                operation_id=operation_id,
                status_code=response.status_code,
                data=response.data,
            )
            if not is_valid:
                raise ValidationError(
                    f"Response validation failed: {', '.join(errors)}"
                )

        return response

    async def acall_operation(
        self,
        operation_id: str,
        path_params: Optional[Dict[str, Any]] = None,
        query_params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        body: Optional[Union[Dict[str, Any], str, bytes]] = None,
        files: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None,
        retries: Optional[int] = None,
        validate_request: Optional[bool] = None,
        validate_response: Optional[bool] = None,
    ) -> ResponseConfig:
        """
        Call an API operation by ID (async version).

        Args:
            operation_id: OpenAPI operation ID
            path_params: Path parameters
            query_params: Query parameters
            headers: Request headers
            body: Request body
            files: File uploads
            timeout: Request timeout
            retries: Number of retries
            validate_request: Whether to validate request
            validate_response: Whether to validate response

        Returns:
            ResponseConfig: Response configuration object
        """
        if not self.schema:
            raise SchemaError("No OpenAPI schema loaded")

        # Get operation configuration
        operation = self.schema.get_operation(operation_id)
        if not operation:
            raise APIError(f"Operation '{operation_id}' not found in schema")

        # Prepare request data
        request_data = {}
        if path_params:
            request_data.update(path_params)
        if query_params:
            request_data.update(query_params)
        if body is not None:
            request_data["body"] = body

        # Validate request if enabled
        validate_request = (
            validate_request
            if validate_request is not None
            else self.config.validate_requests
        )
        if validate_request:
            is_valid, errors = self.schema.validate_request(operation_id, request_data)
            if not is_valid:
                raise ValidationError(f"Request validation failed: {', '.join(errors)}")

        # Build URL
        url = self.schema.build_url(
            operation_id=operation_id,
            base_url=self.config.base_url,
            path_params=path_params,
            query_params=query_params,
        )

        # Prepare headers
        request_headers = self.config.default_headers.copy()
        if headers:
            request_headers.update(headers)

        # Add security headers
        self._add_security_headers(request_headers)

        # Make request
        response = await self.http_client.arequest(
            method=operation.method,
            url=url,
            headers=request_headers,
            params=query_params,
            data=body if not isinstance(body, dict) else None,
            json=body if isinstance(body, dict) else None,
            files=files,
            timeout=timeout or self.config.default_timeout,
            retries=retries or self.config.default_retries,
        )

        # Validate response if enabled
        validate_response = (
            validate_response
            if validate_response is not None
            else self.config.validate_responses
        )
        if validate_response and response.is_success:
            is_valid, errors = self.schema.validate_response(
                operation_id=operation_id,
                status_code=response.status_code,
                data=response.data,
            )
            if not is_valid:
                raise ValidationError(
                    f"Response validation failed: {', '.join(errors)}"
                )

        return response

    def _add_security_headers(self, headers: Dict[str, str]) -> None:
        """Add security headers based on configuration."""
        for security in self.config.security:
            if (
                security.type == "apiKey"
                and security.in_ == "header"
                and security.value
            ):
                headers[security.name] = security.value
            elif (
                security.type == "http"
                and security.scheme == "bearer"
                and security.value
            ):
                headers["Authorization"] = f"Bearer {security.value}"

    def list_operations(self) -> List[str]:
        """List all available operations."""
        if not self.schema:
            return []
        return self.schema.list_operations()

    def get_operation_info(self, operation_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific operation."""
        if not self.schema:
            return None
        return self.schema.get_operation_info(operation_id)

    def get_operations_by_tag(self, tag: str) -> List[Dict[str, Any]]:
        """Get all operations with a specific tag."""
        if not self.schema:
            return []

        operations = self.schema.get_operations_by_tag(tag)
        return [self.schema.get_operation_info(op.operation_id) for op in operations]

    # Convenience methods for common operations
    def get(
        self,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs,
    ) -> ResponseConfig:
        """Make GET request to a specific path."""
        return self.http_client.get(path, params=params, headers=headers, **kwargs)

    def post(
        self,
        path: str,
        data: Optional[Union[Dict[str, Any], str, bytes]] = None,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs,
    ) -> ResponseConfig:
        """Make POST request to a specific path."""
        return self.http_client.post(
            path, data=data, json=json, headers=headers, **kwargs
        )

    def put(
        self,
        path: str,
        data: Optional[Union[Dict[str, Any], str, bytes]] = None,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs,
    ) -> ResponseConfig:
        """Make PUT request to a specific path."""
        return self.http_client.put(
            path, data=data, json=json, headers=headers, **kwargs
        )

    def delete(
        self, path: str, headers: Optional[Dict[str, str]] = None, **kwargs
    ) -> ResponseConfig:
        """Make DELETE request to a specific path."""
        return self.http_client.delete(path, headers=headers, **kwargs)

    def patch(
        self,
        path: str,
        data: Optional[Union[Dict[str, Any], str, bytes]] = None,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs,
    ) -> ResponseConfig:
        """Make PATCH request to a specific path."""
        return self.http_client.patch(
            path, data=data, json=json, headers=headers, **kwargs
        )

    # Async convenience methods
    async def aget(
        self,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs,
    ) -> ResponseConfig:
        """Make async GET request to a specific path."""
        return await self.http_client.aget(
            path, params=params, headers=headers, **kwargs
        )

    async def apost(
        self,
        path: str,
        data: Optional[Union[Dict[str, Any], str, bytes]] = None,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs,
    ) -> ResponseConfig:
        """Make async POST request to a specific path."""
        return await self.http_client.apost(
            path, data=data, json=json, headers=headers, **kwargs
        )

    async def aput(
        self,
        path: str,
        data: Optional[Union[Dict[str, Any], str, bytes]] = None,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs,
    ) -> ResponseConfig:
        """Make async PUT request to a specific path."""
        return await self.http_client.aput(
            path, data=data, json=json, headers=headers, **kwargs
        )

    async def adelete(
        self, path: str, headers: Optional[Dict[str, str]] = None, **kwargs
    ) -> ResponseConfig:
        """Make async DELETE request to a specific path."""
        return await self.http_client.adelete(path, headers=headers, **kwargs)

    async def apatch(
        self,
        path: str,
        data: Optional[Union[Dict[str, Any], str, bytes]] = None,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs,
    ) -> ResponseConfig:
        """Make async PATCH request to a specific path."""
        return await self.http_client.apatch(
            path, data=data, json=json, headers=headers, **kwargs
        )



