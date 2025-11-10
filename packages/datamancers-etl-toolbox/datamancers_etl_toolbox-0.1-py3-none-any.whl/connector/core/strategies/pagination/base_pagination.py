"""
Base pagination strategy interface.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class BasePaginationStrategy(ABC):
    """
    Base class for pagination strategies.
    
    Pagination strategies handle request pagination parameters and
    extract paginated data from responses.
    """

    @abstractmethod
    def decorate_request(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Decorate request parameters with pagination.

        Args:
            params: Request parameters

        Returns:
            Dict[str, Any]: Parameters with pagination added
        """
        pass

    def extract_data(self, response_data: Any) -> list:
        """
        Extract paginated data from response.

        Args:
            response_data: Response data

        Returns:
            list: List of items from response
        """
        if isinstance(response_data, list):
            return response_data
        elif isinstance(response_data, dict):
            # Common patterns: data, items, results
            for key in ["data", "items", "results"]:
                if key in response_data and isinstance(response_data[key], list):
                    return response_data[key]
            return []
        return []

    def extract_next_page(self, response_data: Any) -> Optional[Dict[str, Any]]:
        """
        Extract next page information from response.

        Args:
            response_data: Response data

        Returns:
            Optional[Dict[str, Any]]: Next page parameters or None
        """
        return None

    def has_more_pages(self, response_data: Any) -> bool:
        """
        Check if there are more pages available.

        Args:
            response_data: Response data

        Returns:
            bool: True if more pages are available
        """
        return False


