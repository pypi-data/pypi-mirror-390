"""
Run configuration orchestrator for validating and executing configurations.
"""

from typing import Any, Dict, List, Optional

from .registry.service_registry import ServiceRegistry
from .service import BaseService
from .resource import BaseResource
from ..services.types.rest_api.exceptions import ValidationError, APIError


class RunConfiguration:
    """
    Run configuration orchestrator.

    Validates JSON configurations against available services and resources,
    and executes resource.run() methods.
    """

    def __init__(self, registry: ServiceRegistry):
        """
        Initialize run configuration.

        Args:
            registry: Service registry instance
        """
        if not registry:
            raise ValueError("registry is required")
        self.registry = registry

    def validate_config(self, config: Dict[str, Any]) -> bool:
        """
        Validate JSON configuration.

        Args:
            config: Configuration dictionary

        Returns:
            bool: True if configuration is valid

        Raises:
            ValidationError: If configuration is invalid
        """
        # Validate structure
        if not isinstance(config, dict):
            raise ValidationError("Configuration must be a dictionary")

        # Validate required fields
        if "service" not in config:
            raise ValidationError(
                "Configuration must contain 'service' field. "
                "Operation IDs are unique within a service, not globally."
            )

        service_name = config["service"]

        # Resource is optional if operation_id is provided
        if "resource" not in config:
            # Check if we can auto-detect resource from operation_id
            operation_id = config.get("operation_id") or config.get(
                "parameters", {}
            ).get("operation_id")
            if not operation_id:
                raise ValidationError(
                    "Configuration must contain 'resource' field or 'operation_id' "
                    "to auto-detect resource."
                )
            # Try to find resource from operation_id
            operation_info = self.registry.get_operation_info(
                operation_id, service_name
            )
            if operation_info:
                config["resource"] = operation_info["resource_name"]
                # Set endpoint if not provided
                if not config.get("resource_config", {}).get(
                    "endpoint"
                ) and operation_info.get("endpoint"):
                    if "resource_config" not in config:
                        config["resource_config"] = {}
                    config["resource_config"]["endpoint"] = operation_info["endpoint"]
            else:
                raise ValidationError(
                    f"Operation '{operation_id}' not found in service '{service_name}'. "
                    "Please provide 'resource' explicitly."
                )

        resource_name = config["resource"]

        # Validate service exists
        if not self.validate_service(service_name):
            raise ValidationError(f"Service '{service_name}' not found")

        # Validate resource exists
        if not self.validate_resource(service_name, resource_name):
            raise ValidationError(
                f"Resource '{resource_name}' not found in service '{service_name}'"
            )

        # Validate parameters if provided
        if "parameters" in config:
            self.validate_parameters(service_name, resource_name, config["parameters"])

        return True

    def validate_service(self, service_name: str) -> bool:
        """
        Validate that service exists.

        Args:
            service_name: Service name

        Returns:
            bool: True if service exists
        """
        return self.registry.has_service(service_name)

    def validate_resource(self, service_name: str, resource_name: str) -> bool:
        """
        Validate that resource exists for service.

        Args:
            service_name: Service name
            resource_name: Resource name

        Returns:
            bool: True if resource exists
        """
        return self.registry.has_resource(service_name, resource_name)

    def validate_parameters(
        self, service_name: str, resource_name: str, parameters: Dict[str, Any]
    ) -> bool:
        """
        Validate parameters for resource operation.

        Args:
            service_name: Service name
            resource_name: Resource name
            parameters: Parameters dictionary

        Returns:
            bool: True if parameters are valid

        Raises:
            ValidationError: If parameters are invalid
        """
        # Basic validation - check that parameters is a dict
        if not isinstance(parameters, dict):
            raise ValidationError("Parameters must be a dictionary")

        # TODO: More sophisticated validation could be added here
        # For example, checking against manifest schemas

        return True

    def execute_run(self, config: Dict[str, Any]) -> Any:
        """
        Execute configured run.

        Args:
            config: Configuration dictionary with:
                - service: Service name (required)
                - resource: Resource name (optional if operation_id is provided)
                - operation_id: Operation ID (if provided with service, resource is auto-detected)
                - service_config: Optional service configuration (app_name, auth, etc.)
                - resource_config: Optional resource configuration (endpoint, etc.)
                - parameters: Operation parameters (required, must include operation_id if not in config root)

        Returns:
            Any: Operation result

        Raises:
            ValidationError: If configuration is invalid
            APIError: If execution fails
        """
        # Auto-detect resource from operation_id if service is provided but resource is not
        operation_id = config.get("operation_id")
        parameters = config.get("parameters", {})
        service_name = config.get("service")

        # If operation_id is in config root, add it to parameters
        if operation_id and "operation_id" not in parameters:
            if "parameters" not in config:
                config["parameters"] = {}
            config["parameters"]["operation_id"] = operation_id

        # Also check parameters for operation_id if not in root
        if not operation_id and "operation_id" in parameters:
            operation_id = parameters["operation_id"]

        # If we have operation_id and service, but not resource, try to find resource
        if operation_id and service_name and not config.get("resource"):
            # Try to find resource from operation_id within the service
            operation_info = self.registry.get_operation_info(
                operation_id, service_name
            )
            if operation_info:
                config["resource"] = operation_info["resource_name"]
                # Set endpoint if not provided
                if not config.get("resource_config", {}).get(
                    "endpoint"
                ) and operation_info.get("endpoint"):
                    if "resource_config" not in config:
                        config["resource_config"] = {}
                    config["resource_config"]["endpoint"] = operation_info["endpoint"]
            else:
                raise ValidationError(
                    f"Operation '{operation_id}' not found in service '{service_name}'. "
                    "Please provide 'resource' explicitly."
                )

        # Validate configuration first
        self.validate_config(config)

        service_name = config["service"]
        resource_name = config["resource"]
        service_config = config.get("service_config", {})
        resource_config = config.get("resource_config", {})
        parameters = config.get("parameters", {})

        try:
            # Get service and resource classes
            service_class = self.registry.get_service(service_name)
            resource_class = self.registry.get_resource(service_name, resource_name)

            # Create service instance with config
            service_instance = service_class(**service_config)

            # Create resource instance with config
            # OpenAPIResource requires endpoint as positional argument
            if "endpoint" in resource_config:
                endpoint = resource_config.pop("endpoint")
                resource_instance = resource_class(
                    service=service_instance, endpoint=endpoint, **resource_config
                )
            else:
                # Try to get endpoint from operation_info if available
                operation_id = config.get("operation_id") or config.get(
                    "parameters", {}
                ).get("operation_id")
                if operation_id:
                    operation_info = self.registry.get_operation_info(
                        operation_id, service_name
                    )
                    if operation_info and operation_info.get("endpoint"):
                        resource_instance = resource_class(
                            service=service_instance,
                            endpoint=operation_info["endpoint"],
                            **resource_config,
                        )
                    else:
                        # Fallback: try to create without endpoint (may fail)
                        resource_instance = resource_class(
                            service=service_instance, **resource_config
                        )
                else:
                    # Fallback: try to create without endpoint (may fail)
                    resource_instance = resource_class(
                        service=service_instance, **resource_config
                    )

            # Execute run() method
            return resource_instance.run(parameters)

        except ValueError as e:
            raise ValidationError(f"Configuration error: {e}")
        except Exception as e:
            raise APIError(f"Execution failed: {e}")

    def get_available_services(self) -> List[str]:
        """
        Get list of available services.

        Returns:
            List[str]: List of service names
        """
        return self.registry.list_services()

    def get_available_resources(self, service_name: str) -> List[str]:
        """
        Get list of available resources for a service.

        Args:
            service_name: Service name

        Returns:
            List[str]: List of resource names

        Raises:
            ValidationError: If service not found
        """
        if not self.validate_service(service_name):
            raise ValidationError(f"Service '{service_name}' not found")
        return self.registry.list_resources(service_name)
