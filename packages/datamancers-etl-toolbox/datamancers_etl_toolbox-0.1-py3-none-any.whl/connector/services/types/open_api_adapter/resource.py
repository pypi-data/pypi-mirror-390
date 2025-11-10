"""
OpenAPI Resource implementation.

Resource class that uses OpenAPIService for API calls.
"""

from typing import Any, Dict, List, Optional

from ....core.resource import BaseResource
from .service import OpenAPIService


class OpenAPIResource(BaseResource):
    """
    Resource implementation for OpenAPI-based APIs.
    
    Uses OpenAPIService for making API calls.
    """

    def __init__(
        self,
        service: OpenAPIService,
        endpoint: str,
        operation_id: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize OpenAPI resource.
        
        Args:
            service: OpenAPIService instance
            endpoint: Resource endpoint path
            operation_id: Optional default operation ID for this resource
            **kwargs: Additional resource configuration
        """
        super().__init__(service, endpoint, **kwargs)
        self.operation_id = operation_id

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
        return self.service.call_operation(
            operation_id,
            pagination_strategy=pagination_strategy,
            **kwargs
        )

    def run(self, parameters: Dict[str, Any]) -> Any:
        """
        Execute configured operation.
        
        Args:
            parameters: Operation parameters including:
                - operation_id: OpenAPI operationId (required)
                - pagination_strategy: Optional pagination strategy
                - Other operation-specific parameters
                
        Returns:
            Operation result
        """
        operation_id = parameters.pop("operation_id", self.operation_id)
        if not operation_id:
            raise ValueError("operation_id is required in parameters")
        
        pagination_strategy = parameters.pop("pagination_strategy", None)
        
        return self.call_operation(
            operation_id,
            pagination_strategy=pagination_strategy,
            **parameters
        )

