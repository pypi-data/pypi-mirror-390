"""Base HTTP client for EdgeLab API."""

import requests
from typing import Optional, Dict, Any
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from edgelab.config import get_settings
from edgelab.api.exceptions import (
    AuthenticationError,
    UnauthorizedError,
    NotFoundError,
    ValidationError,
    ServerError,
    NetworkError,
)


class EdgeLabClient:
    """Base HTTP client for EdgeLab API."""

    def __init__(self, base_url: Optional[str] = None):
        """Initialize HTTP client.

        Args:
            base_url: API base URL (defaults to settings)
        """
        settings = get_settings()
        self.base_url = base_url or settings.api_base_url
        self.session = self._create_session()

    def _create_session(self) -> requests.Session:
        """Create requests session with retry logic."""
        session = requests.Session()

        # Configure retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS", "POST"],
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        return session

    def _get_headers(self, authenticated: bool = False) -> Dict[str, str]:
        """Get request headers.

        Args:
            authenticated: Include authentication header

        Returns:
            Headers dict
        """
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "EdgeLab-CLI/0.1.0",
        }

        if authenticated:
            settings = get_settings()
            access_token = settings.get_access_token()
            if access_token:
                headers["Authorization"] = f"Bearer {access_token}"

        return headers

    def _handle_response(self, response: requests.Response) -> Any:
        """Handle API response and raise appropriate exceptions.

        Args:
            response: requests Response object

        Returns:
            Response JSON data

        Raises:
            Various EdgeLabAPIError subclasses
        """
        try:
            # Try to parse JSON response
            data = response.json()
        except ValueError:
            data = {"message": response.text}

        # Handle error status codes
        if response.status_code == 401:
            raise UnauthorizedError(data.get("error", "Unauthorized"))
        elif response.status_code == 403:
            raise AuthenticationError(data.get("error", "Forbidden"))
        elif response.status_code == 404:
            raise NotFoundError(data.get("error", "Not found"))
        elif response.status_code == 400:
            raise ValidationError(data.get("error", "Validation error"))
        elif response.status_code == 409:
            raise ValidationError(data.get("error", "Conflict"))
        elif response.status_code >= 500:
            raise ServerError(data.get("error", "Server error"))
        elif not response.ok:
            raise ServerError(f"HTTP {response.status_code}: {data.get('error', 'Unknown error')}")

        return data

    def get(self, endpoint: str, authenticated: bool = False, **kwargs) -> Any:
        """Make GET request.

        Args:
            endpoint: API endpoint (e.g., "/api/v1/edgelab/strategies")
            authenticated: Require authentication
            **kwargs: Additional requests kwargs

        Returns:
            Response data
        """
        url = f"{self.base_url}{endpoint}"
        headers = self._get_headers(authenticated=authenticated)

        try:
            response = self.session.get(url, headers=headers, **kwargs)
            return self._handle_response(response)
        except requests.exceptions.ConnectionError as e:
            raise NetworkError(f"Connection failed: {e}")
        except requests.exceptions.Timeout as e:
            raise NetworkError(f"Request timeout: {e}")

    def post(
        self, endpoint: str, data: Optional[Dict] = None, authenticated: bool = False, **kwargs
    ) -> Any:
        """Make POST request.

        Args:
            endpoint: API endpoint
            data: Request body (will be JSON encoded)
            authenticated: Require authentication
            **kwargs: Additional requests kwargs

        Returns:
            Response data
        """
        url = f"{self.base_url}{endpoint}"
        headers = self._get_headers(authenticated=authenticated)

        try:
            response = self.session.post(url, json=data, headers=headers, **kwargs)
            return self._handle_response(response)
        except requests.exceptions.ConnectionError as e:
            raise NetworkError(f"Connection failed: {e}")
        except requests.exceptions.Timeout as e:
            raise NetworkError(f"Request timeout: {e}")

    def put(
        self, endpoint: str, data: Optional[Dict] = None, authenticated: bool = False, **kwargs
    ) -> Any:
        """Make PUT request."""
        url = f"{self.base_url}{endpoint}"
        headers = self._get_headers(authenticated=authenticated)

        try:
            response = self.session.put(url, json=data, headers=headers, **kwargs)
            return self._handle_response(response)
        except requests.exceptions.ConnectionError as e:
            raise NetworkError(f"Connection failed: {e}")
        except requests.exceptions.Timeout as e:
            raise NetworkError(f"Request timeout: {e}")

    def delete(self, endpoint: str, authenticated: bool = False, **kwargs) -> Any:
        """Make DELETE request."""
        url = f"{self.base_url}{endpoint}"
        headers = self._get_headers(authenticated=authenticated)

        try:
            response = self.session.delete(url, headers=headers, **kwargs)
            return self._handle_response(response)
        except requests.exceptions.ConnectionError as e:
            raise NetworkError(f"Connection failed: {e}")
        except requests.exceptions.Timeout as e:
            raise NetworkError(f"Request timeout: {e}")

    def get_strategy_code(self, strategy_id: str) -> str:
        """Fetch public strategy code from marketplace.

        Args:
            strategy_id: Strategy UUID

        Returns:
            Strategy code as string

        Raises:
            EdgeLabAPIError: If fetch fails
        """
        response = self.get(
            f"/api/v1/edgelab/marketplace/strategies/{strategy_id}/code",
            authenticated=True,
        )
        # Response format: {"code": "..."}
        return response.get("code") or ""
