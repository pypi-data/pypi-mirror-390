"""
Auto-discovery mechanism for services and resources.
"""

import importlib
from pathlib import Path
from typing import Dict, List, Optional, Type

from .service_registry import ServiceRegistry
from ..service import BaseService
from ..resource import BaseResource


class AutoDiscoveryRegistry(ServiceRegistry):
    """
    Service registry with auto-discovery capability.
    
    Automatically discovers and registers services and resources from
    a specified directory.
    """

    def __init__(self, base_path: Optional[str] = None, package_name: str = "connector.services"):
        """
        Initialize auto-discovery registry.

        Args:
            base_path: Base path to scan for services (defaults to src/connector/services)
            package_name: Python package name for services (defaults to "connector.services")
        """
        super().__init__()
        self.base_path = base_path
        self.package_name = package_name
        self._discover_services()

    def _discover_services(self):
        """Automatically discover all services and resources."""
        if not self.base_path:
            # Default to src/connector/services
            import os
            current_dir = Path(__file__).parent.parent.parent
            self.base_path = str(current_dir / "services")

        services_path = Path(self.base_path)
        if not services_path.exists():
            return

        for service_file in self._scan_service_files(services_path):
            try:
                service_name = service_file.stem
                service_module = self._load_service_module(service_name)
                
                # Load service class
                service_class = self._get_service_class(service_module, service_name)
                if service_class:
                    self.register_service(service_name, service_class)
                
                # Load all resource classes
                resource_classes = self._get_resource_classes(service_module, service_name)
                for resource_name, resource_class in resource_classes.items():
                    self.register_resource(service_name, resource_name, resource_class)
            except Exception as e:
                # Log error but continue discovery
                print(f"Warning: Failed to discover service from {service_file}: {e}")

    def _scan_service_files(self, services_path: Path) -> List[Path]:
        """
        Scan directory for service files.

        Args:
            services_path: Path to services directory

        Returns:
            List[Path]: List of service file paths
        """
        service_files = []
        for file_path in services_path.iterdir():
            if (
                file_path.is_file()
                and file_path.suffix == ".py"
                and not file_path.name.startswith("_")
                and file_path.name != "__init__.py"
            ):
                service_files.append(file_path)
        return service_files

    def _load_service_module(self, service_name: str):
        """
        Load service module.

        Args:
            service_name: Service name (file name without .py)

        Returns:
            Module: Loaded module
        """
        module_name = f"{self.package_name}.{service_name}"
        return importlib.import_module(module_name)

    def _get_service_class(self, module, service_name: str) -> Optional[Type[BaseService]]:
        """
        Get service class from module.

        Args:
            module: Service module
            service_name: Service name

        Returns:
            Optional[Type[BaseService]]: Service class or None
        """
        # Try common naming patterns
        class_names = [
            f"{service_name.capitalize()}Service",
            f"{service_name.title().replace('_', '')}Service",
            "Service",
        ]

        for class_name in class_names:
            if hasattr(module, class_name):
                service_class = getattr(module, class_name)
                if (
                    isinstance(service_class, type)
                    and issubclass(service_class, BaseService)
                ):
                    return service_class

        # Search for any class that is a subclass of BaseService
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if (
                isinstance(attr, type)
                and issubclass(attr, BaseService)
                and attr != BaseService
            ):
                return attr

        return None

    def _get_resource_classes(
        self, module, service_name: str
    ) -> Dict[str, Type[BaseResource]]:
        """
        Get all resource classes from module.

        Args:
            module: Service module
            service_name: Service name

        Returns:
            Dict[str, Type[BaseResource]]: Dictionary of resource_name -> resource_class
        """
        resource_classes = {}

        # Search for classes ending with "Resource"
        for attr_name in dir(module):
            if attr_name.endswith("Resource") and not attr_name.startswith("_"):
                resource_class = getattr(module, attr_name)
                if (
                    isinstance(resource_class, type)
                    and issubclass(resource_class, BaseResource)
                    and resource_class != BaseResource
                ):
                    # Extract resource name (remove "Resource" suffix)
                    resource_name = attr_name.replace("Resource", "").lower()
                    resource_classes[resource_name] = resource_class

        return resource_classes


