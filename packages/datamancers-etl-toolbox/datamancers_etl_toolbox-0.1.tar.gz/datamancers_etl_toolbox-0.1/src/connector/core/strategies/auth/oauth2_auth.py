"""
OAuth2 authentication strategy.
"""

from typing import Callable, Dict, Optional

from .base_auth import BaseAuthStrategy


class OAuth2Auth(BaseAuthStrategy):
    """
    OAuth2 authentication strategy.
    
    Supports both access token and refresh token flow.
    """

    def __init__(
        self,
        access_token: Optional[str] = None,
        refresh_token: Optional[str] = None,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        token_url: Optional[str] = None,
        token_refresh_callback: Optional[Callable] = None,
    ):
        """
        Initialize OAuth2 authentication.

        Args:
            access_token: OAuth2 access token
            refresh_token: OAuth2 refresh token (optional)
            client_id: OAuth2 client ID (optional, for token refresh)
            client_secret: OAuth2 client secret (optional, for token refresh)
            token_url: Token endpoint URL (optional, for token refresh)
            token_refresh_callback: Callback function for token refresh (optional)
        """
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.client_id = client_id
        self.client_secret = client_secret
        self.token_url = token_url
        self.token_refresh_callback = token_refresh_callback

    def get_auth_headers(self) -> Dict[str, str]:
        """
        Get authentication headers with OAuth2 access token.

        Returns:
            Dict[str, str]: Dictionary containing Authorization header
        """
        if not self.access_token:
            # Try to refresh token if refresh_token is available
            if self.refresh_token and self.token_refresh_callback:
                self.access_token = self.token_refresh_callback(
                    self.refresh_token, self.client_id, self.client_secret, self.token_url
                )

        if not self.access_token:
            raise ValueError("access_token is required or token refresh failed")

        return {"Authorization": f"Bearer {self.access_token}"}

    def refresh_access_token(self) -> Optional[str]:
        """
        Refresh access token using refresh token.

        Returns:
            Optional[str]: New access token if refresh successful, None otherwise
        """
        if not self.refresh_token:
            return None

        if self.token_refresh_callback:
            self.access_token = self.token_refresh_callback(
                self.refresh_token, self.client_id, self.client_secret, self.token_url
            )
            return self.access_token

        # Default implementation would make HTTP request to token_url
        # This is left for subclasses or external implementations
        return None

    def validate_credentials(self) -> bool:
        """
        Validate OAuth2 credentials.

        Returns:
            bool: True if access_token or refresh_token is available
        """
        return bool(self.access_token or self.refresh_token)

