"""
Manifest API for accessing service manifests.
"""

from typing import Any, Dict, List, Optional, Type

from .base import ServiceManifest, ResourceManifest, OperationManifest
from .generator import ManifestGenerator
from ..service import BaseService
from ..resource import BaseResource
from ..registry.service_registry import ServiceRegistry


class ManifestAPI:
    """
    API for accessing service manifests.
    
    Provides methods to get service, resource, and operation manifests
    from services and resources.
    """

    def __init__(self, registry: Optional[ServiceRegistry] = None):
        """
        Initialize manifest API.

        Args:
            registry: Optional service registry (for registry-based access)
        """
        self.registry = registry
        self.generator = ManifestGenerator()
        self._manifest_cache: Dict[str, ServiceManifest] = {}

    def get_service_manifest(
        self, service: BaseService, service_name: Optional[str] = None
    ) -> ServiceManifest:
        """
        Get service manifest from service instance.

        Args:
            service: Service instance
            service_name: Optional service name

        Returns:
            ServiceManifest: Service manifest
        """
        if not service_name:
            service_name = service.__class__.__name__.replace("Service", "").lower()

        # Check cache
        cache_key = f"service:{service_name}"
        if cache_key in self._manifest_cache:
            return self._manifest_cache[cache_key]

        # Generate manifest
        manifest = self.generator.generate_service_manifest(
            service.__class__, service_name
        )

        # Cache manifest
        self._manifest_cache[cache_key] = manifest

        return manifest

    def get_resource_manifest(
        self, resource: BaseResource, resource_name: Optional[str] = None
    ) -> ResourceManifest:
        """
        Get resource manifest from resource instance.

        Args:
            resource: Resource instance
            resource_name: Optional resource name

        Returns:
            ResourceManifest: Resource manifest
        """
        if not resource_name:
            resource_name = resource.__class__.__name__.replace("Resource", "").lower()

        return self.generator.generate_resource_manifest(
            resource.__class__, resource_name
        )

    def get_service_manifest_by_name(self, service_name: str) -> ServiceManifest:
        """
        Get service manifest by service name (requires registry).

        Args:
            service_name: Service name

        Returns:
            ServiceManifest: Service manifest

        Raises:
            ValueError: If registry is not available or service not found
        """
        if not self.registry:
            raise ValueError("Registry is required for get_service_manifest_by_name")

        # Check cache
        cache_key = f"service:{service_name}"
        if cache_key in self._manifest_cache:
            return self._manifest_cache[cache_key]

        # Get service class from registry
        service_class = self.registry.get_service(service_name)

        # Check if it's an OpenAPI service - if so, generate from OpenAPI schema
        from ...services.types.open_api_adapter.service import OpenAPIService
        if issubclass(service_class, OpenAPIService):
            # Try to get OpenAPI schema for this service
            manifest = self._generate_manifest_from_openapi(service_name, service_class)
            if manifest:
                self._manifest_cache[cache_key] = manifest
                return manifest

        # Generate manifest from service class
        manifest = self.generator.generate_service_manifest(service_class, service_name)

        # Cache manifest
        self._manifest_cache[cache_key] = manifest

        return manifest

    def _generate_manifest_from_openapi(
        self, service_name: str, service_class: Type[BaseService]
    ) -> Optional[ServiceManifest]:
        """
        Generate manifest from OpenAPI schema for OpenAPI service.

        Args:
            service_name: Service name
            service_class: Service class

        Returns:
            Optional[ServiceManifest]: Generated manifest or None
        """
        try:
            # Extract app_name from service_name
            app_name = (
                service_name
                .replace("_api_v3", "")
                .replace("_api_v2", "")
                .replace("_api_v1", "")
                .replace("_api", "")
            )

            # Find schema file
            from pathlib import Path
            import os

            schemas_dir = (
                Path(__file__).parent.parent.parent
                / "services"
                / "types"
                / "open_api_adapter"
                / "schemas"
            )
            if not schemas_dir.exists():
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
                return self.generator.generate_manifest_from_openapi_schema(
                    schema_file, service_name
                )
        except Exception:
            pass

        return None

    def get_resource_manifest_by_name(
        self, service_name: str, resource_name: str
    ) -> ResourceManifest:
        """
        Get resource manifest by service and resource name (requires registry).

        Args:
            service_name: Service name
            resource_name: Resource name

        Returns:
            ResourceManifest: Resource manifest

        Raises:
            ValueError: If registry is not available or service/resource not found
        """
        if not self.registry:
            raise ValueError("Registry is required for get_resource_manifest_by_name")

        # Check if it's an OpenAPI service - if so, get from service manifest
        service_class = self.registry.get_service(service_name)
        from ...services.types.open_api_adapter.service import OpenAPIService
        if issubclass(service_class, OpenAPIService):
            # Get service manifest (will be generated from OpenAPI schema)
            service_manifest = self.get_service_manifest_by_name(service_name)
            # Find resource in service manifest
            resource_manifest = service_manifest.get_resource(resource_name)
            if resource_manifest:
                return resource_manifest

        # Get resource class from registry
        resource_class = self.registry.get_resource(service_name, resource_name)

        # Generate manifest
        return self.generator.generate_resource_manifest(resource_class, resource_name)

    def get_operation_manifest(
        self, service_name: str, resource_name: str, operation_name: str
    ) -> Optional[OperationManifest]:
        """
        Get operation manifest by service, resource, and operation name.

        Args:
            service_name: Service name
            resource_name: Resource name
            operation_name: Operation name

        Returns:
            Optional[OperationManifest]: Operation manifest or None
        """
        resource_manifest = self.get_resource_manifest_by_name(
            service_name, resource_name
        )
        return resource_manifest.get_operation(operation_name)

    def list_service_manifests(self) -> List[str]:
        """
        List all available service names (requires registry).

        Returns:
            List[str]: List of service names

        Raises:
            ValueError: If registry is not available
        """
        if not self.registry:
            raise ValueError("Registry is required for list_service_manifests")
        return self.registry.list_services()

    def list_resource_manifests(self, service_name: str) -> List[str]:
        """
        List all available resource names for a service (requires registry).

        Args:
            service_name: Service name

        Returns:
            List[str]: List of resource names

        Raises:
            ValueError: If registry is not available
        """
        if not self.registry:
            raise ValueError("Registry is required for list_resource_manifests")
        return self.registry.list_resources(service_name)

    def clear_cache(self):
        """Clear manifest cache."""
        self._manifest_cache.clear()


