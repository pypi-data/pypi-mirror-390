"""
Base authentication strategy interface.
"""

from abc import ABC, abstractmethod
from typing import Dict


class BaseAuthStrategy(ABC):
    """
    Base class for authentication strategies.
    
    Authentication strategies are responsible for adding authentication
    headers or parameters to HTTP requests.
    """

    @abstractmethod
    def get_auth_headers(self) -> Dict[str, str]:
        """
        Get authentication headers.

        Returns:
            Dict[str, str]: Dictionary of authentication headers
        """
        pass

    def validate_credentials(self) -> bool:
        """
        Validate authentication credentials.

        Returns:
            bool: True if credentials are valid
        """
        return True


