"""
Exception classes for Concise SDK
"""


class ConciseError(Exception):
    """Base exception for Concise SDK"""
    pass


class AuthenticationError(ConciseError):
    """Raised when API key is invalid or missing"""
    pass


class APIError(ConciseError):
    """Raised when API returns an error"""

    def __init__(self, message: str, status_code: int = None):
        super().__init__(message)
        self.status_code = status_code


class RateLimitError(ConciseError):
    """Raised when rate limit is exceeded"""
    pass


class NetworkError(ConciseError):
    """Raised when network request fails"""
    pass
