"""
Tests for custom exceptions.
"""

import pytest
from interpal.exceptions import (
    InterpalException,
    AuthenticationError,
    APIError,
    RateLimitError,
    WebSocketError,
    ValidationError,
)


def test_base_exception():
    """Test base InterpalException."""
    exc = InterpalException("Test error")
    assert str(exc) == "Test error"


def test_authentication_error():
    """Test AuthenticationError."""
    exc = AuthenticationError("Login failed", status_code=401)
    assert str(exc) == "Login failed"
    assert exc.status_code == 401


def test_api_error():
    """Test APIError."""
    exc = APIError("API failed", status_code=500)
    assert str(exc) == "API failed"
    assert exc.status_code == 500


def test_rate_limit_error():
    """Test RateLimitError."""
    exc = RateLimitError("Too many requests", retry_after=60)
    assert exc.status_code == 429
    assert exc.retry_after == 60


def test_websocket_error():
    """Test WebSocketError."""
    exc = WebSocketError("Connection failed")
    assert str(exc) == "Connection failed"


def test_validation_error():
    """Test ValidationError."""
    exc = ValidationError("Invalid data")
    assert str(exc) == "Invalid data"


def test_exception_inheritance():
    """Test exception inheritance."""
    assert issubclass(AuthenticationError, InterpalException)
    assert issubclass(APIError, InterpalException)
    assert issubclass(RateLimitError, APIError)
    assert issubclass(WebSocketError, InterpalException)
    assert issubclass(ValidationError, InterpalException)

