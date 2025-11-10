"""
OpenAPI Translator implementation.

Translates OpenAPI schemas into Service/Resource/Operation structure.
"""

import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Type, Union

from ....core.openapi_translator.base_translator import BaseTranslator
from ....core.resource import BaseResource
from ....core.service import BaseService
from ....core.strategies.auth.base_auth import BaseAuthStrategy
from .service import OpenAPIService
from .resource import OpenAPIResource


class OpenAPITranslator(BaseTranslator):
    """
    OpenAPI Translator implementation.
    
    Translates OpenAPI 3.0 schemas into Service/Resource/Operation structure.
    """

    def __init__(self):
        """Initialize OpenAPI translator."""
        pass

    def translate(
        self, schema: Union[Dict[str, Any], Path, str]
    ) -> Dict[str, Any]:
        """
        Translate OpenAPI schema into Service/Resource/Operation structure.
        
        Args:
            schema: OpenAPI schema (dict, file path, or schema name)
            
        Returns:
            Dict containing:
                - service: Service configuration dict
                - resources: List of Resource configuration dicts
                - operations: List of Operation configuration dicts
        """
        # Load schema
        schema_dict = self.load_schema(schema)
        
        # Generate components
        service = self.generate_service(schema_dict)
        resources = self.generate_resources(schema_dict)
        operations = self.generate_operations(schema_dict)
        
        return {
            "service": service,
            "resources": resources,
            "operations": operations,
        }

    def generate_service(
        self, schema: Dict[str, Any]
    ) -> Union[Type[BaseService], Dict[str, Any]]:
        """
        Generate Service from OpenAPI schema.
        
        Maps:
        - OpenAPI `servers` → Service `base_url` (with variable support)
        - OpenAPI `security` → Service `auth_strategy`
        - OpenAPI `info` → Service metadata
        
        Args:
            schema: OpenAPI schema dictionary
            
        Returns:
            Service class (OpenAPIService) or configuration dict
        """
        # Extract info for service name
        info = schema.get("info", {})
        service_name = info.get("title", "unknown_service").lower().replace(" ", "_")
        description = info.get("description")
        version = info.get("version", "1.0.0")
        
        # Create a dynamic service class that uses OpenAPIService
        # The service will be instantiated with app_name pointing to the schema
        return {
            "name": service_name,
            "class": OpenAPIService,
            "app_name": service_name,  # Schema name for OpenAPIClient
            "description": description,
            "version": version,
        }

    def generate_resources(
        self, schema: Dict[str, Any]
    ) -> List[Union[Type[BaseResource], Dict[str, Any]]]:
        """
        Generate Resources from OpenAPI schema.
        
        Maps:
        - OpenAPI `paths` → Resources (endpoint with variable support)
        
        Args:
            schema: OpenAPI schema dictionary
            
        Returns:
            List of Resource configuration dicts
        """
        resources = []
        paths = schema.get("paths", {})
        
        # Group paths by resource (e.g., /accounts/{slug}/subjects -> subjects resource)
        resource_paths = {}
        
        for path, path_item in paths.items():
            # Extract resource name from path
            resource_name = self._extract_resource_name(path)
            
            if resource_name not in resource_paths:
                resource_paths[resource_name] = []
            
            resource_paths[resource_name].append({
                "path": path,
                "path_item": path_item,
            })
        
        # Create resource configurations
        for resource_name, path_items in resource_paths.items():
            # Use the first path as the base endpoint
            base_path = path_items[0]["path"]
            
            # Extract variables from path
            vars_dict = {}
            var_pattern = r"\{(\w+)\}"
            variables = re.findall(var_pattern, base_path)
            for var in variables:
                vars_dict[var] = None  # Will be provided at runtime
            
            # Extract endpoint (remove variables for base endpoint)
            endpoint = base_path
            for var in variables:
                endpoint = endpoint.replace(f"{{{var}}}", "")
            
            resource_config = {
                "name": resource_name,
                "class": OpenAPIResource,
                "endpoint": endpoint,
                "vars": vars_dict,
                "paths": [item["path"] for item in path_items],
            }
            
            resources.append(resource_config)
        
        return resources

    def generate_operations(
        self, schema: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Generate Operations from OpenAPI schema.
        
        Maps:
        - OpenAPI `operations` (GET, POST, etc.) → Operations (method, path with variables, parameters)
        
        Args:
            schema: OpenAPI schema dictionary
            
        Returns:
            List of Operation configuration dicts
        """
        operations = []
        paths = schema.get("paths", {})
        
        for path, path_item in paths.items():
            # Extract resource name
            resource_name = self._extract_resource_name(path)
            
            # Process each HTTP method
            for method, operation in path_item.items():
                if method.upper() not in ["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"]:
                    continue
                
                operation_id = operation.get("operationId")
                if not operation_id:
                    continue
                
                # Extract parameters
                parameters = self._extract_parameters(operation, path_item)
                
                # Extract request body
                request_body = operation.get("requestBody")
                
                # Extract responses
                responses = operation.get("responses", {})
                
                # Extract path variables
                vars_dict = {}
                var_pattern = r"\{(\w+)\}"
                variables = re.findall(var_pattern, path)
                for var in variables:
                    vars_dict[var] = None  # Will be provided at runtime
                
                operation_config = {
                    "operation_id": operation_id,
                    "resource_name": resource_name,
                    "method": method.upper(),
                    "path": path,
                    "vars": vars_dict,
                    "parameters": parameters,
                    "request_body": request_body,
                    "responses": responses,
                    "description": operation.get("description"),
                    "summary": operation.get("summary"),
                }
                
                operations.append(operation_config)
        
        return operations

    def _extract_auth_strategy(
        self, schema: Dict[str, Any]
    ) -> Optional[BaseAuthStrategy]:
        """
        Extract authentication strategy from OpenAPI security schemes.
        
        Args:
            schema: OpenAPI schema dictionary
            
        Returns:
            Auth strategy instance or None
        """
        security_schemes = schema.get("components", {}).get("securitySchemes", {})
        security = schema.get("security", [])
        
        if not security_schemes or not security:
            return None
        
        # Get the first security scheme
        security_requirement = security[0] if security else {}
        
        for scheme_name, _ in security_requirement.items():
            scheme = security_schemes.get(scheme_name)
            if not scheme:
                continue
            
            scheme_type = scheme.get("type")
            
            if scheme_type == "oauth2":
                # OAuth2 authentication
                flows = scheme.get("flows", {})
                client_creds = flows.get("clientCredentials", {})
                token_url = client_creds.get("tokenUrl")
                
                # Return OAuth2Auth config (will be instantiated with credentials later)
                return {
                    "type": "oauth2",
                    "token_url": token_url,
                    "scheme": scheme,
                }
            
            elif scheme_type == "http":
                scheme_name_http = scheme.get("scheme", "").lower()
                if scheme_name_http == "bearer":
                    # Bearer token authentication
                    return {
                        "type": "bearer",
                        "scheme": scheme,
                    }
                elif scheme_name_http == "basic":
                    # Basic authentication
                    return {
                        "type": "basic",
                        "scheme": scheme,
                    }
            
            elif scheme_type == "apiKey":
                # API Key authentication
                return {
                    "type": "apiKey",
                    "name": scheme.get("name"),
                    "in": scheme.get("in"),
                    "scheme": scheme,
                }
        
        return None

    def _extract_resource_name(self, path: str) -> str:
        """
        Extract resource name from OpenAPI path.
        
        Examples:
        - /accounts/{slug}/subjects -> subjects
        - /accounts/{slug}/invoices -> invoices
        - /user.json -> user
        
        Args:
            path: OpenAPI path string
            
        Returns:
            Resource name
        """
        # Remove leading/trailing slashes
        path = path.strip("/")
        
        # Remove file extensions
        path = path.replace(".json", "").replace(".yaml", "").replace(".yml", "")
        
        # Split by slashes
        parts = path.split("/")
        
        # Find the last meaningful part (not a variable)
        for part in reversed(parts):
            if part and not part.startswith("{") and not part.endswith("}"):
                # Convert to snake_case
                resource_name = part.replace("-", "_").lower()
                return resource_name
        
        # Fallback: use the last part
        if parts:
            return parts[-1].replace("-", "_").lower()
        
        return "unknown_resource"

    def _extract_parameters(
        self, operation: Dict[str, Any], path_item: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Extract parameters from OpenAPI operation.
        
        Args:
            operation: OpenAPI operation dictionary
            path_item: OpenAPI path item dictionary (for shared parameters)
            
        Returns:
            List of parameter dictionaries
        """
        parameters = []
        
        # Get parameters from operation and path_item
        op_params = operation.get("parameters", [])
        path_params = path_item.get("parameters", [])
        
        # Combine and deduplicate
        all_params = {}
        for param in path_params + op_params:
            param_name = param.get("name")
            if param_name:
                all_params[param_name] = param
        
        # Convert to parameter manifests
        for param_name, param in all_params.items():
            param_schema = param.get("schema", {})
            
            param_config = {
                "name": param_name,
                "in": param.get("in", "query"),  # path, query, header, cookie
                "required": param.get("required", False),
                "description": param.get("description"),
                "type": param_schema.get("type", "string"),
                "default": param_schema.get("default"),
                "enum": param_schema.get("enum"),
                "format": param_schema.get("format"),
                "schema": param_schema,
            }
            
            parameters.append(param_config)
        
        return parameters

