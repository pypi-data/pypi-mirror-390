"""
Manifest generator for creating service manifests.
"""

import inspect
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Type, Union

from .base import (
    ServiceManifest,
    ResourceManifest,
    OperationManifest,
    ParameterManifest,
)
from ..service import BaseService
from ..resource import BaseResource


class ManifestGenerator:
    """
    Generator for creating service manifests from service and resource classes.
    """

    def generate_service_manifest(
        self, service_class: Type[BaseService], service_name: Optional[str] = None
    ) -> ServiceManifest:
        """
        Generate service manifest from service class.

        Args:
            service_class: Service class
            service_name: Optional service name (defaults to class name)

        Returns:
            ServiceManifest: Generated service manifest
        """
        if not service_name:
            service_name = service_class.__name__.replace("Service", "").lower()

        # Create service instance to get base_url
        try:
            service_instance = service_class()
            base_url = service_instance.base_url
        except Exception:
            base_url = None

        # Extract authentication methods
        auth_methods = self._extract_authentication_methods(service_class)

        # Extract resources (if any are defined in the service class)
        resources = self._extract_resources(service_class)

        return ServiceManifest(
            name=service_name,
            version="1.0.0",
            description=service_class.__doc__,
            base_url=base_url,
            authentication_methods=auth_methods,
            resources=resources,
        )

    def generate_resource_manifest(
        self, resource_class: Type[BaseResource], resource_name: Optional[str] = None
    ) -> ResourceManifest:
        """
        Generate resource manifest from resource class.

        Args:
            resource_class: Resource class
            resource_name: Optional resource name (defaults to class name)

        Returns:
            ResourceManifest: Generated resource manifest
        """
        if not resource_name:
            resource_name = resource_class.__name__.replace("Resource", "").lower()

        # Extract operations from resource methods
        operations = self._extract_operations(resource_class)

        # Try to get endpoint from __init__ if possible
        endpoint = self._extract_endpoint(resource_class)

        return ResourceManifest(
            name=resource_name,
            description=resource_class.__doc__,
            operations=operations,
            endpoint=endpoint,
        )

    def _extract_authentication_methods(
        self, service_class: Type[BaseService]
    ) -> List[Dict[str, Any]]:
        """
        Extract authentication methods from service class.

        Args:
            service_class: Service class

        Returns:
            List[Dict[str, Any]]: List of authentication method dictionaries
        """
        auth_methods = []

        # Check if service has auth_strategy
        try:
            service_instance = service_class()
            if service_instance.auth_strategy:
                auth_type = type(service_instance.auth_strategy).__name__
                auth_methods.append(
                    {
                        "type": auth_type,
                        "description": service_instance.auth_strategy.__class__.__doc__,
                    }
                )
        except Exception:
            pass

        return auth_methods

    def _extract_resources(
        self, service_class: Type[BaseService]
    ) -> List[ResourceManifest]:
        """
        Extract resources from service class.

        Args:
            service_class: Service class

        Returns:
            List[ResourceManifest]: List of resource manifests
        """
        # Resources are typically defined in separate classes
        # This method would need to scan the module for resource classes
        # For now, return empty list
        return []

    def _extract_operations(
        self, resource_class: Type[BaseResource]
    ) -> List[OperationManifest]:
        """
        Extract operations from resource class.

        Args:
            resource_class: Resource class

        Returns:
            List[OperationManifest]: List of operation manifests
        """
        operations = []

        # Get all public methods
        for method_name in dir(resource_class):
            if method_name.startswith("_"):
                continue

            method = getattr(resource_class, method_name)
            if not callable(method) or method_name in ["run"]:
                continue

            # Skip inherited methods from BaseResource
            if method_name in ["create", "read", "update", "delete", "list", "extract", "load"]:
                continue

            # Extract operation details
            operation = self._extract_operation(method, method_name)
            if operation:
                operations.append(operation)

        # Add standard CRUD operations
        operations.extend(self._get_standard_operations())

        return operations

    def _extract_operation(self, method: callable, method_name: str) -> Optional[OperationManifest]:
        """
        Extract operation manifest from method.

        Args:
            method: Method object
            method_name: Method name

        Returns:
            Optional[OperationManifest]: Operation manifest or None
        """
        # Get method signature
        sig = inspect.signature(method)
        parameters = []

        # Extract parameters
        for param_name, param in sig.parameters.items():
            if param_name == "self":
                continue

            param_type = "Any"
            if param.annotation != inspect.Parameter.empty:
                param_type = str(param.annotation)

            parameters.append(
                ParameterManifest(
                    name=param_name,
                    type=param_type,
                    required=param.default == inspect.Parameter.empty,
                    description=None,
                    default=param.default if param.default != inspect.Parameter.empty else None,
                )
            )

        return OperationManifest(
            name=method_name,
            description=method.__doc__,
            parameters=parameters,
            return_type=str(sig.return_annotation)
            if sig.return_annotation != inspect.Signature.empty
            else None,
        )

    def _get_standard_operations(self) -> List[OperationManifest]:
        """
        Get standard CRUD operations.

        Returns:
            List[OperationManifest]: List of standard operation manifests
        """
        return [
            OperationManifest(
                name="create",
                description="Create a new resource",
                parameters=[
                    ParameterManifest(
                        name="data", type="Dict[str, Any]", required=True, description="Resource data"
                    )
                ],
                return_type="Any",
            ),
            OperationManifest(
                name="read",
                description="Read a resource by ID",
                parameters=[
                    ParameterManifest(
                        name="resource_id", type="str", required=True, description="Resource identifier"
                    )
                ],
                return_type="Any",
            ),
            OperationManifest(
                name="update",
                description="Update a resource",
                parameters=[
                    ParameterManifest(
                        name="resource_id", type="str", required=True, description="Resource identifier"
                    ),
                    ParameterManifest(
                        name="data", type="Dict[str, Any]", required=True, description="Updated resource data"
                    ),
                ],
                return_type="Any",
            ),
            OperationManifest(
                name="delete",
                description="Delete a resource",
                parameters=[
                    ParameterManifest(
                        name="resource_id", type="str", required=True, description="Resource identifier"
                    )
                ],
                return_type="bool",
            ),
            OperationManifest(
                name="list",
                description="List all resources",
                parameters=[
                    ParameterManifest(
                        name="params", type="Optional[Dict[str, Any]]", required=False, description="Query parameters"
                    )
                ],
                return_type="List[Any]",
            ),
        ]

    def _extract_endpoint(self, resource_class: Type[BaseResource]) -> Optional[str]:
        """
        Extract endpoint from resource class.

        Args:
            resource_class: Resource class

        Returns:
            Optional[str]: Endpoint or None
        """
        # Try to get endpoint from __init__ signature
        try:
            sig = inspect.signature(resource_class.__init__)
            for param_name, param in sig.parameters.items():
                if param_name == "endpoint":
                    # Can't get default value easily, return None
                    return None
        except Exception:
            pass

        return None

    def generate_manifest_from_openapi_schema(
        self, schema: Union[Dict[str, Any], Path, str], service_name: Optional[str] = None
    ) -> ServiceManifest:
        """
        Generate service manifest from OpenAPI schema.

        Args:
            schema: OpenAPI schema dictionary, file path, or file path string
            service_name: Optional service name (defaults to schema title)

        Returns:
            ServiceManifest: Generated service manifest
        """
        # Load schema if needed
        if isinstance(schema, (str, Path)):
            schema_path = Path(schema)
            with open(schema_path, "r") as f:
                schema = json.load(f)

        # Extract service info
        info = schema.get("info", {})
        if not service_name:
            service_name = info.get("title", "unknown_service").lower().replace(" ", "_")
        version = info.get("version", "1.0.0")
        description = info.get("description")

        # Extract base URL
        servers = schema.get("servers", [])
        base_url = servers[0].get("url") if servers else None

        # Extract authentication methods
        auth_methods = []
        security_schemes = schema.get("components", {}).get("securitySchemes", {})
        for scheme_name, scheme in security_schemes.items():
            auth_methods.append({
                "name": scheme_name,
                "type": scheme.get("type", "unknown"),
                "description": scheme.get("description"),
            })

        # Extract resources and operations from paths
        resources_dict = {}
        paths = schema.get("paths", {})

        for path, path_item in paths.items():
            # Extract resource name from path
            resource_name = self._extract_resource_name_from_path(path)

            # Initialize resource if not exists
            if resource_name not in resources_dict:
                resources_dict[resource_name] = {
                    "name": resource_name,
                    "description": None,
                    "endpoint": path,
                    "operations": [],
                }

            # Process each HTTP method
            for method, operation in path_item.items():
                if method.upper() not in ["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"]:
                    continue

                operation_id = operation.get("operationId")
                if not operation_id:
                    continue

                # Extract parameters
                parameters = []
                for param in operation.get("parameters", []):
                    param_name = param.get("name")
                    if not param_name:  # Skip parameters without name
                        continue
                    param_schema = param.get("schema", {})
                    parameters.append(
                        ParameterManifest(
                            name=param_name,
                            type=param_schema.get("type", "string"),
                            required=param.get("required", False),
                            description=param.get("description"),
                            default=param_schema.get("default"),
                            validation_rules={
                                "in": param.get("in"),  # path, query, header, cookie
                                "schema": param_schema,
                            },
                        )
                    )

                # Extract request body parameters if present
                request_body = operation.get("requestBody")
                if request_body:
                    content = request_body.get("content", {})
                    if "application/json" in content:
                        body_schema = content["application/json"].get("schema", {})
                        # For request body, we add it as a special parameter
                        parameters.append(
                            ParameterManifest(
                                name="body",
                                type="object",
                                required=request_body.get("required", False),
                                description=request_body.get("description"),
                                validation_rules={
                                    "in": "body",
                                    "schema": body_schema,
                                },
                            )
                        )

                # Extract request/response schemas
                request_schema = None
                if request_body:
                    content = request_body.get("content", {})
                    if "application/json" in content:
                        request_schema = content["application/json"].get("schema")
                        # Resolve schema references
                        request_schema = self._resolve_schema_reference(schema, request_schema)
                
                response_schema = None
                responses = operation.get("responses", {})
                # Try 201, 200, or first success response
                for status_code in ["201", "200", "default"]:
                    if status_code in responses:
                        response = responses[status_code]
                        content = response.get("content", {})
                        if "application/json" in content:
                            response_schema = content["application/json"].get("schema")
                            # Resolve schema references
                            response_schema = self._resolve_schema_reference(schema, response_schema)
                            break

                # Create operation manifest
                operation_manifest = OperationManifest(
                    name=operation_id,
                    description=operation.get("description") or operation.get("summary"),
                    parameters=parameters,
                    return_type="Any",  # Could extract from responses
                    return_description=None,
                    request_schema=request_schema,
                    response_schema=response_schema,
                    validation_rules={
                        "method": method.upper(),
                        "path": path,
                        "request_body": request_body,
                        "responses": operation.get("responses", {}),
                    },
                )

                resources_dict[resource_name]["operations"].append(operation_manifest)

        # Convert to ResourceManifest list
        resources = [
            ResourceManifest(
                name=resource_data["name"],
                description=resource_data["description"],
                endpoint=resource_data["endpoint"],
                operations=resource_data["operations"],
            )
            for resource_data in resources_dict.values()
        ]

        return ServiceManifest(
            name=service_name,
            version=version,
            description=description,
            base_url=base_url,
            authentication_methods=auth_methods,
            resources=resources,
        )

    def _extract_resource_name_from_path(self, path: str) -> str:
        """
        Extract resource name from OpenAPI path.

        Args:
            path: OpenAPI path (e.g., "/accounts/{account_id}/expenses")

        Returns:
            str: Resource name (e.g., "expenses")
        """
        # Remove leading slash and split
        parts = path.strip("/").split("/")
        
        # Remove path parameters (e.g., {account_id})
        parts = [p for p in parts if not p.startswith("{") and not p.endswith("}")]
        
        # Use last part as resource name, or "root" if empty
        if parts:
            resource_name = parts[-1]
            # Remove common suffixes
            if resource_name.endswith(".json"):
                resource_name = resource_name[:-5]
            return resource_name
        
        return "root"

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


