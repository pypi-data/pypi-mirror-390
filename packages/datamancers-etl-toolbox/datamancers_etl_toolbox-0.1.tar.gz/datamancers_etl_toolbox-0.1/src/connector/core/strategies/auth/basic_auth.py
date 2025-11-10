"""
Basic authentication strategy.
"""

import base64
from typing import Dict

from .base_auth import BaseAuthStrategy


class BasicAuth(BaseAuthStrategy):
    """
    HTTP Basic authentication strategy.
    
    Implements RFC 7617 Basic Authentication.
    """

    def __init__(self, username: str, password: str):
        """
        Initialize basic authentication.

        Args:
            username: Username for authentication
            password: Password for authentication
        """
        if not username:
            raise ValueError("username is required")
        if not password:
            raise ValueError("password is required")

        self.username = username
        self.password = password

    def get_auth_headers(self) -> Dict[str, str]:
        """
        Get authentication headers with Basic auth credentials.

        Returns:
            Dict[str, str]: Dictionary containing Authorization header
        """
        credentials = f"{self.username}:{self.password}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        return {"Authorization": f"Basic {encoded_credentials}"}

    def validate_credentials(self) -> bool:
        """
        Validate basic auth credentials.

        Returns:
            bool: True if username and password are not empty
        """
        return bool(self.username and self.password)


