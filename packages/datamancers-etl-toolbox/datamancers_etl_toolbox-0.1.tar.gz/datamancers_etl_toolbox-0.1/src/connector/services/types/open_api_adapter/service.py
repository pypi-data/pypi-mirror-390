"""
OpenAPI Service implementation.

Service class that uses OpenAPIClient for API calls.
"""

from typing import Any, Dict, Optional

from ....core.service import BaseService
from .openapi_client import OpenAPIClient


class OpenAPIService(BaseService):
    """
    Service implementation for OpenAPI-based APIs.
    
    Uses OpenAPIClient for making API calls.
    """

    def __init__(
        self,
        app_name: str,
        auth: Optional[Dict[str, Any]] = None,
        server_index: int = 0,
        base_url: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize OpenAPI service.
        
        Args:
            app_name: OpenAPI schema name (e.g., "fakturoid")
            auth: Authentication credentials dict
            server_index: Index of server to use from servers array
            base_url: Optional base URL override
            **kwargs: Additional service configuration
        """
        # Initialize OpenAPI client first to get base_url
        self.openapi_client = OpenAPIClient(
            app_name=app_name,
            auth=auth or {},
            server_index=server_index,
            base_url=base_url,
        )
        
        # Use base_url from OpenAPI client
        actual_base_url = base_url or self.openapi_client.base_url
        
        # Initialize base service
        super().__init__(
            base_url=actual_base_url,
            **kwargs
        )
        
        self.app_name = app_name
        self.auth = auth or {}

    def call_operation(
        self,
        operation_id: str,
        pagination_strategy: Optional[Any] = None,
        **kwargs
    ) -> Any:
        """
        Call an API operation by operationId.
        
        Args:
            operation_id: OpenAPI operationId
            pagination_strategy: Pagination strategy (None, False, or dict)
            **kwargs: Operation parameters
            
        Returns:
            Operation result (Response or list of items)
        """
        return self.openapi_client.call(
            operation_id,
            pagination_strategy=pagination_strategy,
            **kwargs
        )

    def close(self):
        """Close the service and cleanup resources."""
        if hasattr(self, "openapi_client"):
            self.openapi_client.session.close()
        super().close()

