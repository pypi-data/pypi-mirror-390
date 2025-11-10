"""
OpenAPI Translator module.

Provides translation from OpenAPI schemas to Service/Resource/Operation structure.
"""

from .base_translator import BaseTranslator
from .registry_integration import RegistryIntegration

__all__ = ["BaseTranslator", "RegistryIntegration"]

