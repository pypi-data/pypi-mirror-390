"""
Token-based authentication strategy.
"""

from typing import Dict, Optional

from .base_auth import BaseAuthStrategy


class TokenAuth(BaseAuthStrategy):
    """
    Token-based authentication strategy.
    
    Supports both Bearer token and custom header token authentication.
    """

    def __init__(
        self,
        token: str,
        header_name: str = "Authorization",
        token_prefix: str = "Bearer",
    ):
        """
        Initialize token authentication.

        Args:
            token: Authentication token
            header_name: Header name for the token (default: "Authorization")
            token_prefix: Token prefix (default: "Bearer")
        """
        if not token:
            raise ValueError("token is required")

        self.token = token
        self.header_name = header_name
        self.token_prefix = token_prefix

    def get_auth_headers(self) -> Dict[str, str]:
        """
        Get authentication headers with token.

        Returns:
            Dict[str, str]: Dictionary containing authentication header
        """
        if self.token_prefix:
            value = f"{self.token_prefix} {self.token}"
        else:
            value = self.token

        return {self.header_name: value}

    def validate_credentials(self) -> bool:
        """
        Validate token credentials.

        Returns:
            bool: True if token is not empty
        """
        return bool(self.token)


