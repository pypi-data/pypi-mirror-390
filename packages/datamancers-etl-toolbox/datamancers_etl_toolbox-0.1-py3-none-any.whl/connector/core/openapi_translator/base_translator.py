"""
Base translator abstract class for all translator implementations.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional, Type, Union

from ..service import BaseService
from ..resource import BaseResource


class BaseTranslator(ABC):
    """
    Base abstract class for all translator implementations.
    
    Translators convert external schema formats (OpenAPI, GraphQL, etc.)
    into the internal Service/Resource/Operation structure.
    """

    @abstractmethod
    def translate(
        self, schema: Union[Dict[str, Any], Path, str]
    ) -> Dict[str, Any]:
        """
        Translate schema into Service/Resource/Operation structure.
        
        Args:
            schema: Schema to translate (dict, file path, or schema name)
            
        Returns:
            Dict containing:
                - service: Service class or configuration
                - resources: List of Resource classes or configurations
                - operations: List of Operation classes or configurations
        """
        pass

    @abstractmethod
    def generate_service(
        self, schema: Dict[str, Any]
    ) -> Union[Type[BaseService], Dict[str, Any]]:
        """
        Generate Service from schema.
        
        Args:
            schema: Schema dictionary
            
        Returns:
            Service class or configuration dict
        """
        pass

    @abstractmethod
    def generate_resources(
        self, schema: Dict[str, Any]
    ) -> List[Union[Type[BaseResource], Dict[str, Any]]]:
        """
        Generate Resources from schema.
        
        Args:
            schema: Schema dictionary
            
        Returns:
            List of Resource classes or configuration dicts
        """
        pass

    @abstractmethod
    def generate_operations(
        self, schema: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Generate Operations from schema.
        
        Args:
            schema: Schema dictionary
            
        Returns:
            List of Operation configurations
        """
        pass

    def load_schema(self, schema: Union[Dict[str, Any], Path, str]) -> Dict[str, Any]:
        """
        Load schema from various sources.
        
        Args:
            schema: Schema (dict, file path, or schema name)
            
        Returns:
            Schema dictionary
            
        Raises:
            ValueError: If schema cannot be loaded
        """
        if isinstance(schema, dict):
            return schema
        
        if isinstance(schema, (str, Path)):
            path = Path(schema)
            if not path.exists():
                # Try to find in schemas directory
                from ...services.types.open_api_adapter.openapi_client import OpenAPIClient
                try:
                    # Try to load using OpenAPIClient's schema loading logic
                    client = OpenAPIClient(app_name=str(path.stem) if path.suffix else schema)
                    return client.schema
                except Exception:
                    raise ValueError(f"Schema file not found: {path}")
            
            # Load from file
            import json
            import yaml
            
            content = path.read_text()
            if path.suffix in (".json",):
                return json.loads(content)
            elif path.suffix in (".yaml", ".yml"):
                return yaml.safe_load(content)
            else:
                raise ValueError(f"Unsupported schema format: {path.suffix}")
        
        raise ValueError(f"Unsupported schema type: {type(schema)}")

