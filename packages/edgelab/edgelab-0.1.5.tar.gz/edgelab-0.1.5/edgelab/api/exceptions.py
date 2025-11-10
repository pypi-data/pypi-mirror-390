"""API exceptions."""


class EdgeLabAPIError(Exception):
    """Base exception for EdgeLab API errors."""

    pass


class AuthenticationError(EdgeLabAPIError):
    """Authentication failed."""

    pass


class UnauthorizedError(EdgeLabAPIError):
    """Unauthorized access."""

    pass


class NotFoundError(EdgeLabAPIError):
    """Resource not found."""

    pass


class ValidationError(EdgeLabAPIError):
    """Validation error."""

    pass


class ServerError(EdgeLabAPIError):
    """Server error."""

    pass


class NetworkError(EdgeLabAPIError):
    """Network error."""

    pass
