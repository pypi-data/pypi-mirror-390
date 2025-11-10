"""
Registry integration for automatic registration of translated services/resources/operations.
"""

from typing import Any, Dict, List, Optional, Type

from ..registry.service_registry import ServiceRegistry
from ..service import BaseService
from ..resource import BaseResource


class RegistryIntegration:
    """
    Integration layer for registering translated services/resources/operations
    into the ServiceRegistry.
    """

    def __init__(self, registry: Optional[ServiceRegistry] = None):
        """
        Initialize registry integration.

        Args:
            registry: ServiceRegistry instance (creates new one if not provided)
        """
        self.registry = registry or ServiceRegistry()

    def register_from_translator(
        self, translator: Any, schema: Any, service_name: Optional[str] = None
    ) -> str:
        """
        Register services/resources/operations from translator.

        Args:
            translator: Translator instance (must have translate() method)
            schema: Schema to translate
            service_name: Optional service name (auto-generated if not provided)

        Returns:
            str: Registered service name
        """
        # Translate schema
        translated = translator.translate(schema)

        # Extract service name
        if not service_name:
            service_name = self._extract_service_name(translated, schema)

        # Register service
        service = translated.get("service")
        if isinstance(service, type) and issubclass(service, BaseService):
            self.registry.register_service(service_name, service)
        elif isinstance(service, dict):
            # Service config contains class and app_name
            service_class = service.get("class")
            if service_class and issubclass(service_class, BaseService):
                # Create a factory function that creates service instances
                # For now, we'll register the class directly
                # The app_name will be passed when instantiating
                self.registry.register_service(service_name, service_class)
            else:
                # Create service class dynamically
                service_class = self._create_service_class(service_name, service)
                self.registry.register_service(service_name, service_class)

        # Register resources
        resources = translated.get("resources", [])
        operations = translated.get("operations", [])

        # Create operation_id -> resource mapping
        operation_to_resource = {}
        for operation_config in operations:
            operation_id = operation_config.get("operation_id") or operation_config.get(
                "name"
            )
            op_resource_name = operation_config.get("resource_name")
            if operation_id and op_resource_name:
                operation_to_resource[operation_id] = op_resource_name

        for resource_config in resources:
            resource_name = resource_config.get("name") or self._extract_resource_name(
                resource_config
            )
            resource_class = resource_config.get("class")
            endpoint = resource_config.get("endpoint")

            if resource_class and issubclass(resource_class, BaseResource):
                self.registry.register_resource(
                    service_name, resource_name, resource_class
                )
            elif isinstance(resource_config, dict):
                # Create resource class dynamically
                resource_class = self._create_resource_class(
                    service_name, resource_name, resource_config
                )
                self.registry.register_resource(
                    service_name, resource_name, resource_class
                )

            # Register operations for this resource
            for operation_config in operations:
                operation_id = operation_config.get(
                    "operation_id"
                ) or operation_config.get("name")
                op_resource_name = operation_config.get("resource_name")

                # Match operation to resource
                if operation_id and (
                    op_resource_name == resource_name
                    or (
                        operation_id in operation_to_resource
                        and operation_to_resource[operation_id] == resource_name
                    )
                ):
                    # Use endpoint from resource_config or operation path
                    op_endpoint = endpoint or operation_config.get("path")
                    self.registry.register_operation(
                        service_name,
                        resource_name,
                        operation_id,
                        op_endpoint,
                    )

        return service_name

    def auto_register_services(self, services: List[Dict[str, Any]]):
        """
        Automatically register multiple services.

        Args:
            services: List of service configurations
        """
        for service_config in services:
            service_name = service_config.get("name")
            service_class = service_config.get("class")
            if service_name and service_class:
                self.registry.register_service(service_name, service_class)

    def auto_register_resources(self, resources: List[Dict[str, Any]]):
        """
        Automatically register multiple resources.

        Args:
            resources: List of resource configurations with service_name
        """
        for resource_config in resources:
            service_name = resource_config.get("service_name")
            resource_name = resource_config.get("name")
            resource_class = resource_config.get("class")
            if service_name and resource_name and resource_class:
                self.registry.register_resource(
                    service_name, resource_name, resource_class
                )

    def auto_register_operations(self, operations: List[Dict[str, Any]]):
        """
        Automatically register multiple operations.

        Note: Operations are typically registered as part of resources,
        but this method can be used for standalone operation registration.

        Args:
            operations: List of operation configurations
        """
        # Operations are typically part of resources, so this is a placeholder
        # for future operation-level registration if needed
        pass

    def _extract_service_name(self, translated: Dict[str, Any], schema: Any) -> str:
        """Extract service name from translated data or schema."""
        # Try to get from translated data
        service = translated.get("service")
        if isinstance(service, dict):
            return service.get("name", "unknown_service")

        # Try to get from schema
        if isinstance(schema, dict):
            info = schema.get("info", {})
            title = info.get("title", "unknown_service")
            # Normalize service name (lowercase, replace spaces with underscores)
            return title.lower().replace(" ", "_").replace("-", "_")

        return "unknown_service"

    def _extract_resource_name(self, resource_config: Dict[str, Any]) -> str:
        """Extract resource name from resource configuration."""
        return resource_config.get("name", "unknown_resource")

    def _create_service_class(
        self, service_name: str, service_config: Dict[str, Any]
    ) -> Type[BaseService]:
        """Create a service class dynamically from configuration."""
        from ..service import BaseService

        class_name = service_name.replace("_", " ").title().replace(" ", "")

        # Get app_name from config (for OpenAPIService)
        app_name = service_config.get("app_name", service_name)

        class DynamicService(BaseService):
            """Dynamically created service class."""

            def __init__(self, **kwargs):
                # For OpenAPIService, we need app_name
                if "app_name" not in kwargs:
                    kwargs["app_name"] = app_name
                # Merge config with kwargs
                config = {**service_config, **kwargs}
                # Remove class and name from config before passing to super
                config.pop("class", None)
                config.pop("name", None)
                super().__init__(**config)

        DynamicService.__name__ = class_name
        return DynamicService

    def _create_resource_class(
        self,
        service_name: str,
        resource_name: str,
        resource_config: Dict[str, Any],
    ) -> Type[BaseResource]:
        """Create a resource class dynamically from configuration."""
        from ..resource import BaseResource

        class_name = resource_name.replace("_", " ").title().replace(" ", "")

        # Get endpoint from config
        endpoint = resource_config.get("endpoint", f"/{resource_name}")

        class DynamicResource(BaseResource):
            """Dynamically created resource class."""

            def __init__(self, service, **kwargs):
                # Merge config with kwargs
                config = {**resource_config, **kwargs}
                # Remove class and name from config
                config.pop("class", None)
                config.pop("name", None)
                # Get endpoint
                resource_endpoint = config.pop("endpoint", endpoint)
                super().__init__(service, resource_endpoint, **config)

            def run(self, parameters: Dict[str, Any]) -> Any:
                """Execute operation."""
                # Default implementation - would be overridden by specific operations
                operation_id = parameters.get("operation_id")
                if operation_id and hasattr(self.service, "call_operation"):
                    return self.service.call_operation(operation_id, **parameters)
                return self.list(**parameters)

        DynamicResource.__name__ = class_name
        return DynamicResource
