"""
Base Resource class for all resource implementations.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from .base_service import BaseService
from ..api_client.exceptions import APIError, ValidationError


class BaseResource(ABC):
    """
    Base class for all resource implementations.
    
    Resources inherit configuration from their parent Service and implement
    CRUD operations and business logic for specific entities.
    """

    def __init__(
        self,
        service: BaseService,
        endpoint: str,
        auth_strategy: Optional[Any] = None,
        retry_strategy: Optional[Any] = None,
        pagination_strategy: Optional[Any] = None,
    ):
        """
        Initialize base resource.

        Args:
            service: Parent service instance
            endpoint: Resource endpoint path (e.g., "/tasks", "/projects")
            auth_strategy: Optional auth strategy override (defaults to service strategy)
            retry_strategy: Optional retry strategy override (defaults to service strategy)
            pagination_strategy: Optional pagination strategy override (defaults to service strategy)
        """
        if not service:
            raise ValidationError("service is required")
        if not endpoint:
            raise ValidationError("endpoint is required")

        self.service = service
        self.endpoint = endpoint.rstrip("/")
        self.auth_strategy = auth_strategy or service.auth_strategy
        self.retry_strategy = retry_strategy or service.retry_strategy
        self.pagination_strategy = pagination_strategy or service.pagination_strategy

    @property
    def full_endpoint(self) -> str:
        """Get full endpoint URL."""
        return f"{self.service.base_url}{self.endpoint}"

    def get_auth_headers(self) -> Dict[str, str]:
        """
        Get authentication headers.

        Returns:
            Dict[str, str]: Authentication headers
        """
        if self.auth_strategy and hasattr(self.auth_strategy, "get_auth_headers"):
            return self.auth_strategy.get_auth_headers()
        return self.service.get_auth_headers()

    def create(self, data: Dict[str, Any], **kwargs) -> Any:
        """
        Create a new resource.

        Args:
            data: Resource data
            **kwargs: Additional parameters

        Returns:
            Any: Created resource data
        """
        headers = self.get_auth_headers()
        response = self.service.http_client.post(
            self.endpoint, json=data, headers=headers, **kwargs
        )
        if not response.is_success:
            raise APIError(
                f"Failed to create resource: {response.error_message}",
                status_code=response.status_code,
            )
        return response.data

    def read(self, resource_id: str, **kwargs) -> Any:
        """
        Read a resource by ID.

        Args:
            resource_id: Resource identifier
            **kwargs: Additional parameters

        Returns:
            Any: Resource data
        """
        headers = self.get_auth_headers()
        url = f"{self.endpoint}/{resource_id}"
        response = self.service.http_client.get(url, headers=headers, **kwargs)
        if not response.is_success:
            raise APIError(
                f"Failed to read resource: {response.error_message}",
                status_code=response.status_code,
            )
        return response.data

    def update(self, resource_id: str, data: Dict[str, Any], **kwargs) -> Any:
        """
        Update a resource.

        Args:
            resource_id: Resource identifier
            data: Updated resource data
            **kwargs: Additional parameters

        Returns:
            Any: Updated resource data
        """
        headers = self.get_auth_headers()
        url = f"{self.endpoint}/{resource_id}"
        response = self.service.http_client.put(
            url, json=data, headers=headers, **kwargs
        )
        if not response.is_success:
            raise APIError(
                f"Failed to update resource: {response.error_message}",
                status_code=response.status_code,
            )
        return response.data

    def delete(self, resource_id: str, **kwargs) -> bool:
        """
        Delete a resource.

        Args:
            resource_id: Resource identifier
            **kwargs: Additional parameters

        Returns:
            bool: True if deletion was successful
        """
        headers = self.get_auth_headers()
        url = f"{self.endpoint}/{resource_id}"
        response = self.service.http_client.delete(url, headers=headers, **kwargs)
        if not response.is_success:
            raise APIError(
                f"Failed to delete resource: {response.error_message}",
                status_code=response.status_code,
            )
        return True

    def list(self, params: Optional[Dict[str, Any]] = None, **kwargs) -> List[Any]:
        """
        List all resources.

        Args:
            params: Query parameters
            **kwargs: Additional parameters

        Returns:
            List[Any]: List of resources
        """
        headers = self.get_auth_headers()

        # Apply pagination strategy if available
        if self.pagination_strategy and hasattr(
            self.pagination_strategy, "decorate_request"
        ):
            if params is None:
                params = {}
            params = self.pagination_strategy.decorate_request(params)

        # Apply retry strategy if available
        if self.retry_strategy and hasattr(
            self.retry_strategy, "execute_with_retry"
        ):

            def _make_request():
                return self.service.http_client.get(
                    self.endpoint, params=params, headers=headers, **kwargs
                )

            response = self.retry_strategy.execute_with_retry(_make_request)
        else:
            response = self.service.http_client.get(
                self.endpoint, params=params, headers=headers, **kwargs
            )

        if not response.is_success:
            raise APIError(
                f"Failed to list resources: {response.error_message}",
                status_code=response.status_code,
            )

        # Extract paginated data if pagination strategy is available
        if self.pagination_strategy and hasattr(
            self.pagination_strategy, "extract_data"
        ):
            return self.pagination_strategy.extract_data(response.data)

        # Default: assume response.data is a list or contains a list
        if isinstance(response.data, list):
            return response.data
        elif isinstance(response.data, dict) and "data" in response.data:
            return response.data["data"]
        elif isinstance(response.data, dict) and "items" in response.data:
            return response.data["items"]
        else:
            return [response.data] if response.data else []

    def extract(self, **kwargs) -> Any:
        """
        Extract data from the resource (ETL operation).

        Args:
            **kwargs: Extraction parameters

        Returns:
            Any: Extracted data
        """
        return self.list(**kwargs)

    def load(self, data: Any, **kwargs) -> Any:
        """
        Load data into the resource (ETL operation).

        Args:
            data: Data to load
            **kwargs: Additional parameters

        Returns:
            Any: Load result
        """
        if isinstance(data, list):
            results = []
            for item in data:
                if isinstance(item, dict) and "id" in item:
                    results.append(self.update(item["id"], item, **kwargs))
                else:
                    results.append(self.create(item, **kwargs))
            return results
        elif isinstance(data, dict):
            if "id" in data:
                return self.update(data["id"], data, **kwargs)
            else:
                return self.create(data, **kwargs)
        else:
            raise ValidationError("load() expects dict or list of dicts")

    @abstractmethod
    def run(self, parameters: Dict[str, Any]) -> Any:
        """
        Execute configured operation (required for RunConfiguration).

        Args:
            parameters: Operation parameters

        Returns:
            Any: Operation result
        """
        pass


