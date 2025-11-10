"""
Offset-based pagination strategy.
"""

from typing import Any, Dict, Optional

from .base_pagination import BasePaginationStrategy


class OffsetPagination(BasePaginationStrategy):
    """
    Offset-based pagination strategy.
    
    Uses offset and limit parameters for pagination.
    """

    def __init__(
        self,
        limit: int = 100,
        offset: int = 0,
        limit_param: str = "limit",
        offset_param: str = "offset",
    ):
        """
        Initialize offset pagination strategy.

        Args:
            limit: Number of items per page
            offset: Starting offset
            limit_param: Query parameter name for limit
            offset_param: Query parameter name for offset
        """
        if limit < 1:
            raise ValueError("limit must be at least 1")
        if offset < 0:
            raise ValueError("offset must be non-negative")

        self.limit = limit
        self.offset = offset
        self.limit_param = limit_param
        self.offset_param = offset_param

    def decorate_request(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Decorate request parameters with offset pagination.

        Args:
            params: Request parameters

        Returns:
            Dict[str, Any]: Parameters with pagination added
        """
        # Don't override if already set
        if self.limit_param not in params:
            params[self.limit_param] = self.limit
        if self.offset_param not in params:
            params[self.offset_param] = self.offset

        return params

    def extract_data(self, response_data: Any) -> list:
        """
        Extract paginated data from response.

        Args:
            response_data: Response data

        Returns:
            list: List of items from response
        """
        return super().extract_data(response_data)

    def extract_next_page(self, response_data: Any) -> Optional[Dict[str, Any]]:
        """
        Extract next page information from response.

        Args:
            response_data: Response data

        Returns:
            Optional[Dict[str, Any]]: Next page parameters with updated offset
        """
        data = self.extract_data(response_data)
        if len(data) >= self.limit:
            return {
                self.limit_param: self.limit,
                self.offset_param: self.offset + self.limit,
            }
        return None

    def has_more_pages(self, response_data: Any) -> bool:
        """
        Check if there are more pages available.

        Args:
            response_data: Response data

        Returns:
            bool: True if more pages are available
        """
        data = self.extract_data(response_data)
        return len(data) >= self.limit

    def next_page(self):
        """Move to next page."""
        self.offset += self.limit

    def reset(self):
        """Reset pagination to first page."""
        self.offset = 0


