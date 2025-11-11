"""Authentication strategies for ArcGIS Portal."""
import os
import time
import logging
from typing import Optional
from abc import ABC, abstractmethod
import requests

log = logging.getLogger(__name__)


class AuthStrategy(ABC):
    """Base authentication strategy."""

    @abstractmethod
    def get_token(self) -> Optional[str]:
        """Get authentication token."""
        pass

    @abstractmethod
    def is_token_valid(self) -> bool:
        """Check if current token is still valid."""
        pass


class NoAuth(AuthStrategy):
    """No authentication - for public layers."""

    def get_token(self) -> Optional[str]:
        return None

    def is_token_valid(self) -> bool:
        return True


class TokenAuth(AuthStrategy):
    """Use a pre-existing token."""

    def __init__(self, token: str, expires_at: Optional[float] = None):
        """
        Initialize with existing token.

        Args:
            token: The authentication token
            expires_at: Unix timestamp when token expires (None = never)
        """
        self.token = token
        self.expires_at = expires_at or (time.time() + 3600)

    def get_token(self) -> str:
        return self.token

    def is_token_valid(self) -> bool:
        return time.time() < self.expires_at - 300  # 5 min buffer


class UsernamePasswordAuth(AuthStrategy):
    """Authenticate with username and password."""

    def __init__(
        self,
        portal_url: str,
        username: Optional[str] = None,
        password: Optional[str] = None,
        env_username_key: str = "ARCGIS_USERNAME",
        env_password_key: str = "ARCGIS_PASSWORD"
    ):
        """
        Initialize username/password authentication.

        Args:
            portal_url: ArcGIS Portal URL
            username: Username (if None, reads from env var)
            password: Password (if None, reads from env var)
            env_username_key: Environment variable name for username
            env_password_key: Environment variable name for password
        """
        self.portal_url = portal_url.rstrip('/')
        self.username = username or os.environ.get(env_username_key, "")
        self.password = password or os.environ.get(env_password_key, "")
        self._token: Optional[str] = None
        self._token_expiry: float = 0

        if not self.username or not self.password:
            raise ValueError(
                f"Username and password required. Either pass them directly or "
                f"set {env_username_key} and {env_password_key} environment variables."
            )

    def get_token(self) -> str:
        """Get or refresh authentication token."""
        if not self.is_token_valid():
            self._refresh_token()
        return self._token

    def is_token_valid(self) -> bool:
        """Check if token is still valid."""
        if not self._token:
            return False
        # Refresh 5 minutes before expiry
        return time.time() < self._token_expiry - 300

    def _refresh_token(self):
        """Authenticate and get a new token."""
        token_url = f"{self.portal_url}/sharing/rest/generateToken"

        params = {
            'username': self.username,
            'password': self.password,
            'client': 'referer',
            'referer': self.portal_url,
            'expiration': 60,  # minutes
            'f': 'json'
        }

        try:
            response = requests.post(token_url, data=params)
            response.raise_for_status()
            result = response.json()

            if 'token' in result:
                self._token = result['token']
                # Token expires in 60 minutes
                self._token_expiry = time.time() + 3600
                log.info("Successfully obtained authentication token")
            else:
                error_msg = result.get('error', {}).get('message', 'Unknown error')
                raise Exception(f"Failed to get token: {error_msg}")
        except Exception as e:
            log.error(f"Error getting token: {e}")
            raise
