"""
Custom exception classes for the Interpals library.
"""


class InterpalException(Exception):
    """Base exception class for all Interpals library exceptions."""
    pass


class AuthenticationError(InterpalException):
    """Raised when authentication fails or session is invalid."""
    
    def __init__(self, message="Authentication failed", status_code=None):
        self.status_code = status_code
        super().__init__(message)


class APIError(InterpalException):
    """Raised when an API request fails."""
    
    def __init__(self, message, status_code=None, response=None):
        self.status_code = status_code
        self.response = response
        super().__init__(message)


class RateLimitError(APIError):
    """Raised when rate limit is exceeded."""
    
    def __init__(self, message="Rate limit exceeded", retry_after=None):
        self.retry_after = retry_after
        super().__init__(message, status_code=429)


class WebSocketError(InterpalException):
    """Raised when WebSocket connection fails."""
    pass


class ValidationError(InterpalException):
    """Raised when invalid parameters or data are provided."""
    pass


class NotFoundError(APIError):
    """Raised when a requested resource is not found."""
    
    def __init__(self, message="Resource not found"):
        super().__init__(message, status_code=404)


class PermissionError(APIError):
    """Raised when user doesn't have permission to access a resource."""
    
    def __init__(self, message="Permission denied"):
        super().__init__(message, status_code=403)

