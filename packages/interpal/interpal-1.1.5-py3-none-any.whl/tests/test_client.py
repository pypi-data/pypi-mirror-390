"""
Tests for the main client classes.
"""

import pytest
from interpal import InterpalClient, AsyncInterpalClient
from interpal.exceptions import AuthenticationError, ValidationError


class TestInterpalClient:
    """Tests for synchronous InterpalClient."""
    
    def test_client_initialization(self):
        """Test client can be initialized."""
        client = InterpalClient()
        assert client is not None
        assert not client.is_authenticated
    
    def test_client_with_session_cookie(self):
        """Test client initialization with session cookie."""
        client = InterpalClient(session_cookie="test_cookie")
        assert client.auth.session_cookie == "test_cookie"
    
    def test_login_requires_credentials(self):
        """Test login fails without credentials."""
        client = InterpalClient()
        with pytest.raises(ValueError):
            client.login()
    
    def test_import_session(self):
        """Test session import."""
        client = InterpalClient()
        client.import_session("test_session_id", "test_token")
        assert client.auth.session_cookie == "test_session_id"
        assert client.auth.auth_token == "test_token"
    
    def test_export_session(self):
        """Test session export."""
        client = InterpalClient()
        client.import_session("test_session", "test_token")
        session = client.export_session()
        assert session['session_cookie'] == "test_session"
        assert session['auth_token'] == "test_token"


class TestAsyncInterpalClient:
    """Tests for asynchronous AsyncInterpalClient."""
    
    def test_async_client_initialization(self):
        """Test async client can be initialized."""
        client = AsyncInterpalClient()
        assert client is not None
        assert not client.is_authenticated
    
    def test_async_client_with_session_cookie(self):
        """Test async client initialization with session cookie."""
        client = AsyncInterpalClient(session_cookie="test_cookie")
        assert client.auth.session_cookie == "test_cookie"
    
    def test_async_login_requires_credentials(self):
        """Test async login fails without credentials."""
        client = AsyncInterpalClient()
        with pytest.raises(ValueError):
            client.login()
    
    @pytest.mark.asyncio
    async def test_async_client_close(self):
        """Test async client can be closed."""
        client = AsyncInterpalClient()
        await client.close()
        # Should not raise an exception


class TestClientMethods:
    """Tests for client convenience methods."""
    
    def test_client_has_api_modules(self):
        """Test client has all API modules."""
        client = InterpalClient()
        assert hasattr(client, 'user')
        assert hasattr(client, 'messages')
        assert hasattr(client, 'search')
        assert hasattr(client, 'media')
        assert hasattr(client, 'social')
        assert hasattr(client, 'realtime')
    
    def test_client_convenience_methods(self):
        """Test client has convenience methods."""
        client = InterpalClient()
        assert hasattr(client, 'get_self')
        assert hasattr(client, 'get_user')
        assert hasattr(client, 'get_threads')
        assert hasattr(client, 'send_message')
        assert hasattr(client, 'search_users')

