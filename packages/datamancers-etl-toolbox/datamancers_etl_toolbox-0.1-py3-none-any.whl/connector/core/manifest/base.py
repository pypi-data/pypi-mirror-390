"""
Base manifest classes for service metadata.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class ParameterManifest:
    """Manifest for operation parameters."""

    name: str
    type: str
    required: bool = False
    description: Optional[str] = None
    default: Optional[Any] = None
    validation_rules: Dict[str, Any] = field(default_factory=dict)


@dataclass
class OperationManifest:
    """Manifest for resource operations."""

    name: str
    description: Optional[str] = None
    parameters: List[ParameterManifest] = field(default_factory=list)
    return_type: Optional[str] = None
    return_description: Optional[str] = None
    validation_rules: Dict[str, Any] = field(default_factory=dict)
    request_schema: Optional[Dict[str, Any]] = None
    response_schema: Optional[Dict[str, Any]] = None

    def get_parameter(self, name: str) -> Optional[ParameterManifest]:
        """
        Get parameter by name.

        Args:
            name: Parameter name

        Returns:
            Optional[ParameterManifest]: Parameter manifest or None
        """
        for param in self.parameters:
            if param.name == name:
                return param
        return None

    def get_required_parameters(self) -> List[ParameterManifest]:
        """
        Get list of required parameters.

        Returns:
            List[ParameterManifest]: List of required parameters
        """
        return [param for param in self.parameters if param.required]


@dataclass
class ResourceManifest:
    """Manifest for resources."""

    name: str
    description: Optional[str] = None
    operations: List[OperationManifest] = field(default_factory=list)
    endpoint: Optional[str] = None

    def get_operation(self, name: str) -> Optional[OperationManifest]:
        """
        Get operation by name.

        Args:
            name: Operation name

        Returns:
            Optional[OperationManifest]: Operation manifest or None
        """
        for op in self.operations:
            if op.name == name:
                return op
        return None

    def list_operations(self) -> List[str]:
        """
        List all operation names.

        Returns:
            List[str]: List of operation names
        """
        return [op.name for op in self.operations]


@dataclass
class ServiceManifest:
    """Manifest for services."""

    name: str
    version: str = "1.0.0"
    description: Optional[str] = None
    base_url: Optional[str] = None
    authentication_methods: List[Dict[str, Any]] = field(default_factory=list)
    resources: List[ResourceManifest] = field(default_factory=list)

    def get_resource(self, name: str) -> Optional[ResourceManifest]:
        """
        Get resource by name.

        Args:
            name: Resource name

        Returns:
            Optional[ResourceManifest]: Resource manifest or None
        """
        for resource in self.resources:
            if resource.name == name:
                return resource
        return None

    def list_resources(self) -> List[str]:
        """
        List all resource names.

        Returns:
            List[str]: List of resource names
        """
        return [resource.name for resource in self.resources]

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert manifest to dictionary.

        Returns:
            Dict[str, Any]: Manifest as dictionary
        """
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "base_url": self.base_url,
            "authentication_methods": self.authentication_methods,
            "resources": [
                {
                    "name": resource.name,
                    "description": resource.description,
                    "endpoint": resource.endpoint,
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
                                    "default": param.default,
                                    "validation_rules": param.validation_rules,
                                }
                                for param in op.parameters
                            ],
                            "return_type": op.return_type,
                            "return_description": op.return_description,
                            "validation_rules": op.validation_rules,
                        }
                        for op in resource.operations
                    ],
                }
                for resource in self.resources
            ],
        }


