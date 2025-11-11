class TimebackError(Exception):
    """Base exception for Timeback client errors."""
    def __init__(self, *args, error_details=None, **kwargs):
        super().__init__(*args)
        self.error_details = error_details


class ConfigurationError(TimebackError):
    """Raised when required configuration/env vars are missing or invalid."""


class AuthError(TimebackError):
    """Raised when authentication fails."""


class RequestError(TimebackError):
    """Raised for non-2xx HTTP responses not covered by more specific errors."""


class NotFoundError(RequestError):
    """Raised when a 404 is returned by the API."""


class RateLimitError(RequestError):
    """Raised when a 429 is returned by the API."""


class ServerError(RequestError):
    """Raised when a 5xx is returned by the API."""


class ParseError(TimebackError):
    """Raised when response parsing into models fails."""


