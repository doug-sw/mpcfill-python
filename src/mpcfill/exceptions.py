class MPCFillError(Exception):
    """Base exception for all MPCFill-related errors."""

    pass


class NetworkError(MPCFillError):
    """Raised when a network or connection error occurs."""

    pass


class NotFoundError(MPCFillError):
    """Raised when a requested resource is not found (HTTP 404)."""

    pass


class ServerError(MPCFillError):
    """Raised when the MPCFill server returns an HTTP 5xx error."""

    pass


class ClientError(MPCFillError):
    """Raised when the MPCFill service returns a non-404 4xx error."""

    pass
