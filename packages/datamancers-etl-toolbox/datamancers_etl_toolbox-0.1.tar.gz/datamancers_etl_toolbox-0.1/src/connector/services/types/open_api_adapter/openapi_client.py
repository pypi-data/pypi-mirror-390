"""
Generic OpenAPI Client
A wrapper that constructs API requests based on an OpenAPI schema.
Supports API Key, HTTP Basic, HTTP Bearer, and OAuth 2.0 Client Credentials.
Includes automatic pagination support for paginated endpoints.
"""

import base64
import json
import os
import re
import time
from collections.abc import Generator
from pathlib import Path
from typing import Any, Optional, Union

import requests
import yaml

try:
    from importlib.resources import files
except ImportError:
    # Python < 3.9 compatibility
    from importlib_resources import files


class OpenAPIClient:
    """
    Generic client that constructs API requests based on OpenAPI schema.

    Usage:
        client = OpenAPIClient(
            schema_path="path/to/openapi.json",
            auth={"api_key": "your-key"}
        )
        response = client.call("operationId", slug="account", page=1)
    """

    def __init__(
        self,
        app_name: Union[str, Path],
        auth: Optional[dict[str, Any]] = None,
        server_index: int = 0,
        base_url: Optional[str] = None,
    ):
        """
        Initialize the OpenAPI client.

        Args:
            schema_path: Path to OpenAPI schema file (JSON or YAML)
            auth: Authentication credentials dict. Supported keys:
                  - api_key: For API Key authentication
                  - username/password: For HTTP Basic authentication
                  - token: For HTTP Bearer authentication
                  - client_id/client_secret: For OAuth 2.0 Client Credentials
            server_index: Index of server to use from servers array
        """
        self.schema = self._load_schema(app_name)
        self.auth = auth or {}
        self.base_url = base_url or self._get_base_url(server_index)
        self.operations = self._parse_operations()
        self.session = requests.Session()

        # OAuth 2.0 state (initialized by _setup_auth if needed)
        self._oauth_enabled = False
        self._oauth_token_url: Optional[str] = None
        self._access_token: Optional[str] = None
        self._token_expires_at: float = 0

        self._setup_auth()

    def _load_schema(self, app_name: Union[str, Path]) -> dict[str, Any]:
        """Load OpenAPI schema from JSON or YAML file."""
        # check if app name is a path (contains json at the end) if so, use it as is if not, try to look for it in openapi_schema directory
        if isinstance(app_name, Path):
            path = app_name
        else:
            # Check if app_name is an absolute path or a relative path
            if os.path.isabs(str(app_name)):
                path = Path(app_name)
            else:
                # Try to find the schema file in the package resources
                try:
                    # First try to find it in the package resources (when installed via pip)
                    schema_file = files("etl").joinpath(
                        f"openapi_schema/{app_name}.json"
                    )
                    if schema_file.exists():
                        path = schema_file
                    else:
                        # Fallback to relative path for development
                        # Try multiple possible locations
                        possible_paths = [
                            Path(f"src/connector/services/types/open_api_adapter/schemas/{app_name}.json"),
                            Path(f"src/openapi_schema/{app_name}.json"),
                            Path(f"openapi_schema/{app_name}.json"),
                            Path(__file__).parent / "schemas" / f"{app_name}.json",
                            Path(__file__).parent.parent.parent
                            / "openapi_schema"
                            / f"{app_name}.json",
                        ]

                        path = None
                        for possible_path in possible_paths:
                            if possible_path.exists():
                                path = possible_path
                                break

                        if path is None:
                            # Last resort: try to find it relative to current working directory
                            path = Path(f"src/connector/services/types/open_api_adapter/schemas/{app_name}.json")
                except Exception:
                    # Fallback to relative path for development
                    # Try the schemas directory first
                    fallback_path = Path(f"src/connector/services/types/open_api_adapter/schemas/{app_name}.json")
                    if fallback_path.exists():
                        path = fallback_path
                    else:
                        path = Path(f"src/openapi_schema/{app_name}.json")

            if not path.exists():
                raise ValueError(f"Schema file not found: {path}")

        # Read the file content
        if hasattr(path, "read_text"):
            # This is a pathlib.Path or importlib.resources path
            content = path.read_text()
        else:
            # Fallback for regular file paths
            with open(path) as f:
                content = f.read()

        # Parse based on file extension
        if str(path).endswith(".json"):
            schema = json.loads(content)
        elif str(path).endswith((".yaml", ".yml")):
            schema = yaml.safe_load(content)
        else:
            raise ValueError(f"Unsupported schema format: {path.suffix}")

        # Resolve all $ref references
        return self._resolve_refs(schema, schema)

    def _resolve_refs(
        self, obj: Any, root_schema: dict[str, Any], seen: Optional[set] = None
    ) -> Any:
        """
        Recursively resolve all $ref references in the schema.

        Args:
            obj: Current object to process (dict, list, or primitive)
            root_schema: Root schema for resolving references
            seen: Set of already processed references (circular reference detection)

        Returns:
            Object with all $ref references resolved
        """
        if seen is None:
            seen = set()

        # Handle dictionaries
        if isinstance(obj, dict):
            # Check if this is a $ref
            if "$ref" in obj:
                ref_path = obj["$ref"]

                # Avoid circular references
                if ref_path in seen:
                    return obj

                seen.add(ref_path)

                # Resolve the reference
                resolved = self._get_ref_value(ref_path, root_schema)

                # Recursively resolve the resolved object
                resolved = self._resolve_refs(resolved, root_schema, seen.copy())

                # Merge other properties (if any) with resolved content
                result = dict(resolved) if isinstance(resolved, dict) else resolved
                for key, value in obj.items():
                    if key != "$ref":
                        if isinstance(result, dict):
                            result[key] = self._resolve_refs(
                                value, root_schema, seen.copy()
                            )

                return result
            else:
                # Recursively resolve all values in the dictionary
                return {
                    key: self._resolve_refs(value, root_schema, seen.copy())
                    for key, value in obj.items()
                }

        # Handle lists
        elif isinstance(obj, list):
            return [self._resolve_refs(item, root_schema, seen.copy()) for item in obj]

        # Return primitives as-is
        else:
            return obj

    def _get_ref_value(self, ref_path: str, schema: dict[str, Any]) -> Any:
        """
        Get the value from a JSON reference path.

        Args:
            ref_path: JSON reference path (e.g., "#/components/parameters/Slug")
            schema: Root schema to search in

        Returns:
            Referenced value
        """
        # Remove the leading '#/' if present
        if ref_path.startswith("#/"):
            ref_path = ref_path[2:]

        # Split path and navigate through schema
        parts = ref_path.split("/")
        current = schema

        for part in parts:
            if isinstance(current, dict):
                current = current.get(part)
                if current is None:
                    raise ValueError(f"Reference '{ref_path}' not found in schema")
            else:
                raise ValueError(
                    f"Cannot navigate through non-dict at '{part}' "
                    f"in reference '{ref_path}'"
                )

        return current

    def _get_base_url(self, server_index: int) -> str:
        """Extract base URL from schema servers."""
        servers = self.schema.get("servers", [])
        if not servers:
            raise ValueError("No servers defined in OpenAPI schema")
        if server_index >= len(servers):
            raise ValueError(f"Server index {server_index} out of range")
        return servers[server_index]["url"]

    def _parse_operations(self) -> dict[str, dict[str, Any]]:
        """Parse all operations from the schema and index by operationId."""
        operations = {}
        paths = self.schema.get("paths", {})

        for path, path_item in paths.items():
            for method, operation in path_item.items():
                if method.upper() not in [
                    "GET",
                    "POST",
                    "PUT",
                    "PATCH",
                    "DELETE",
                    "HEAD",
                    "OPTIONS",
                ]:
                    continue

                operation_id = operation.get("operationId")
                if not operation_id:
                    continue

                operations[operation_id] = {
                    "path": path,
                    "method": method.upper(),
                    "parameters": operation.get("parameters", []),
                    "requestBody": operation.get("requestBody"),
                    "responses": operation.get("responses", {}),
                }

        return operations

    def _setup_auth(self):
        """Setup authentication based on security schemes."""
        security_schemes = self.schema.get("components", {}).get("securitySchemes", {})

        for _scheme_name, scheme in security_schemes.items():
            if scheme["type"] == "apiKey":
                header_name = scheme.get("name", "Authorization")
                if "api_key" in self.auth:
                    self.session.headers[header_name] = self.auth["api_key"]
            elif scheme["type"] == "http" and scheme.get("scheme") == "basic":
                if "username" in self.auth and "password" in self.auth:
                    self.session.auth = (self.auth["username"], self.auth["password"])
            elif scheme["type"] == "http" and scheme.get("scheme") == "bearer":
                if "token" in self.auth:
                    self.session.headers["Authorization"] = (
                        f"Bearer {self.auth['token']}"
                    )
            elif scheme["type"] == "oauth2":
                # OAuth 2.0 support
                if "client_id" in self.auth and "client_secret" in self.auth:
                    self._setup_oauth2(scheme)

    def _setup_oauth2(self, scheme: dict[str, Any]):
        """Setup OAuth 2.0 Client Credentials Flow."""
        flows = scheme.get("flows", {})

        if "clientCredentials" in flows:
            client_creds = flows["clientCredentials"]
            self._oauth_token_url = client_creds.get("tokenUrl")

            if self._oauth_token_url:
                self._oauth_enabled = True
                # Note: Token will be obtained on first API call

    def _get_basic_auth_header(self) -> str:
        """Generate HTTP Basic auth header for OAuth token endpoint."""
        client_id = self.auth.get("client_id", "")
        client_secret = self.auth.get("client_secret", "")
        credentials = f"{client_id}:{client_secret}"
        encoded = base64.b64encode(credentials.encode()).decode()
        return f"Basic {encoded}"

    def _obtain_oauth_token(self) -> dict[str, Any]:
        """
        Obtain new OAuth 2.0 access token using Client Credentials Flow.

        Returns:
            Token response dict with access_token, token_type, expires_in
        """
        if not self._oauth_token_url:
            raise ValueError("OAuth token URL not configured")

        headers = {
            "Authorization": self._get_basic_auth_header(),
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": self.session.headers.get("User-Agent", "OpenAPI-Client"),
        }

        payload = {"grant_type": "client_credentials"}

        # Make token request (bypass normal call to avoid recursion)
        response = self.session.post(
            self._oauth_token_url, json=payload, headers=headers
        )
        response.raise_for_status()

        token_data = response.json()

        # Store token and calculate expiration
        self._access_token = token_data["access_token"]
        # Subtract 60 seconds as safety margin
        expires_in = token_data.get("expires_in", 3600) - 60
        self._token_expires_at = time.time() + expires_in

        return token_data

    def _ensure_valid_oauth_token(self):
        """Ensure we have a valid OAuth access token, obtaining new one if needed."""
        if not self._access_token or time.time() >= self._token_expires_at:
            self._obtain_oauth_token()

        # Set Bearer token in session headers
        self.session.headers["Authorization"] = f"Bearer {self._access_token}"

    def call(
        self,
        operation_id: str,
        pagination_strategy: Optional[Union[dict[str, Any], bool]] = None,
        **kwargs,
    ) -> Union[requests.Response, list[dict[str, Any]]]:
        """
        Call an API operation by its operationId.

        Automatically paginates if operation has pagination parameters.

        Args:
            operation_id: The operationId from OpenAPI schema
            pagination_strategy: Pagination configuration:
                - None (default): Auto-detect and fetch all pages if paginated
                - False: Disable pagination, return single Response
                - dict: Configure pagination with keys:
                    - "enabled": bool (default True)
                    - "strategy": "auto"|"page"|"offset"|"cursor" (default "auto")
                    - "max_pages": int (optional)
            **kwargs: Parameters (routed automatically)

        Returns:
            - List of all items (if paginated and pagination enabled)
            - requests.Response (if not paginated or pagination disabled)

        Examples:
            # Auto-pagination (returns all items)
            items = client.call("listSubjects", slug="corp")

            # Disable pagination (returns Response)
            response = client.call(
                "listSubjects", slug="corp", pagination_strategy=False
            )

            # Custom pagination
            items = client.call(
                "listSubjects",
                slug="corp",
                pagination_strategy={"max_pages": 3, "strategy": "page"}
            )
        """
        if operation_id not in self.operations:
            raise ValueError(f"Operation '{operation_id}' not found in schema")

        # Parse pagination strategy
        pagination_config = self._parse_pagination_config(
            operation_id, pagination_strategy
        )

        # Check if pagination is enabled and operation supports it
        if pagination_config["enabled"] and self._supports_pagination(operation_id):
            # Auto-paginate and return all items
            return self._call_with_pagination(operation_id, pagination_config, kwargs)
        else:
            # Single request (original behavior)
            return self._call_single(operation_id, kwargs)

    def _parse_pagination_config(
        self, operation_id: str, pagination_strategy: Optional[Union[dict, bool]]
    ) -> dict[str, Any]:
        """Parse pagination_strategy parameter into config dict."""
        # Default config
        config = {
            "enabled": True,
            "strategy": "auto",
            "max_pages": None,
        }

        if pagination_strategy is False:
            # Explicitly disabled
            config["enabled"] = False
        elif pagination_strategy is True or pagination_strategy is None:
            # Enabled with defaults
            config["enabled"] = True
        elif isinstance(pagination_strategy, dict):
            # Custom configuration
            config.update(pagination_strategy)
            config["enabled"] = pagination_strategy.get("enabled", True)

        return config

    def _supports_pagination(self, operation_id: str) -> bool:
        """Check if operation supports pagination."""
        if operation_id not in self.operations:
            return False

        operation = self.operations[operation_id]
        param_names = {p.get("name", "").lower() for p in operation["parameters"]}

        # Check for common pagination parameters
        pagination_params = {"page", "offset", "skip", "cursor", "next"}
        return bool(param_names & pagination_params)

    def _call_with_pagination(
        self, operation_id: str, config: dict[str, Any], params: dict[str, Any]
    ) -> list[dict[str, Any]]:
        """Execute call with automatic pagination."""
        strategy = config.get("strategy", "auto")
        max_pages = config.get("max_pages")

        # Auto-detect strategy if needed
        if strategy == "auto":
            strategy = self._detect_pagination_strategy(operation_id)

        # Get paginator
        paginator = self._get_paginator(strategy)

        # Collect all pages
        all_items = []
        page_count = 0

        for page in paginator(self, operation_id, params):
            if isinstance(page, list):
                all_items.extend(page)
            else:
                all_items.append(page)
            page_count += 1

            if max_pages and page_count >= max_pages:
                break

        return all_items

    def _call_single(
        self, operation_id: str, params: dict[str, Any]
    ) -> requests.Response:
        """Execute single API call without pagination."""
        operation = self.operations[operation_id]

        # OAuth 2.0: Ensure valid token before API call (skip for token endpoint)
        if self._oauth_enabled and "/oauth/token" not in operation.get("path", ""):
            self._ensure_valid_oauth_token()

        # Build the request
        url = self._build_url(operation, params)
        headers = self._build_headers(operation, params)
        query_params = self._build_query_params(operation, params)
        body = self._build_body(operation, params)

        # Make the request
        method = operation["method"]

        response = self.session.request(
            method=method,
            url=url,
            headers=headers,
            params=query_params,
            json=body if body else None,
        )

        return response

    def _build_url(self, operation: dict[str, Any], params: dict[str, Any]) -> str:
        """Build URL with path parameters."""
        path = operation["path"]
        url = self.base_url + path

        # Replace path parameters
        for param in operation["parameters"]:
            if param["in"] == "path" and param["name"] in params:
                placeholder = f"{{{param['name']}}}"
                url = url.replace(placeholder, str(params[param["name"]]))

        return url

    def _build_headers(
        self, operation: dict[str, Any], params: dict[str, Any]
    ) -> dict[str, str]:
        """Build headers from header parameters."""
        headers = {}

        for param in operation["parameters"]:
            if param["in"] == "header" and param["name"] in params:
                headers[param["name"]] = str(params[param["name"]])

        return headers

    def _build_query_params(
        self, operation: dict[str, Any], params: dict[str, Any]
    ) -> dict[str, Any]:
        """Build query parameters."""
        query_params = {}

        for param in operation["parameters"]:
            if param["in"] == "query" and param["name"] in params:
                query_params[param["name"]] = params[param["name"]]

        return query_params

    def _build_body(
        self, operation: dict[str, Any], params: dict[str, Any]
    ) -> Optional[dict[str, Any]]:
        """Build request body from remaining parameters."""
        if not operation.get("requestBody"):
            return None

        if operation["method"] == "POST" and params.get("json"):
            return params.get("json")

        # Get parameter names already used in path, query, or headers
        used_params = set()
        for param in operation["parameters"]:
            if param["in"] == "body":
                used_params.add(param["name"])

        # Remaining parameters go into body
        body_params = {k: v for k, v in params.items() if k not in used_params}

        return body_params if body_params else None

    def download_file(self, operation_id: str, **kwargs) -> bytes:
        """
        Download a file from an API endpoint.

        Args:
            operation_id: The operationId from OpenAPI schema
            **kwargs: Parameters to pass to the operation

        Returns:
            File content as bytes
        """
        # Disable pagination for file downloads
        response = self.call(operation_id, pagination_strategy=False, **kwargs)
        response.raise_for_status()
        return response.content

    def _detect_pagination_strategy(self, operation_id: str) -> str:
        """
        Auto-detect pagination strategy from operation parameters.

        Args:
            operation_id: The operationId to check

        Returns:
            Detected strategy name ("page", "offset", or "cursor")
        """
        if operation_id not in self.operations:
            return "page"  # Default fallback

        operation = self.operations[operation_id]
        param_names = {p.get("name", "").lower() for p in operation["parameters"]}

        # Check for page-based pagination
        if "page" in param_names:
            return "page"

        # Check for offset-based pagination
        if "offset" in param_names or "skip" in param_names:
            return "offset"

        # Check for cursor-based pagination
        if "cursor" in param_names or "next" in param_names:
            return "cursor"

        # Default to page-based
        return "page"

    def _get_paginator(self, strategy: str):
        """Get pagination function for the given strategy."""
        paginators = {
            "page": self._paginate_page_based,
            "offset": self._paginate_offset_based,
            "cursor": self._paginate_cursor_based,
        }

        if strategy not in paginators:
            raise ValueError(
                f"Unknown pagination strategy: {strategy}. "
                f"Use: {', '.join(paginators.keys())}"
            )

        return paginators[strategy]

    def _paginate_page_based(
        self, client, operation_id: str, params: dict[str, Any]
    ) -> Generator[list[dict[str, Any]], None, None]:
        """
        Page-based pagination (page=1, page=2, ...).

        Continues until:
        - Empty response
        - Response with fewer items than expected (< page_size)
        """
        page = params.get("page", 1)
        page_size = params.get("per_page") or params.get("page_size") or 40

        while True:
            # Update page number
            params["page"] = page

            # Make request (use _call_single to avoid recursion)
            response = client._call_single(operation_id, params)
            response.raise_for_status()
            items = response.json()

            # Check if we got results
            if not items:
                break

            yield items

            # Check if this is the last page
            if len(items) < page_size:
                break

            page += 1

    def _paginate_offset_based(
        self, client, operation_id: str, params: dict[str, Any]
    ) -> Generator[list[dict[str, Any]], None, None]:
        """
        Offset-based pagination (offset=0, offset=20, ...).

        Continues until empty response.
        """
        offset = params.get("offset", 0)
        limit = params.get("limit", 20)

        while True:
            # Update offset
            params["offset"] = offset

            # Make request (use _call_single to avoid recursion)
            response = client._call_single(operation_id, params)
            response.raise_for_status()
            items = response.json()

            # Check if we got results
            if not items:
                break

            yield items

            # Check if this is the last page
            if len(items) < limit:
                break

            offset += limit

    def _paginate_cursor_based(
        self, client, operation_id: str, params: dict[str, Any]
    ) -> Generator[list[dict[str, Any]], None, None]:
        """
        Cursor-based pagination (cursor=token).

        Continues until no next cursor in response.
        """
        cursor = params.get("cursor")

        while True:
            # Update cursor if we have one
            if cursor:
                params["cursor"] = cursor

            # Make request (use _call_single to avoid recursion)
            response = client._call_single(operation_id, params)
            response.raise_for_status()
            data = response.json()

            # Extract items (handle different response formats)
            if isinstance(data, list):
                items = data
                next_cursor = None
            elif isinstance(data, dict):
                # Common formats: {items: [...], next_cursor: "..."}
                items = data.get("items") or data.get("data") or data.get("results")
                next_cursor = (
                    data.get("next_cursor")
                    or data.get("next")
                    or data.get("cursor")
                    or data.get("pagination", {}).get("next")
                )
            else:
                break

            # Check if we got results
            if not items:
                break

            yield items

            # Check if there's a next cursor
            if not next_cursor:
                break

            cursor = next_cursor

    def get_schema(self, schema_name: str) -> dict[str, Any]:
        """
        Get a schema definition from components/schemas.

        Args:
            schema_name: Name of the schema (e.g., "User", "Subject", "Invoice")

        Returns:
            Schema definition dictionary

        Raises:
            ValueError: If schema not found

        Example:
            user_schema = client.get_schema("User")
            print(user_schema["properties"]["email"])
        """
        schemas = self.schema.get("components", {}).get("schemas", {})

        if schema_name not in schemas:
            available = ", ".join(schemas.keys())
            raise ValueError(
                f"Schema '{schema_name}' not found. " f"Available schemas: {available}"
            )

        return schemas[schema_name]

    def list_schemas(self) -> list[str]:
        """
        List all available schema names from components/schemas.

        Returns:
            List of schema names

        Example:
            schemas = client.list_schemas()
            print(f"Available schemas: {', '.join(schemas)}")
        """
        return list(self.schema.get("components", {}).get("schemas", {}).keys())

    def get_schema_property(
        self, schema_name: str, property_path: str
    ) -> dict[str, Any]:
        """
        Get a specific property from a schema definition.

        Args:
            schema_name: Name of the schema
            property_path: Dot-separated path to property (e.g., "email", "accounts.0")

        Returns:
            Property definition dictionary

        Raises:
            ValueError: If schema or property not found

        Example:
            email_def = client.get_schema_property("User", "email")
            print(f"Email type: {email_def['type']}")
        """
        schema = self.get_schema(schema_name)

        # Navigate through the property path
        parts = property_path.split(".")
        current = schema.get("properties", {})

        for part in parts:
            if part not in current:
                raise ValueError(
                    f"Property '{property_path}' not found in schema '{schema_name}'"
                )
            current = current[part]

        return current

    def get_schema_for_structured_output(
        self, schema_name: str, exclude_fields: Optional[list[str]] = None
    ) -> dict[str, Any]:
        """
        Get schema formatted for LangChain's with_structured_output.

        This method returns a clean JSON Schema that works with Gemini's
        function calling. The schema name is sanitized to meet Gemini's
        requirements:
        - Must start with a letter or underscore
        - Only alphanumeric (a-z, A-Z, 0-9), underscores (_), dots (.),
          colons (:), dashes (-)
        - Max 64 characters

        Args:
            schema_name: Name of the schema from OpenAPI spec
            exclude_fields: Optional list of field names to exclude from
                          the schema (useful for fields you'll fill
                          programmatically)

        Returns:
            JSON Schema dict compatible with Gemini function calling

        Example:
            # Get schema excluding fields you'll fill later
            schema = client.get_schema_for_structured_output(
                "CreateExpenseRequest",
                exclude_fields=["subject_id", "document_type", "vat_rate"]
            )
            model = model.with_structured_output(schema)
        """
        # Get the base schema
        base_schema = self.get_schema(schema_name)

        # Create a copy to avoid modifying the original
        schema = json.loads(json.dumps(base_schema))

        # Exclude specified fields from properties
        if exclude_fields and "properties" in schema:
            for field in exclude_fields:
                schema["properties"].pop(field, None)

            # Also remove from required fields if present
            if "required" in schema:
                schema["required"] = [
                    req for req in schema["required"] if req not in exclude_fields
                ]

        # Add a title for better Gemini compatibility (use sanitized name)
        # Convert CamelCase to snake_case for Gemini
        sanitized_name = re.sub(r"(?<!^)(?=[A-Z])", "_", schema_name).lower()
        schema["title"] = sanitized_name

        return schema
