"""
Cursor-based pagination strategy.
"""

from typing import Any, Dict, Optional

from .base_pagination import BasePaginationStrategy


class CursorPagination(BasePaginationStrategy):
    """
    Cursor-based pagination strategy.
    
    Uses cursor/token parameters for pagination.
    """

    def __init__(
        self,
        cursor: Optional[str] = None,
        limit: int = 100,
        cursor_param: str = "cursor",
        limit_param: str = "limit",
        next_cursor_key: str = "next_cursor",
    ):
        """
        Initialize cursor pagination strategy.

        Args:
            cursor: Initial cursor value
            limit: Number of items per page
            cursor_param: Query parameter name for cursor
            limit_param: Query parameter name for limit
            next_cursor_key: Key in response for next cursor
        """
        if limit < 1:
            raise ValueError("limit must be at least 1")

        self.cursor = cursor
        self.limit = limit
        self.cursor_param = cursor_param
        self.limit_param = limit_param
        self.next_cursor_key = next_cursor_key

    def decorate_request(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Decorate request parameters with cursor pagination.

        Args:
            params: Request parameters

        Returns:
            Dict[str, Any]: Parameters with pagination added
        """
        # Don't override if already set
        if self.limit_param not in params:
            params[self.limit_param] = self.limit

        # Only add cursor if we have one
        if self.cursor and self.cursor_param not in params:
            params[self.cursor_param] = self.cursor

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
            Optional[Dict[str, Any]]: Next page parameters with updated cursor
        """
        if isinstance(response_data, dict):
            next_cursor = response_data.get(self.next_cursor_key)
            if next_cursor:
                return {
                    self.limit_param: self.limit,
                    self.cursor_param: next_cursor,
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
        if isinstance(response_data, dict):
            next_cursor = response_data.get(self.next_cursor_key)
            return bool(next_cursor)
        return False

    def set_cursor(self, cursor: Optional[str]):
        """Set cursor value."""
        self.cursor = cursor

    def reset(self):
        """Reset pagination to first page."""
        self.cursor = None


