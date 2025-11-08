"""
Authentication and session management for Interpals API.
"""

import requests
from typing import Optional, Dict, Any
from http.cookiejar import CookieJar
from .exceptions import AuthenticationError, ValidationError
from .utils import extract_cookie


class AuthManager:
    """
    Manages authentication and session cookies for Interpals API.
    """
    
    BASE_URL = "https://api.interpals.net"
    LOGIN_ENDPOINT = "/v1/token"
    VALIDATE_ENDPOINT = "/v1/account/self"
    
    def __init__(self, user_agent: str = "interpal-python-lib/1.0.0"):
        """
        Initialize the authentication manager.
        
        Args:
            user_agent: User agent string for requests
        """
        self.user_agent = user_agent
        self.session_cookie: Optional[str] = None
        self.auth_token: Optional[str] = None
        self.bot_id: Optional[str] = None
        self.cookie_jar = CookieJar()
        self._session: Optional[requests.Session] = None
    
    def login(self, username: str, password: str) -> Dict[str, str]:
        """
        Login with username and password.
        
        Args:
            username: Interpals username or email
            password: Account password
            
        Returns:
            Dictionary containing session cookie and auth token
            
        Raises:
            AuthenticationError: If login fails
            ValidationError: If credentials are invalid
        """
        if not username or not password:
            raise ValidationError("Username and password are required")
        
        # Prepare login request
        url = f"{self.BASE_URL}{self.LOGIN_ENDPOINT}"
        headers = {
            "User-Agent": self.user_agent,
            "Content-Type": "application/x-www-form-urlencoded",
        }
        data = {
            "username": username,
            "password": password,
        }
        
        try:
            # Create a session for cookie handling
            session = requests.Session()
            response = session.post(url, data=data, headers=headers)
            
            if response.status_code == 201:
                # Extract session cookie
                cookies = response.cookies
                session_id = None
                
                for cookie in cookies:
                    if cookie.name == "interpals_sessid":
                        session_id = cookie.value
                        break
                
                if not session_id:
                    # Try to extract from Set-Cookie header
                    set_cookie = response.headers.get("Set-Cookie", "")
                    session_id = extract_cookie(set_cookie, "interpals_sessid")
                
                if not session_id:
                    raise AuthenticationError("Login successful but session cookie not found")
                
                self.session_cookie = session_id
                self._session = session
                
                # Try to extract auth token from response
                try:
                    response_data = response.json()
                except Exception:
                    response_data = {}

                if isinstance(response_data, dict):
                    self.auth_token = response_data.get("auth_token", response_data.get("token"))
                    self.bot_id = self._extract_bot_id(response_data)

                return {
                    "session_cookie": self.session_cookie,
                    "auth_token": self.auth_token,
                    "bot_id": self.bot_id,
                }
            
            elif response.status_code == 401:
                raise AuthenticationError("Invalid username or password", status_code=401)
            elif response.status_code == 429:
                raise AuthenticationError("Too many login attempts. Please try again later.", status_code=429)
            else:
                raise AuthenticationError(
                    f"Login failed with status {response.status_code}",
                    status_code=response.status_code
                )
        
        except requests.RequestException as e:
            raise AuthenticationError(f"Network error during login: {str(e)}")
    
    def import_session(
        self,
        cookie_string: str,
        auth_token: Optional[str] = None,
        bot_id: Optional[str] = None,
    ):
        """
        Import an existing session from cookie string.
        
        Args:
            cookie_string: Session cookie value (interpals_sessid)
            auth_token: Optional authentication token
            
        Raises:
            ValidationError: If cookie string is invalid
        """
        if not cookie_string:
            raise ValidationError("Cookie string cannot be empty")
        
        # Extract session ID if full cookie string is provided
        if "interpals_sessid=" in cookie_string:
            session_id = extract_cookie(cookie_string, "interpals_sessid")
            if not session_id:
                raise ValidationError("Could not extract interpals_sessid from cookie string")
            self.session_cookie = session_id
        else:
            # Assume it's just the session ID
            self.session_cookie = cookie_string
        
        self.auth_token = auth_token
        self.bot_id = str(bot_id) if bot_id is not None else None
    
    def export_session(self) -> Dict[str, Optional[str]]:
        """
        Export current session for storage.
        
        Returns:
            Dictionary containing session cookie and auth token
        """
        return {
            "session_cookie": self.session_cookie,
            "auth_token": self.auth_token,
            "bot_id": self.bot_id,
        }
    
    def validate_session(self) -> bool:
        """
        Validate current session by making a test request.
        
        Returns:
            True if session is valid, False otherwise
            
        Raises:
            AuthenticationError: If no session is set
        """
        if not self.session_cookie:
            raise AuthenticationError("No session cookie set")
        
        url = f"{self.BASE_URL}{self.VALIDATE_ENDPOINT}"
        headers = self.get_headers()
        
        try:
            response = requests.get(url, headers=headers)
            return response.status_code == 200
        except requests.RequestException:
            return False
    
    def get_headers(self) -> Dict[str, str]:
        """
        Get headers for authenticated requests.
        
        Returns:
            Dictionary of headers including cookies and tokens
        """
        headers = {
            "User-Agent": self.user_agent,
        }
        
        if self.session_cookie:
            headers["Cookie"] = f"interpals_sessid={self.session_cookie}"
        
        if self.auth_token:
            headers["X-Auth-Token"] = self.auth_token
        
        return headers
    
    def clear_session(self):
        """Clear current session data."""
        self.session_cookie = None
        self.auth_token = None
        self.bot_id = None
        if self._session:
            self._session.close()
            self._session = None

    def _extract_bot_id(self, payload: Dict[str, Any]) -> Optional[str]:
        """Attempt to extract the bot/user id from the login payload."""
        if not isinstance(payload, dict):
            return None

        candidate_keys = (
            "bot_id",
            "botId",
            "id",
            "uid",
            "user_id",
            "userId",
            "account_id",
            "accountId",
        )

        for key in candidate_keys:
            value = payload.get(key)
            if value not in (None, ""):
                return str(value)

        nested_keys = (
            "bot",
            "user",
            "account",
            "profile",
            "data",
        )

        for container_key in nested_keys:
            nested = payload.get(container_key)
            if isinstance(nested, dict):
                for key in candidate_keys:
                    value = nested.get(key)
                    if value not in (None, ""):
                        return str(value)

        return None
    
    @property
    def is_authenticated(self) -> bool:
        """Check if user is authenticated."""
        return self.session_cookie is not None

