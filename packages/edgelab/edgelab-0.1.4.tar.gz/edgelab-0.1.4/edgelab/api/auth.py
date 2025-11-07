"""Authentication API client."""

from typing import Dict, Any
from edgelab.api.client import EdgeLabClient


class AuthAPI:
    """Authentication API endpoints."""

    def __init__(self, client: EdgeLabClient):
        """Initialize auth API.

        Args:
            client: Base HTTP client
        """
        self.client = client

    def signup(self, email: str, password: str) -> Dict[str, Any]:
        """Sign up for new EdgeLab account.

        Args:
            email: User email
            password: User password

        Returns:
            Response data with tokens and user info

        Raises:
            ValidationError: Email already exists or invalid input
            NetworkError: Connection failed
        """
        data = {"email": email, "password": password}
        response = self.client.post("/api/v1/edgelab/auth/signup", data=data)
        return response["data"]  # API wraps response in {"data": {...}}

    def login(self, email: str, password: str) -> Dict[str, Any]:
        """Login to EdgeLab.

        Args:
            email: User email
            password: User password

        Returns:
            Response data with tokens and user info

        Raises:
            AuthenticationError: Invalid credentials
            NetworkError: Connection failed
        """
        data = {"email": email, "password": password}
        response = self.client.post("/api/v1/edgelab/auth/login", data=data)
        return response["data"]

    def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """Refresh access token.

        Args:
            refresh_token: Refresh token

        Returns:
            New access and refresh tokens

        Raises:
            UnauthorizedError: Invalid refresh token
        """
        data = {"refresh_token": refresh_token}
        response = self.client.post("/api/v1/edgelab/auth/refresh", data=data)
        return response["data"]

    def logout(self, refresh_token: str) -> Dict[str, Any]:
        """Logout from EdgeLab.

        Args:
            refresh_token: Refresh token to invalidate

        Returns:
            Success message
        """
        data = {"refresh_token": refresh_token}
        return self.client.post("/api/v1/edgelab/auth/logout", data=data)
