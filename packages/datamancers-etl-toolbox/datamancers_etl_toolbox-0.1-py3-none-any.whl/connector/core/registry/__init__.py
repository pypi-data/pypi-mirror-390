"""
Service registry system for service and resource discovery.
"""

from .service_registry import ServiceRegistry
from .auto_discovery import AutoDiscoveryRegistry

__all__ = ["ServiceRegistry", "AutoDiscoveryRegistry"]


