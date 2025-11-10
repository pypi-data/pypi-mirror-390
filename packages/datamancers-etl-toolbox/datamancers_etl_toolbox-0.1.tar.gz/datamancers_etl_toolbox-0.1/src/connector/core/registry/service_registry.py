"""
Service registry for managing services and resources.
"""

import inspect
from pathlib import Path
from typing import Dict, List, Optional, Type, Any

from ...core.service import BaseService
from ...core.resource import BaseResource


class ServiceRegistry:
    """
    Registry for services and resources.

    Provides registration and lookup functionality for services and resources.
    Optionally integrates with ManifestAPI for automatic manifest generation.
    """

    def __init__(
        self, auto_generate_manifests: bool = True, auto_discover_openapi: bool = True
    ):
        """
        Initialize service registry.

        Args:
            auto_generate_manifests: If True, automatically generate manifests
                                   when services/resources are registered.
                                   Defaults to True.
            auto_discover_openapi: If True, automatically discover and register
                                 all OpenAPI schemas from schemas directory.
                                 Defaults to True.
        """
        self._services: Dict[str, Type[BaseService]] = {}
        self._resources: Dict[str, Dict[str, Type[BaseResource]]] = {}
        # Index operation_id -> (service_name, resource_name, endpoint)
        self._operation_index: Dict[str, Dict[str, Any]] = {}
        self._auto_generate_manifests = auto_generate_manifests

        # Lazy import to avoid circular dependency
        self._manifest_api = None
        if auto_generate_manifests:
            self._init_manifest_api()

        # Auto-discover OpenAPI schemas if enabled
        if auto_discover_openapi:
            self._auto_discover_openapi_schemas()

    def _init_manifest_api(self):
        """Initialize ManifestAPI if not already initialized."""
        if self._manifest_api is None:
            try:
                from ..manifest.api import ManifestAPI

                self._manifest_api = ManifestAPI(registry=self)
            except ImportError:
                # Manifest system not available, disable auto-generation
                self._auto_generate_manifests = False
                self._manifest_api = None

    def register_service(self, service_name: str, service_class: Type[BaseService]):
        """
        Register a service class.

        Args:
            service_name: Service name (e.g., "google_sheets")
            service_class: Service class

        Raises:
            ValueError: If service_name is invalid or service_class is not a subclass of BaseService
        """
        if not service_name:
            raise ValueError("service_name is required")
        if not issubclass(service_class, BaseService):
            raise ValueError("service_class must be a subclass of BaseService")

        self._services[service_name] = service_class

        # Auto-generate manifest if enabled
        if self._auto_generate_manifests and self._manifest_api:
            try:
                # Generate and cache manifest
                self._manifest_api.get_service_manifest_by_name(service_name)
            except Exception:
                # Manifest generation failed, but don't fail registration
                pass

    def register_resource(
        self,
        service_name: str,
        resource_name: str,
        resource_class: Type[BaseResource],
    ):
        """
        Register a resource class for a service.

        Args:
            service_name: Service name
            resource_name: Resource name (e.g., "spreadsheet")
            resource_class: Resource class

        Raises:
            ValueError: If service_name or resource_name is invalid
        """
        if not service_name:
            raise ValueError("service_name is required")
        if not resource_name:
            raise ValueError("resource_name is required")
        if not issubclass(resource_class, BaseResource):
            raise ValueError("resource_class must be a subclass of BaseResource")

        if service_name not in self._resources:
            self._resources[service_name] = {}

        self._resources[service_name][resource_name] = resource_class

        # Auto-generate manifest if enabled
        if self._auto_generate_manifests and self._manifest_api:
            try:
                # Generate and cache manifest
                self._manifest_api.get_resource_manifest_by_name(
                    service_name, resource_name
                )
            except Exception:
                # Manifest generation failed, but don't fail registration
                pass

    def get_service(self, service_name: str) -> Type[BaseService]:
        """
        Get service class by name.

        Args:
            service_name: Service name

        Returns:
            Type[BaseService]: Service class

        Raises:
            ValueError: If service not found
        """
        if service_name not in self._services:
            raise ValueError(f"Service '{service_name}' not found")
        return self._services[service_name]

    def get_resource(self, service_name: str, resource_name: str) -> Type[BaseResource]:
        """
        Get resource class by service and resource name.

        Args:
            service_name: Service name
            resource_name: Resource name

        Returns:
            Type[BaseResource]: Resource class

        Raises:
            ValueError: If service or resource not found
        """
        if service_name not in self._resources:
            raise ValueError(f"Service '{service_name}' not found")
        if resource_name not in self._resources[service_name]:
            raise ValueError(
                f"Resource '{resource_name}' not found in service '{service_name}'"
            )
        return self._resources[service_name][resource_name]

    def list_services(self) -> List[str]:
        """
        List all registered service names.

        Returns:
            List[str]: List of service names
        """
        return list(self._services.keys())

    def list_resources(self, service_name: str) -> List[str]:
        """
        List all registered resource names for a service.

        Args:
            service_name: Service name

        Returns:
            List[str]: List of resource names
        """
        if service_name not in self._resources:
            return []
        return list(self._resources[service_name].keys())

    def has_service(self, service_name: str) -> bool:
        """
        Check if service is registered.

        Args:
            service_name: Service name

        Returns:
            bool: True if service is registered
        """
        return service_name in self._services

    def has_resource(self, service_name: str, resource_name: str) -> bool:
        """
        Check if resource is registered for a service.

        Args:
            service_name: Service name
            resource_name: Resource name

        Returns:
            bool: True if resource is registered
        """
        return (
            service_name in self._resources
            and resource_name in self._resources[service_name]
        )

    def register_operation(
        self,
        service_name: str,
        resource_name: str,
        operation_id: str,
        endpoint: Optional[str] = None,
    ):
        """
        Register an operation with its operation_id.

        This creates an index mapping operation_id to (service_name, resource_name, endpoint).

        Args:
            service_name: Service name
            resource_name: Resource name
            operation_id: Operation ID (must be unique within service)
            endpoint: Optional endpoint for the operation
        """
        if not service_name:
            raise ValueError("service_name is required")
        if not resource_name:
            raise ValueError("resource_name is required")
        if not operation_id:
            raise ValueError("operation_id is required")

        # Check if operation_id already exists
        if operation_id in self._operation_index:
            existing = self._operation_index[operation_id]
            if (
                existing["service_name"] != service_name
                or existing["resource_name"] != resource_name
            ):
                # Operation ID collision - log warning but allow override
                pass

        self._operation_index[operation_id] = {
            "service_name": service_name,
            "resource_name": resource_name,
            "endpoint": endpoint,
        }

    def get_operation_info(
        self, operation_id: str, service_name: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get service and resource information for an operation_id.

        Args:
            operation_id: Operation ID
            service_name: Optional service name to disambiguate (required if operation_id is not globally unique)

        Returns:
            Optional[Dict[str, Any]]: Dictionary with service_name, resource_name, endpoint
                                     or None if operation_id not found
        """
        # If service_name is provided, check for operation in that service
        if service_name:
            operation_info = self._operation_index.get(operation_id)
            if operation_info and operation_info["service_name"] == service_name:
                return operation_info
            return None

        # Without service_name, return first match (if operation_id is globally unique)
        return self._operation_index.get(operation_id)

    def find_operation(self, operation_id: str) -> Optional[Dict[str, Any]]:
        """
        Find operation by operation_id.

        Alias for get_operation_info() for backward compatibility.

        Args:
            operation_id: Operation ID

        Returns:
            Optional[Dict[str, Any]]: Dictionary with service_name, resource_name, endpoint
        """
        return self.get_operation_info(operation_id)

    def list_operations(
        self, service_name: str, resource_name: Optional[str] = None
    ) -> List[str]:
        """
        List all operation IDs for a service or resource.

        Args:
            service_name: Service name
            resource_name: Optional resource name (if provided, list only operations for that resource)

        Returns:
            List[str]: List of operation IDs
        """
        operations = []
        for operation_id, operation_info in self._operation_index.items():
            if operation_info["service_name"] == service_name:
                if (
                    resource_name is None
                    or operation_info["resource_name"] == resource_name
                ):
                    operations.append(operation_id)
        return sorted(operations)

    def search_operations(
        self,
        service_name: Optional[str] = None,
        resource_name: Optional[str] = None,
        name_filter: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Search for operations with optional filtering.

        Args:
            service_name: Optional service name filter
            resource_name: Optional resource name filter
            name_filter: Optional filter string to match operation IDs (case-insensitive partial match)

        Returns:
            List[Dict[str, Any]]: List of operation information dictionaries with:
                - operation_id: Operation ID
                - service_name: Service name
                - resource_name: Resource name
                - endpoint: Endpoint path
        """
        results = []

        for operation_id, operation_info in self._operation_index.items():
            # Filter by service
            if service_name and operation_info["service_name"] != service_name:
                continue

            # Filter by resource
            if resource_name and operation_info["resource_name"] != resource_name:
                continue

            # Filter by name
            if name_filter:
                name_filter_lower = name_filter.lower()
                if name_filter_lower not in operation_id.lower():
                    continue

            results.append(
                {
                    "operation_id": operation_id,
                    "service_name": operation_info["service_name"],
                    "resource_name": operation_info["resource_name"],
                    "endpoint": operation_info.get("endpoint"),
                }
            )

        return sorted(results, key=lambda x: x["operation_id"])

    def get_operation_details(
        self, operation_id: str, service_name: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get complete details for an operation including manifest metadata.

        Args:
            operation_id: Operation ID
            service_name: Optional service name to disambiguate

        Returns:
            Optional[Dict[str, Any]]: Complete operation details including:
                - operation_id: Operation ID
                - service_name: Service name
                - resource_name: Resource name
                - endpoint: Endpoint path
                - manifest: Operation manifest with parameters, request/response schemas, etc.
        """
        # Get basic operation info
        operation_info = self.get_operation_info(operation_id, service_name)
        if not operation_info:
            return None

        details = {
            "operation_id": operation_id,
            "service_name": operation_info["service_name"],
            "resource_name": operation_info["resource_name"],
            "endpoint": operation_info.get("endpoint"),
            "manifest": None,
        }

        # Try to get manifest if available
        if self._manifest_api:
            try:
                manifest = self.get_operation_manifest(
                    operation_info["service_name"],
                    operation_info["resource_name"],
                    operation_id,
                )
                if manifest:
                    details["manifest"] = {
                        "name": manifest.name,
                        "description": manifest.description,
                        "parameters": [
                            {
                                "name": param.name,
                                "type": param.type,
                                "required": param.required,
                                "description": param.description,
                                "default": param.default,
                                "validation_rules": param.validation_rules,
                            }
                            for param in manifest.parameters
                        ],
                        "required_parameters": [
                            {
                                "name": param.name,
                                "type": param.type,
                                "description": param.description,
                            }
                            for param in manifest.get_required_parameters()
                        ],
                        "optional_parameters": [
                            {
                                "name": param.name,
                                "type": param.type,
                                "description": param.description,
                                "default": param.default,
                            }
                            for param in manifest.parameters
                            if not param.required
                        ],
                        "return_type": manifest.return_type,
                        "return_description": manifest.return_description,
                        "validation_rules": manifest.validation_rules,
                        "request_schema": manifest.request_schema,
                        "response_schema": manifest.response_schema,
                    }
            except Exception:
                # Manifest not available, try to get from OpenAPI schema
                pass

        # Try to get request/response schemas from OpenAPI schema if manifest doesn't have them
        if not details.get("manifest") or not details["manifest"].get("request_schema"):
            try:
                # Try to get from OpenAPI schema
                from ...services.types.open_api_adapter.openapi_client import (
                    OpenAPIClient,
                )
                from pathlib import Path

                service_class = self.get_service(operation_info["service_name"])
                from ...services.types.open_api_adapter.service import OpenAPIService

                if issubclass(service_class, OpenAPIService):
                    # Extract app_name from service_name
                    app_name = (
                        operation_info["service_name"]
                        .replace("_api_v3", "")
                        .replace("_api_v2", "")
                        .replace("_api_v1", "")
                        .replace("_api", "")
                    )

                    # Find schema file
                    schemas_dir = (
                        Path(__file__).parent.parent.parent
                        / "services"
                        / "types"
                        / "open_api_adapter"
                        / "schemas"
                    )
                    if not schemas_dir.exists():
                        import os

                        cwd = Path(os.getcwd())
                        schemas_dir = (
                            cwd
                            / "src"
                            / "connector"
                            / "services"
                            / "types"
                            / "open_api_adapter"
                            / "schemas"
                        )

                    schema_file = schemas_dir / f"{app_name}.json"
                    if schema_file.exists():
                        import json

                        with open(schema_file, "r") as f:
                            schema = json.load(f)

                        # Find operation in schema
                        paths = schema.get("paths", {})
                        for path, path_item in paths.items():
                            for method, operation in path_item.items():
                                if method.upper() not in [
                                    "GET",
                                    "POST",
                                    "PUT",
                                    "PATCH",
                                    "DELETE",
                                ]:
                                    continue

                                op_id = operation.get("operationId")
                                if op_id == operation_id:
                                    # Extract request/response schemas
                                    request_schema = None
                                    request_body = operation.get("requestBody")
                                    if request_body:
                                        content = request_body.get("content", {})
                                        if "application/json" in content:
                                            request_schema = content[
                                                "application/json"
                                            ].get("schema")

                                    response_schema = None
                                    responses = operation.get("responses", {})
                                    if "200" in responses:
                                        response_200 = responses["200"]
                                        content = response_200.get("content", {})
                                        if "application/json" in content:
                                            response_schema = content[
                                                "application/json"
                                            ].get("schema")

                                    # Extract parameters with location
                                    parameters = []
                                    for param in operation.get("parameters", []):
                                        parameters.append(
                                            {
                                                "name": param.get("name"),
                                                "type": param.get("schema", {}).get(
                                                    "type", "string"
                                                ),
                                                "required": param.get(
                                                    "required", False
                                                ),
                                                "description": param.get("description"),
                                                "in": param.get(
                                                    "in"
                                                ),  # path, query, header, cookie
                                                "schema": param.get("schema"),
                                            }
                                        )

                                    # Update manifest or create new one
                                    if not details.get("manifest"):
                                        details["manifest"] = {}

                                    details["manifest"].update(
                                        {
                                            "request_schema": request_schema,
                                            "response_schema": response_schema,
                                            "parameters_with_location": parameters,
                                            "method": method.upper(),
                                            "path": path,
                                        }
                                    )
                                    break
            except Exception:
                pass

        return details

    def _resolve_schema_reference(
        self, schema: Dict[str, Any], schema_obj: Optional[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """
        Resolve OpenAPI schema reference ($ref) to full schema.

        Args:
            schema: Full OpenAPI schema dictionary
            schema_obj: Schema object that may contain $ref

        Returns:
            Resolved schema dictionary or None
        """
        if not schema_obj or not isinstance(schema_obj, dict):
            return schema_obj

        # If schema has $ref, resolve it
        if "$ref" in schema_obj:
            ref_path = schema_obj["$ref"]
            # Remove #/ prefix if present
            if ref_path.startswith("#/"):
                ref_path = ref_path[2:]

            # Navigate through schema using path
            parts = ref_path.split("/")
            resolved = schema
            for part in parts:
                if isinstance(resolved, dict):
                    resolved = resolved.get(part)
                else:
                    return schema_obj  # Can't resolve, return original

            # Recursively resolve any nested references
            if isinstance(resolved, dict):
                resolved = self._resolve_schema_reference(schema, resolved)
                # Merge any additional properties from original schema_obj
                if isinstance(resolved, dict):
                    merged = {**resolved}
                    # Preserve any additional properties from original
                    for key, value in schema_obj.items():
                        if key != "$ref":
                            merged[key] = value
                    return merged
                return resolved

            return resolved

        # If schema has allOf, oneOf, anyOf, resolve them
        for key in ["allOf", "oneOf", "anyOf"]:
            if key in schema_obj:
                resolved_items = []
                for item in schema_obj[key]:
                    resolved_item = self._resolve_schema_reference(schema, item)
                    if isinstance(resolved_item, dict):
                        resolved_items.append(resolved_item)
                    else:
                        resolved_items.append(item)

                # Merge resolved items
                merged = {**schema_obj}
                merged[key] = resolved_items
                return merged

        # If schema has items (for arrays), resolve items schema
        if "items" in schema_obj:
            resolved_items = self._resolve_schema_reference(schema, schema_obj["items"])
            if isinstance(resolved_items, dict):
                merged = {**schema_obj}
                merged["items"] = resolved_items
                return merged

        # If schema has properties, resolve each property
        if "properties" in schema_obj:
            resolved_properties = {}
            for prop_name, prop_schema in schema_obj["properties"].items():
                resolved_prop = self._resolve_schema_reference(schema, prop_schema)
                resolved_properties[prop_name] = resolved_prop
            merged = {**schema_obj}
            merged["properties"] = resolved_properties
            return merged

        return schema_obj

    def clear(self):
        """Clear all registered services and resources."""
        self._services.clear()
        self._resources.clear()
        # Clear manifest cache if available
        if self._manifest_api:
            self._manifest_api.clear_cache()

    def get_service_manifest(self, service_name: str):
        """
        Get service manifest by service name.

        Requires auto_generate_manifests=True and ManifestAPI to be available.

        Args:
            service_name: Service name

        Returns:
            ServiceManifest: Service manifest

        Raises:
            ValueError: If manifest system is not available or service not found
        """
        if not self._manifest_api:
            raise ValueError(
                "Manifest system is not available. "
                "Set auto_generate_manifests=True or initialize ManifestAPI manually."
            )
        return self._manifest_api.get_service_manifest_by_name(service_name)

    def get_resource_manifest(self, service_name: str, resource_name: str):
        """
        Get resource manifest by service and resource name.

        Requires auto_generate_manifests=True and ManifestAPI to be available.

        Args:
            service_name: Service name
            resource_name: Resource name

        Returns:
            ResourceManifest: Resource manifest

        Raises:
            ValueError: If manifest system is not available or service/resource not found
        """
        if not self._manifest_api:
            raise ValueError(
                "Manifest system is not available. "
                "Set auto_generate_manifests=True or initialize ManifestAPI manually."
            )
        return self._manifest_api.get_resource_manifest_by_name(
            service_name, resource_name
        )

    def get_operation_manifest(
        self, service_name: str, resource_name: str, operation_name: str
    ):
        """
        Get operation manifest by service, resource, and operation name.

        Requires auto_generate_manifests=True and ManifestAPI to be available.

        Args:
            service_name: Service name
            resource_name: Resource name
            operation_name: Operation name

        Returns:
            Optional[OperationManifest]: Operation manifest or None

        Raises:
            ValueError: If manifest system is not available
        """
        if not self._manifest_api:
            raise ValueError(
                "Manifest system is not available. "
                "Set auto_generate_manifests=True or initialize ManifestAPI manually."
            )
        return self._manifest_api.get_operation_manifest(
            service_name, resource_name, operation_name
        )

    @property
    def manifest_api(self):
        """
        Get ManifestAPI instance if available.

        Returns:
            Optional[ManifestAPI]: ManifestAPI instance or None
        """
        return self._manifest_api

    def search_services(
        self, name_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for services with optional name filtering.

        Args:
            name_filter: Optional filter string to match service names (case-insensitive partial match)

        Returns:
            List[Dict[str, Any]]: List of service information dictionaries with:
                - name: Service name
                - resources: List of resource names
                - metadata: Service metadata (base_url, auth, pagination, etc.)
        """
        all_services = self.list_services()

        # Filter by name if provided
        if name_filter:
            name_filter_lower = name_filter.lower()
            all_services = [
                service
                for service in all_services
                if name_filter_lower in service.lower()
            ]

        # Get metadata for each service
        results = []
        for service_name in all_services:
            try:
                metadata = self.get_service_metadata(service_name)
                results.append(
                    {
                        "name": service_name,
                        "resources": self.list_resources(service_name),
                        "metadata": metadata,
                    }
                )
            except Exception:
                # If metadata retrieval fails, still include basic info
                results.append(
                    {
                        "name": service_name,
                        "resources": self.list_resources(service_name),
                        "metadata": None,
                    }
                )

        return results

    def get_service_metadata(self, service_name: str) -> Dict[str, Any]:
        """
        Get complete metadata for a service.

        Args:
            service_name: Service name

        Returns:
            Dict[str, Any]: Service metadata including:
                - name: Service name
                - base_url: Base URL of the service
                - authentication_methods: Available authentication methods
                - default_strategies: Default strategies (pagination, retry)
                - resources: List of resources with their metadata
                - version: Service version
                - description: Service description

        Raises:
            ValueError: If service not found
        """
        if not self.has_service(service_name):
            raise ValueError(f"Service '{service_name}' not found")

        # Try to get manifest first (most complete metadata)
        metadata = {
            "name": service_name,
            "base_url": None,
            "authentication_methods": [],
            "default_strategies": {},
            "resources": [],
            "version": "1.0.0",
            "description": None,
        }

        # Get manifest if available
        if self._manifest_api:
            try:
                manifest = self.get_service_manifest(service_name)
                metadata.update(
                    {
                        "base_url": manifest.base_url,
                        "authentication_methods": manifest.authentication_methods,
                        "version": manifest.version,
                        "description": manifest.description,
                        "resources": [
                            {
                                "name": resource.name,
                                "endpoint": resource.endpoint,
                                "description": resource.description,
                                "operations": [
                                    {
                                        "name": op.name,
                                        "description": op.description,
                                        "parameters": [
                                            {
                                                "name": param.name,
                                                "type": param.type,
                                                "required": param.required,
                                                "description": param.description,
                                            }
                                            for param in op.parameters
                                        ],
                                    }
                                    for op in resource.operations
                                ],
                            }
                            for resource in manifest.resources
                        ],
                    }
                )
            except Exception:
                # Manifest not available, try to get from service class
                pass

        # If manifest didn't provide resources, get them from registry
        if not metadata["resources"]:
            resource_names = self.list_resources(service_name)
            metadata["resources"] = [
                {
                    "name": resource_name,
                    "endpoint": None,
                    "description": None,
                    "operations": [],
                }
                for resource_name in resource_names
            ]

        # Try to get base_url and auth from service class if not in manifest
        if not metadata["base_url"]:
            try:
                service_class = self.get_service(service_name)
                # Try to create instance to get base_url
                try:
                    # For OpenAPIService, we need app_name
                    if hasattr(service_class, "__init__"):
                        sig = inspect.signature(service_class.__init__)
                        if "app_name" in sig.parameters:
                            # It's OpenAPIService, try to get base_url from OpenAPIClient
                            # We can't create instance without app_name, so skip
                            pass
                        else:
                            service_instance = service_class()
                            metadata["base_url"] = getattr(
                                service_instance, "base_url", None
                            )
                            # Get auth strategy info
                            if hasattr(service_instance, "auth_strategy"):
                                auth_strategy = service_instance.auth_strategy
                                if auth_strategy:
                                    metadata["authentication_methods"] = [
                                        {
                                            "type": auth_strategy.__class__.__name__,
                                            "description": auth_strategy.__class__.__doc__,
                                        }
                                    ]
                            # Get pagination strategy info
                            if hasattr(service_instance, "pagination_strategy"):
                                pagination_strategy = (
                                    service_instance.pagination_strategy
                                )
                                if pagination_strategy:
                                    metadata["default_strategies"]["pagination"] = {
                                        "type": pagination_strategy.__class__.__name__,
                                        "description": pagination_strategy.__class__.__doc__,
                                    }
                            # Get retry strategy info
                            if hasattr(service_instance, "retry_strategy"):
                                retry_strategy = service_instance.retry_strategy
                                if retry_strategy:
                                    metadata["default_strategies"]["retry"] = {
                                        "type": retry_strategy.__class__.__name__,
                                        "description": retry_strategy.__class__.__doc__,
                                    }
                except Exception:
                    pass
            except Exception:
                pass

        # For OpenAPIService, try to get info from OpenAPIClient schema
        if not metadata["base_url"]:
            try:
                service_class = self.get_service(service_name)
                # Check if it's OpenAPIService
                from ...services.types.open_api_adapter.service import OpenAPIService

                if issubclass(service_class, OpenAPIService):
                    # Try to extract app_name from service_name
                    # Service names are like "fakturoid_api_v3" -> app_name is "fakturoid"
                    app_name = (
                        service_name.replace("_api_v3", "")
                        .replace("_api_v2", "")
                        .replace("_api_v1", "")
                        .replace("_api", "")
                    )

                    # Try to load schema and get base_url and auth
                    try:
                        from ...services.types.open_api_adapter.openapi_client import (
                            OpenAPIClient,
                        )
                        from pathlib import Path

                        # Find schema file
                        schemas_dir = (
                            Path(__file__).parent.parent.parent
                            / "services"
                            / "types"
                            / "open_api_adapter"
                            / "schemas"
                        )
                        if not schemas_dir.exists():
                            import os

                            cwd = Path(os.getcwd())
                            schemas_dir = (
                                cwd
                                / "src"
                                / "connector"
                                / "services"
                                / "types"
                                / "open_api_adapter"
                                / "schemas"
                            )

                        schema_file = schemas_dir / f"{app_name}.json"
                        if schema_file.exists():
                            # Load schema
                            import json

                            with open(schema_file, "r") as f:
                                schema = json.load(f)

                            # Get base_url from servers
                            servers = schema.get("servers", [])
                            if servers:
                                metadata["base_url"] = servers[0].get("url", None)

                            # Get authentication methods from security schemes
                            components = schema.get("components", {})
                            security_schemes = components.get("securitySchemes", {})
                            if security_schemes:
                                metadata["authentication_methods"] = [
                                    {
                                        "name": name,
                                        "type": scheme.get("type", "unknown"),
                                        "scheme": scheme.get("scheme"),
                                        "description": scheme.get("description"),
                                        "flows": scheme.get("flows", {}),
                                        "token_url": scheme.get("flows", {})
                                        .get("clientCredentials", {})
                                        .get("tokenUrl")
                                        if scheme.get("type") == "oauth2"
                                        else None,
                                    }
                                    for name, scheme in security_schemes.items()
                                ]

                            # Get resource endpoints from paths
                            paths = schema.get("paths", {})
                            resource_endpoints = {}
                            for path, path_item in paths.items():
                                # Extract resource name from path
                                # e.g., "/accounts/{slug}/subjects.json" -> "subjects"
                                path_parts = path.strip("/").split("/")
                                # Find resource name (usually the last part before .json or after accounts)
                                resource_name = None
                                for part in reversed(path_parts):
                                    if (
                                        part
                                        and not part.startswith("{")
                                        and part != "accounts"
                                    ):
                                        resource_name = part.replace(
                                            ".json", ""
                                        ).replace(".yaml", "")
                                        break

                                if resource_name:
                                    if resource_name not in resource_endpoints:
                                        resource_endpoints[resource_name] = path

                            # Update resources with endpoints
                            for resource in metadata["resources"]:
                                resource_name = resource["name"]
                                if resource_name in resource_endpoints:
                                    resource["endpoint"] = resource_endpoints[
                                        resource_name
                                    ]

                            # Get default pagination info from schema (if available)
                            # OpenAPI doesn't have standard pagination, but we can check for common patterns
                            # For now, we'll note that pagination is supported
                            metadata["default_strategies"]["pagination"] = {
                                "type": "automatic",
                                "description": "Automatic pagination support based on OpenAPI schema",
                            }
                    except Exception:
                        pass
            except Exception:
                pass

        return metadata

    def _auto_discover_openapi_schemas(self):
        """
        Automatically discover and register all OpenAPI schemas from schemas directory.

        This method scans the OpenAPI schemas directory and automatically registers
        all available services using the OpenAPI Translator.
        """
        try:
            from ..openapi_translator.registry_integration import RegistryIntegration
            from ...services.types.open_api_adapter.translator import OpenAPITranslator

            # Find schemas directory - try multiple paths
            possible_paths = [
                # Relative to this file: core/registry/service_registry.py
                Path(__file__).parent.parent.parent
                / "services"
                / "types"
                / "open_api_adapter"
                / "schemas",
                # From workspace root
                Path(__file__).parent.parent.parent.parent.parent
                / "src"
                / "connector"
                / "services"
                / "types"
                / "open_api_adapter"
                / "schemas",
            ]

            # Also try to find it relative to current working directory
            import os

            cwd = Path(os.getcwd())
            possible_paths.extend(
                [
                    cwd
                    / "src"
                    / "connector"
                    / "services"
                    / "types"
                    / "open_api_adapter"
                    / "schemas",
                    cwd
                    / "connector"
                    / "services"
                    / "types"
                    / "open_api_adapter"
                    / "schemas",
                ]
            )

            schemas_dir = None
            for path in possible_paths:
                if path.exists() and path.is_dir():
                    schemas_dir = path
                    break

            if not schemas_dir:
                # Schemas directory not found, skip auto-discovery
                return

            # Initialize translator and integration
            translator = OpenAPITranslator()
            integration = RegistryIntegration(self)

            # Find all JSON schema files
            schema_files = list(schemas_dir.glob("*.json"))

            for schema_file in schema_files:
                try:
                    # Register service from schema
                    service_name = integration.register_from_translator(
                        translator, schema_file
                    )
                    # Service is now registered in self via RegistryIntegration
                except Exception:
                    # Log error but continue with other schemas
                    # Don't fail on individual schema errors
                    pass

        except ImportError:
            # OpenAPI Translator not available, skip auto-discovery
            pass
        except Exception:
            # Any other error, skip auto-discovery
            pass
