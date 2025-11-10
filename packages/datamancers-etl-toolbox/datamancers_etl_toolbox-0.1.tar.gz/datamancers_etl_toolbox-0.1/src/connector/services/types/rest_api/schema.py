"""
OpenAPI schema parser and validator.
"""

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Tuple
from urllib.parse import urljoin, urlparse

from .exceptions import SchemaError, ValidationError
from .models import OperationConfig, HTTPMethod


class OpenAPISchema:
    """OpenAPI schema parser and validator."""

    def __init__(self, schema: Dict[str, Any]):
        """
        Initialize with OpenAPI schema.

        Args:
            schema: OpenAPI 3.0 schema dictionary
        """
        self.schema = schema
        self._validate_schema()
        self._operations: Dict[str, OperationConfig] = {}
        self._parse_operations()

    def _validate_schema(self) -> None:
        """Validate that the schema is a valid OpenAPI 3.0 document."""
        if not isinstance(self.schema, dict):
            raise SchemaError("Schema must be a dictionary")

        if "openapi" not in self.schema:
            raise SchemaError("Missing 'openapi' field")

        version = self.schema["openapi"]
        if not version.startswith("3.0"):
            raise SchemaError(f"Unsupported OpenAPI version: {version}")

        if "paths" not in self.schema:
            raise SchemaError("Missing 'paths' field")

        if "info" not in self.schema:
            raise SchemaError("Missing 'info' field")

    def _parse_operations(self) -> None:
        """Parse all operations from the schema."""
        paths = self.schema.get("paths", {})

        for path, path_item in paths.items():
            if not isinstance(path_item, dict):
                continue

            # Parse each HTTP method for this path
            for method_name, operation in path_item.items():
                if method_name.startswith("x-") or not isinstance(operation, dict):
                    continue

                try:
                    method = HTTPMethod(method_name.upper())
                except ValueError:
                    continue

                operation_id = operation.get(
                    "operationId", f"{method.value}_{path.replace('/', '_').strip('_')}"
                )

                config = OperationConfig(
                    operation_id=operation_id,
                    method=method,
                    path=path,
                    summary=operation.get("summary"),
                    description=operation.get("description"),
                    tags=operation.get("tags", []),
                    parameters=operation.get("parameters", []),
                    request_body=operation.get("requestBody"),
                    responses=operation.get("responses", {}),
                    security=operation.get("security", []),
                )

                self._operations[operation_id] = config

    @classmethod
    def from_file(cls, file_path: Union[str, Path]) -> "OpenAPISchema":
        """
        Load schema from file.

        Args:
            file_path: Path to OpenAPI schema file

        Returns:
            OpenAPISchema: Parsed schema object
        """
        path = Path(file_path)

        if not path.exists():
            raise SchemaError(f"Schema file not found: {path}")

        try:
            with open(path, "r", encoding="utf-8") as f:
                if path.suffix.lower() == ".json":
                    schema = json.load(f)
                else:
                    import yaml

                    schema = yaml.safe_load(f)

            return cls(schema)
        except Exception as e:
            raise SchemaError(f"Failed to load schema from {path}: {e}")

    def get_operation(self, operation_id: str) -> Optional[OperationConfig]:
        """Get operation configuration by ID."""
        return self._operations.get(operation_id)

    def list_operations(self) -> List[str]:
        """List all available operation IDs."""
        return list(self._operations.keys())

    def get_operations_by_tag(self, tag: str) -> List[OperationConfig]:
        """Get all operations with a specific tag."""
        return [op for op in self._operations.values() if tag in op.tags]

    def validate_request(
        self, operation_id: str, data: Dict[str, Any], strict: bool = False
    ) -> Tuple[bool, List[str]]:
        """
        Validate request data against operation schema.

        Args:
            operation_id: Operation ID to validate against
            data: Request data to validate
            strict: Whether to use strict validation

        Returns:
            Tuple of (is_valid, error_messages)
        """
        operation = self.get_operation(operation_id)
        if not operation:
            return False, [f"Operation '{operation_id}' not found"]

        errors = []

        # Validate parameters
        param_errors = self._validate_parameters(operation, data)
        errors.extend(param_errors)

        # Validate request body
        if operation.request_body and "body" in data:
            body_errors = self._validate_request_body(operation, data["body"])
            errors.extend(body_errors)

        return len(errors) == 0, errors

    def validate_response(
        self, operation_id: str, status_code: int, data: Any, strict: bool = False
    ) -> Tuple[bool, List[str]]:
        """
        Validate response data against operation schema.

        Args:
            operation_id: Operation ID to validate against
            status_code: HTTP status code
            data: Response data to validate
            strict: Whether to use strict validation

        Returns:
            Tuple of (is_valid, error_messages)
        """
        operation = self.get_operation(operation_id)
        if not operation:
            return False, [f"Operation '{operation_id}' not found"]

        # Find response schema for status code
        response_schema = self._get_response_schema(operation, status_code)
        if not response_schema:
            return True, []  # No schema to validate against

        errors = self._validate_schema_data(response_schema, data, strict)
        return len(errors) == 0, errors

    def _validate_parameters(
        self, operation: OperationConfig, data: Dict[str, Any]
    ) -> List[str]:
        """Validate operation parameters."""
        errors = []

        for param in operation.parameters:
            param_name = param.get("name")
            param_in = param.get("in")
            required = param.get("required", False)

            if param_in == "path":
                if required and param_name not in data:
                    errors.append(f"Required path parameter '{param_name}' is missing")
            elif param_in == "query":
                if required and param_name not in data:
                    errors.append(f"Required query parameter '{param_name}' is missing")
            elif param_in == "header":
                if required and param_name not in data:
                    errors.append(f"Required header '{param_name}' is missing")

        return errors

    def _validate_request_body(
        self, operation: OperationConfig, body: Any
    ) -> List[str]:
        """Validate request body against schema."""
        if not operation.request_body:
            return []

        content = operation.request_body.get("content", {})
        if not content:
            return []

        # For now, validate against JSON schema if available
        json_content = content.get("application/json", {})
        if json_content and "schema" in json_content:
            return self._validate_schema_data(json_content["schema"], body, False)

        return []

    def _get_response_schema(
        self, operation: OperationConfig, status_code: int
    ) -> Optional[Dict[str, Any]]:
        """Get response schema for status code."""
        responses = operation.responses

        # Try exact status code first
        if str(status_code) in responses:
            response = responses[str(status_code)]
        elif "default" in responses:
            response = responses["default"]
        else:
            return None

        content = response.get("content", {})
        json_content = content.get("application/json", {})

        return json_content.get("schema")

    def _validate_schema_data(
        self, schema: Dict[str, Any], data: Any, strict: bool
    ) -> List[str]:
        """Validate data against JSON schema."""
        errors = []

        # Basic type validation
        schema_type = schema.get("type")
        if schema_type:
            if schema_type == "object" and not isinstance(data, dict):
                errors.append(f"Expected object, got {type(data).__name__}")
            elif schema_type == "array" and not isinstance(data, list):
                errors.append(f"Expected array, got {type(data).__name__}")
            elif schema_type == "string" and not isinstance(data, str):
                errors.append(f"Expected string, got {type(data).__name__}")
            elif schema_type == "integer" and not isinstance(data, int):
                errors.append(f"Expected integer, got {type(data).__name__}")
            elif schema_type == "number" and not isinstance(data, (int, float)):
                errors.append(f"Expected number, got {type(data).__name__}")
            elif schema_type == "boolean" and not isinstance(data, bool):
                errors.append(f"Expected boolean, got {type(data).__name__}")

        # Required fields validation
        required_fields = schema.get("required", [])
        if isinstance(data, dict):
            for field in required_fields:
                if field not in data:
                    errors.append(f"Required field '{field}' is missing")

        # Enum validation
        enum_values = schema.get("enum")
        if enum_values is not None and data not in enum_values:
            errors.append(f"Value must be one of {enum_values}")

        return errors

    def build_url(
        self,
        operation_id: str,
        base_url: str,
        path_params: Optional[Dict[str, Any]] = None,
        query_params: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Build full URL for operation.

        Args:
            operation_id: Operation ID
            base_url: Base URL
            path_params: Path parameters
            query_params: Query parameters

        Returns:
            str: Built URL
        """
        operation = self.get_operation(operation_id)
        if not operation:
            raise SchemaError(f"Operation '{operation_id}' not found")

        # Replace path parameters
        path = operation.path
        if path_params:
            for param_name, param_value in path_params.items():
                path = path.replace(f"{{{param_name}}}", str(param_value))

        # Build full URL
        url = urljoin(base_url, path)

        # Add query parameters
        if query_params:
            query_string = "&".join([f"{k}={v}" for k, v in query_params.items()])
            url = f"{url}?{query_string}"

        return url

    def get_operation_info(self, operation_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about an operation."""
        operation = self.get_operation(operation_id)
        if not operation:
            return None

        return {
            "operation_id": operation.operation_id,
            "method": operation.method.value,
            "path": operation.path,
            "summary": operation.summary,
            "description": operation.description,
            "tags": operation.tags,
            "parameters": operation.parameters,
            "request_body": operation.request_body,
            "responses": operation.responses,
        }



