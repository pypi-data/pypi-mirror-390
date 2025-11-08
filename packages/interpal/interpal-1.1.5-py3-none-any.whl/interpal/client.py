"""
Main client classes for the Interpals library.
Provides both synchronous and asynchronous interfaces.
"""

from typing import Optional, Callable, Dict, Any

try:  # Support running as a package or as a standalone module
    from .auth import AuthManager
    from .http import HTTPClient, AsyncHTTPClient
    from .websocket import WebSocketClient, SyncWebSocketClient
    from .websocket_config import WebSocketConfig, ConnectionProfile
    from .session_manager import SessionManager
    from .state import InterpalState
    from .api.user import UserAPI
    from .api.messages import MessagesAPI
    from .api.search import SearchAPI
    from .api.media import MediaAPI
    from .api.social import SocialAPI
    from .api.realtime import RealtimeAPI
    from .api.notifications import NotificationsAPI
    from .api.posts import PostsAPI
except ImportError:  # pragma: no cover - fallback for direct execution
    from interpal.auth import AuthManager
    from interpal.http import HTTPClient, AsyncHTTPClient
    from interpal.websocket import WebSocketClient, SyncWebSocketClient
    from interpal.websocket_config import WebSocketConfig, ConnectionProfile
    from interpal.session_manager import SessionManager
    from interpal.state import InterpalState
    from interpal.api.user import UserAPI
    from interpal.api.messages import MessagesAPI
    from interpal.api.search import SearchAPI
    from interpal.api.media import MediaAPI
    from interpal.api.social import SocialAPI
    from interpal.api.realtime import RealtimeAPI
    from interpal.api.notifications import NotificationsAPI
    from interpal.api.posts import PostsAPI


class InterpalClient:
    """
    Synchronous Interpals client.
    
    Example:
        >>> client = InterpalClient(username="user", password="pass")
        >>> client.login()
        >>> profile = client.get_self()
        >>> print(f"Logged in as {profile.name}")
    """
    
    def __init__(
        self,
        username: Optional[str] = None,
        password: Optional[str] = None,
        session_cookie: Optional[str] = None,
        auth_token: Optional[str] = None,
        auto_login: bool = False,
        user_agent: str = "interpal-python-lib/2.0.0",
        persist_session: bool = False,
        session_file: Optional[str] = None,
        session_expiration_hours: int = 24,
        max_messages: int = 1000,
        cache_users: bool = True,
        cache_threads: bool = True,
        weak_references: bool = True,
        websocket_config: Optional[WebSocketConfig] = None,
        websocket_profile: Optional[str] = None,
        enable_websocket_health_monitoring: bool = True
    ):
        """
        Initialize Interpals client.

        Args:
            username: Interpals username for login
            password: Account password
            session_cookie: Existing session cookie
            auth_token: Existing auth token
            auto_login: Automatically login on initialization
            user_agent: User agent string
            persist_session: Enable persistent session storage
            session_file: Path to session file (default: .interpals_session.json)
            session_expiration_hours: Hours until session expires (default: 24)
            max_messages: Maximum number of messages to cache (default: 1000)
            cache_users: Enable user caching (default: True)
            cache_threads: Enable thread caching (default: True)
            weak_references: Use weak references for memory efficiency (default: True)
            websocket_config: Custom WebSocket configuration (default: stable profile)
            websocket_profile: WebSocket profile name ('stable', 'mobile', 'unstable_network')
            enable_websocket_health_monitoring: Enable WebSocket health monitoring (default: True)
        """
        # Store credentials
        self._username = username
        self._password = password
        self.bot_id: Optional[str] = None
        self.bot_id: Optional[str] = None
        self.bot_id: Optional[str] = None
        
        # Initialize session manager
        self._persist_session = persist_session
        self._session_manager = None
        if persist_session:
            self._session_manager = SessionManager(
                session_file=session_file,
                expiration_hours=session_expiration_hours
            )
        
        # Initialize auth manager
        self.auth = AuthManager(user_agent=user_agent)
        
        # Try to load saved session first if persist_session is enabled
        loaded_from_file = False
        if self._session_manager:
            saved_session = self._session_manager.load_session()
            if saved_session:
                print(f"Loading saved session for {saved_session.get('username', 'user')}...")
                self.auth.import_session(
                    saved_session['session_cookie'],
                    saved_session.get('auth_token'),
                    saved_session.get('bot_id')
                )
                if saved_session.get('bot_id') is not None:
                    self.bot_id = str(saved_session['bot_id'])
                loaded_from_file = True
                
                # Validate the loaded session
                try:
                    if not self.auth.validate_session():
                        print("Saved session is invalid. Will login with credentials.")
                        loaded_from_file = False
                        self._session_manager.clear_session()
                    else:
                        print("Saved session is valid!")
                except Exception as e:
                    print(f"Session validation failed: {e}")
                    loaded_from_file = False
                    self._session_manager.clear_session()
        
        # Import session if provided explicitly
        if not loaded_from_file and session_cookie:
            self.auth.import_session(session_cookie, auth_token)
            self.bot_id = self.auth.bot_id
            self.bot_id = self.auth.bot_id

        # Initialize state management
        self.state = InterpalState(
            dispatch=None,  # Will be set when WebSocket is initialized
            http=None,      # Will be set after HTTP client creation
            max_messages=max_messages,
            cache_users=cache_users,
            cache_threads=cache_threads,
            weak_references=weak_references
        )

        # Initialize HTTP client
        self.http = HTTPClient(self.auth)

        # Set HTTP reference in state
        self.state.http = self.http
        
        # Initialize WebSocket configuration
        if websocket_config:
            self._websocket_config = websocket_config
        elif websocket_profile:
            self._websocket_config = WebSocketConfig.from_profile(websocket_profile)
        else:
            self._websocket_config = WebSocketConfig()
        
        self._enable_websocket_health_monitoring = enable_websocket_health_monitoring
        
        # Initialize WebSocket client
        self._ws_client: Optional[SyncWebSocketClient] = None
        
        # Initialize API modules with state
        self.user = UserAPI(self.http, state=self.state)
        self.messages = MessagesAPI(self.http, state=self.state)
        self.search = SearchAPI(self.http, state=self.state)
        self.media = MediaAPI(self.http, state=self.state)
        self.social = SocialAPI(self.http, state=self.state)
        self.realtime = RealtimeAPI(self.http, state=self.state)
        self.notifications = NotificationsAPI(self.http, state=self.state)
        self.posts = PostsAPI(self.http, state=self.state)
        
        # Auto login if requested and no valid session was loaded
        if not loaded_from_file and auto_login and username and password:
            self.login()
    
    def login(self, username: Optional[str] = None, password: Optional[str] = None):
        """
        Login to Interpals and save session if persist_session is enabled.
        
        Args:
            username: Username (uses constructor value if not provided)
            password: Password (uses constructor value if not provided)
        """
        user = username or self._username
        pwd = password or self._password
        
        if not user or not pwd:
            raise ValueError("Username and password required for login")
        
        # Perform login
        session_data = self.auth.login(user, pwd)
        if session_data.get('bot_id') is not None:
            self.bot_id = str(session_data['bot_id'])
            self.auth.bot_id = self.bot_id
        
        # Save session if persistence is enabled
        if self._session_manager:
            if not self.bot_id:
                try:
                    profile = self.user.get_self()
                    potential_id = getattr(profile, 'id', None)
                    if potential_id is None and isinstance(profile, dict):
                        potential_id = profile.get('id')
                    if potential_id is not None:
                        self.bot_id = str(potential_id)
                        self.auth.bot_id = self.bot_id
                except Exception as e:
                    print(f"Warning: Failed to determine bot ID after login: {e}")
            self._session_manager.save_session(
                session_cookie=session_data['session_cookie'],
                auth_token=session_data.get('auth_token'),
                username=user,
                bot_id=self.bot_id
            )
            print(f"Session saved and will expire in {self._session_manager.expiration_hours} hours")
    
    def import_session(
        self,
        cookie_string: str,
        auth_token: Optional[str] = None,
        bot_id: Optional[str] = None,
    ):
        """
        Import an existing session.
        
        Args:
            cookie_string: Session cookie value
            auth_token: Optional auth token
        """
        self.auth.import_session(cookie_string, auth_token, bot_id)
        self.bot_id = self.auth.bot_id
    
    def export_session(self) -> Dict[str, Optional[str]]:
        """
        Export current session for storage.
        
        Returns:
            Dictionary with session_cookie and auth_token
        """
        return self.auth.export_session()
    
    def validate_session(self) -> bool:
        """
        Validate current session.
        
        Returns:
            True if session is valid
        """
        return self.auth.validate_session()
    
    @property
    def is_authenticated(self) -> bool:
        """Check if client is authenticated."""
        return self.auth.is_authenticated
    
    # Convenience methods for common operations
    
    def get_self(self):
        """Get current user profile."""
        profile = self.user.get_self()
        potential_id = getattr(profile, 'id', None)
        if potential_id is None and isinstance(profile, dict):
            potential_id = profile.get('id')
        if potential_id is not None:
            self.bot_id = str(potential_id)
            self.auth.bot_id = self.bot_id
        return profile
    
    def get_user(self, user_id: str):
        """Get user profile by ID."""
        return self.user.get_user(user_id)
    
    def get_threads(self):
        """Get message threads."""
        return self.messages.get_threads()
    
    def get_user_thread(self, user_id: str):
        """Get or create thread with a user."""
        return self.messages.get_user_thread(user_id)
    
    def send_message(self, thread_id: str, content: str):
        """Send a message."""
        return self.messages.send_message(thread_id, content)
    
    def send_message_correction(
        self,
        thread_id: str,
        message: str,
        attachment_id: str,
        tmp_id: Optional[str] = None,
    ):
        """Send a correction attachment message."""
        return self.messages.send_message_correction(thread_id, message, attachment_id, tmp_id)

    def read_message(self, thread_id: str, message_id: str):
        """Mark a specific message as read."""
        return self.messages.read_message(thread_id, message_id)

    def send_gif(self, thread_id: str, gif_url: str, tmp_id: Optional[str] = None):
        """
        Send a GIF as a message.
        
        Args:
            thread_id: Thread ID to send the GIF to
            gif_url: URL of the GIF to send
            tmp_id: Temporary ID for the message (optional)
            
        Returns:
            Sent Message object with GIF attachment
        """
        return self.messages.send_gif(thread_id, gif_url, tmp_id)
    
    def search_users(self, **kwargs):
        """Search for users."""
        return self.search.search_users(**kwargs)
    
    def get_feed(self, feed_type: str = "global", limit: int = 20, **kwargs):
        """
        Get main feed.
        
        Args:
            feed_type: Type of feed - "global" or "following" (default: "global")
            limit: Maximum items (default: 20)
            **kwargs: Additional parameters (offset, extra)
        """
        return self.search.get_feed(feed_type=feed_type, limit=limit, **kwargs)
    
    def upload_photo(self, file_path: str, caption: Optional[str] = None):
        """Upload a photo."""
        return self.media.upload_photo(file_path, caption)
    
    def send_photo_message(
        self, 
        thread_id: str, 
        file_path: Optional[str] = None,
        image_url: Optional[str] = None,
        tmp_id: Optional[str] = None
    ):
        """
        Upload and send a photo as a message.
        
        Args:
            thread_id: Thread ID to send the photo to
            file_path: Path to the local photo file (optional if image_url provided)
            image_url: URL of the image to download and send (optional if file_path provided)
            tmp_id: Temporary ID for the message (optional)
            
        Returns:
            Dictionary with message data including id, thread_id, sender_id, 
            attachments with photo details, fake_id, and tmp_id
        """
        return self.media.send_photo_message(thread_id, file_path, image_url, tmp_id)
    
    def get_notifications(self):
        """Get notifications."""
        return self.notifications.get_notifications()
    
    # WebSocket event system
    
    def event(self, event_name: str):
        """
        Decorator for registering WebSocket event handlers.
        
        Args:
            event_name: Name of the event (e.g., 'on_message', 'on_typing')
            
        Example:
            @client.event('on_message')
            def handle_message(data):
                print(f"New message: {data}")
        """
        if self._ws_client is None:
            self._ws_client = SyncWebSocketClient(
                self.auth,
                config=self._websocket_config,
                enable_health_monitoring=self._enable_websocket_health_monitoring
            )
        return self._ws_client.on(event_name)
    
    def start_websocket(self):
        """Start WebSocket connection for real-time events."""
        if self._ws_client is None:
            self._ws_client = SyncWebSocketClient(
                self.auth,
                config=self._websocket_config,
                enable_health_monitoring=self._enable_websocket_health_monitoring
            )
        self._ws_client.connect()
    
    def stop_websocket(self):
        """Stop WebSocket connection."""
        if self._ws_client:
            self._ws_client.disconnect()
    
    def close(self):
        """Close all connections."""
        self.http.close()
        if self._ws_client:
            self._ws_client.disconnect()
        self.auth.clear_session()
    
    def get_session_info(self) -> Optional[Dict[str, Any]]:
        """
        Get information about stored session.
        
        Returns:
            Dictionary with session info or None if no session manager
        """
        if self._session_manager:
            return self._session_manager.get_session_info()
        return None
    
    def clear_saved_session(self):
        """Clear saved session file."""
        if self._session_manager:
            self._session_manager.clear_session()
            print("Saved session cleared")

    # State management methods

    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics from the state manager.

        Returns:
            Dictionary with cache statistics
        """
        return self.state.get_cache_stats()

    def clear_caches(self):
        """Clear all caches in the state manager."""
        self.state.clear_all_caches()

    def clear_user_cache(self):
        """Clear user cache."""
        self.state.clear_user_cache()

    def clear_message_cache(self):
        """Clear message cache."""
        self.state.clear_message_cache()

    def get_cached_user(self, user_id: str):
        """
        Get cached user by ID.

        Args:
            user_id: User ID

        Returns:
            Cached User or None
        """
        return self.state.get_cached_user(user_id)

    def get_cached_message(self, message_id: str):
        """
        Get cached message by ID.

        Args:
            message_id: Message ID

        Returns:
            Cached Message or None
        """
        return self.state.get_cached_message(message_id)
    
    def get_websocket_status(self) -> Optional[Dict[str, Any]]:
        """
        Get WebSocket connection status and health metrics.
        
        Returns:
            Dictionary with connection status or None if WebSocket not initialized
        """
        if self._ws_client:
            return self._ws_client.get_connection_status()
        return None
    
    def get_websocket_health(self) -> Optional[Dict[str, Any]]:
        """
        Get WebSocket health metrics.
        
        Returns:
            Dictionary with health metrics or None if WebSocket not initialized
        """
        if self._ws_client:
            return self._ws_client.get_health_metrics()
        return None
    
    def get_deduplication_stats(self) -> Optional[Dict[str, Any]]:
        """
        Get WebSocket event deduplication statistics.
        
        Shows how many duplicate events were blocked during hot-swap reconnections.
        
        Returns:
            Dictionary with deduplication stats or None if WebSocket not initialized
        """
        if self._ws_client:
            return self._ws_client.get_deduplication_stats()
        return None


class AsyncInterpalClient:
    """
    Asynchronous Interpals client.
    
    Example:
        >>> client = AsyncInterpalClient(username="user", password="pass")
        >>> await client.login()
        >>> profile = await client.get_self()
        >>> print(f"Logged in as {profile.name}")
    """
    
    def __init__(
        self,
        username: Optional[str] = None,
        password: Optional[str] = None,
        session_cookie: Optional[str] = None,
        auth_token: Optional[str] = None,
        user_agent: str = "interpal-python-lib/2.0.0",
        persist_session: bool = False,
        session_file: Optional[str] = None,
        session_expiration_hours: int = 24,
        max_messages: int = 1000,
        cache_users: bool = True,
        cache_threads: bool = True,
        weak_references: bool = True,
        websocket_config: Optional[WebSocketConfig] = None,
        websocket_profile: Optional[str] = None,
        enable_websocket_health_monitoring: bool = True
    ):
        """
        Initialize async Interpals client.

        Args:
            username: Interpals username for login
            password: Account password
            session_cookie: Existing session cookie
            auth_token: Existing auth token
            user_agent: User agent string
            persist_session: Enable persistent session storage
            session_file: Path to session file (default: .interpals_session.json)
            session_expiration_hours: Hours until session expires (default: 24)
            max_messages: Maximum number of messages to cache (default: 1000)
            cache_users: Enable user caching (default: True)
            cache_threads: Enable thread caching (default: True)
            weak_references: Use weak references for memory efficiency (default: True)
            websocket_config: Custom WebSocket configuration (default: stable profile)
            websocket_profile: WebSocket profile name ('stable', 'mobile', 'unstable_network')
            enable_websocket_health_monitoring: Enable WebSocket health monitoring (default: True)
        """
        # Store credentials
        self._username = username
        self._password = password
        self.bot_id: Optional[str] = None
        
        # Initialize session manager
        self._persist_session = persist_session
        self._session_manager = None
        if persist_session:
            self._session_manager = SessionManager(
                session_file=session_file,
                expiration_hours=session_expiration_hours
            )
        
        # Initialize auth manager
        self.auth = AuthManager(user_agent=user_agent)
        
        # Try to load saved session first if persist_session is enabled
        loaded_from_file = False
        if self._session_manager:
            saved_session = self._session_manager.load_session()
            
            if saved_session:
                print(f"Loading saved session for {saved_session.get('username', 'user')}...")
                self.auth.import_session(
                    saved_session['session_cookie'],
                    saved_session.get('auth_token'),
                    saved_session.get('bot_id')
                )
                if saved_session.get('bot_id') is not None:
                    self.bot_id = str(saved_session['bot_id'])
                loaded_from_file = True
                
                # Validate the loaded session
                try:
                    if not self.auth.validate_session():
                        print("Saved session is invalid. Will login with credentials.")
                        loaded_from_file = False
                        self._session_manager.clear_session()
                    else:
                        print("Saved session is valid!")
                except Exception as e:
                    print(f"Session validation failed: {e}")
                    loaded_from_file = False
                    self._session_manager.clear_session()
        
        # Import session if provided explicitly
        if not loaded_from_file and session_cookie:
            self.auth.import_session(session_cookie, auth_token)
            self.bot_id = self.auth.bot_id

        # Initialize state management
        self.state = InterpalState(
            dispatch=None,  # Will be set when WebSocket is initialized
            http=None,      # Will be set after HTTP client creation
            max_messages=max_messages,
            cache_users=cache_users,
            cache_threads=cache_threads,
            weak_references=weak_references
        )

        # Initialize async HTTP client
        self.http = AsyncHTTPClient(self.auth)

        # Set HTTP reference in state
        self.state.http = self.http
        
        # Initialize WebSocket configuration
        if websocket_config:
            self._websocket_config = websocket_config
        elif websocket_profile:
            self._websocket_config = WebSocketConfig.from_profile(websocket_profile)
        else:
            self._websocket_config = WebSocketConfig()
        
        self._enable_websocket_health_monitoring = enable_websocket_health_monitoring
        
        # Initialize WebSocket client
        self._ws_client: Optional[WebSocketClient] = None
        
        # Initialize API modules with state (they'll use async methods)
        self.user = UserAPI(self.http, state=self.state)
        self.messages = MessagesAPI(self.http, state=self.state)
        self.search = SearchAPI(self.http, state=self.state)
        self.media = MediaAPI(self.http, state=self.state)
        self.social = SocialAPI(self.http, state=self.state)
        self.realtime = RealtimeAPI(self.http, state=self.state)
        self.notifications = NotificationsAPI(self.http, state=self.state)
        self.posts = PostsAPI(self.http, state=self.state)
    
    def login(self, username: Optional[str] = None, password: Optional[str] = None):
        """
        Login to Interpals and save session if persist_session is enabled (sync operation).
        
        Args:
            username: Username (uses constructor value if not provided)
            password: Password (uses constructor value if not provided)
        """
        user = username or self._username
        pwd = password or self._password
        print(f"Logging in as {user}...")
        if not user or not pwd:
            raise ValueError("Username and password required for login")
        
        # Login is synchronous even in async client
        session_data = self.auth.login(user, pwd)
        if session_data.get('bot_id') is not None:
            self.bot_id = str(session_data['bot_id'])
            self.auth.bot_id = self.bot_id
        
        # Save session if persistence is enabled
        if self._session_manager:
            self._session_manager.save_session(
                session_cookie=session_data['session_cookie'],
                auth_token=session_data.get('auth_token'),
                username=user,
                bot_id=self.bot_id
            )
            print(f"Session saved and will expire in {self._session_manager.expiration_hours} hours")
    
    def import_session(
        self,
        cookie_string: str,
        auth_token: Optional[str] = None,
        bot_id: Optional[str] = None,
    ):
        """
        Import an existing session.
        
        Args:
            cookie_string: Session cookie value
            auth_token: Optional auth token
        """
        self.auth.import_session(cookie_string, auth_token, bot_id)
        self.bot_id = self.auth.bot_id
    
    def export_session(self) -> Dict[str, Optional[str]]:
        """
        Export current session for storage.
        
        Returns:
            Dictionary with session_cookie and auth_token
        """
        return self.auth.export_session()
    
    @property
    def is_authenticated(self) -> bool:
        """Check if client is authenticated."""
        return self.auth.is_authenticated
    
    # Async convenience methods for common operations
    
    async def get_self(self):
        """Get current user profile."""
        data = await self.http.get("/v1/account/self")
        if self.state:
            profile = self.state.create_profile(data)
        else:
            from .models.user import Profile
            profile = Profile(state=self.state, data=data)

        potential_id = getattr(profile, 'id', None)
        if potential_id is None and isinstance(profile, dict):
            potential_id = profile.get('id')
        if potential_id is not None:
            self.bot_id = str(potential_id)
            self.auth.bot_id = self.bot_id

        return profile
    
    async def get_user(self, user_id: str):
        """Get user profile by ID."""
        data = await self.http.get(f"/v1/profile/{user_id}")
        if self.state:
            return self.state.create_profile(data)
        from .models.user import Profile
        return Profile(state=self.state, data=data)
    
    async def get_threads(self):
        """Get message threads."""
        data = await self.http.get("/v1/thread")
        if isinstance(data, list):
            if self.state:
                return [self.state.create_thread(t) for t in data]
            from .models.message import Thread
            return [Thread(state=self.state, data=t) for t in data]
        elif isinstance(data, dict) and "threads" in data:
            if self.state:
                return [self.state.create_thread(t) for t in data["threads"]]
            from .models.message import Thread
            return [Thread(state=self.state, data=t) for t in data["threads"]]
        return []
    
    async def send_message(self, thread_id: str, content: str):
        """Send a message."""
        # API expects 'message' field, not 'content'
        data = {"thread_id": thread_id, "message": content}
        response = await self.http.post("/v1/message", data=data)
        if self.state:
            return self.state.create_message(response)
        from .models.message import Message
        return Message(state=self.state, data=response)
    
    async def send_gif(self, thread_id: str, gif_url: str, tmp_id: Optional[str] = None):
        """
        Send a GIF as a message.
        
        Args:
            thread_id: Thread ID to send the GIF to
            gif_url: URL of the GIF to send
            tmp_id: Temporary ID for the message (optional)
            
        Returns:
            Sent Message object with GIF attachment
        """
        data = {
            'thread_id': thread_id,
            'attachment_type': 'gif',
            'tmp_id': tmp_id or '34bc',
            'gif_attachment_url': gif_url,
        }
        response = await self.http.post("/v1/message", data=data)
        if self.state:
            return self.state.create_message(response)
        from .models.message import Message
        return Message(state=self.state, data=response)
    
    async def send_message_correction(
        self,
        thread_id: str,
        message: str,
        attachment_id: str,
        tmp_id: Optional[str] = None,
    ):
        """Send a correction attachment message."""
        data = {
            "thread_id": thread_id,
            "message": message,
            "attachment_type": "correction",
            "attachment_id": attachment_id,
        }
        if tmp_id is not None:
            data["tmp_id"] = tmp_id
        response = await self.http.post("/v1/message", data=data)
        if self.state:
            return self.state.create_message(response)
        from .models.message import Message
        return Message(state=self.state, data=response)

    async def read_message(self, thread_id: str, message_id: str):
        """Mark a specific message as read."""
        data = {"message_id": message_id}
        return await self.http.put(f"/v1/thread/{thread_id}/viewed", data=data)

    async def search_users(self, **kwargs):
        """Search for users."""
        params = {k: v for k, v in kwargs.items() if v is not None}
        data = await self.http.get("/v1/search/user", params=params)
        from .models.user import Profile
        if isinstance(data, list):
            return [Profile(u) for u in data]
        elif isinstance(data, dict) and "results" in data:
            return [Profile(u) for u in data["results"]]
        return []
    
    async def get_feed(
        self,
        feed_type: str = "global",
        limit: int = 20,
        offset: int = 0,
        extra: Optional[str] = "photos.user"
    ):
        """
        Get main feed.
        
        Args:
            feed_type: Type of feed - "global" or "following" (default: "global")
            limit: Maximum items (default: 20)
            offset: Pagination offset
            extra: Extra data to include (default: "photos.user")
        """
        params = {
            "type": feed_type,
            "limit": limit,
            "offset": offset
        }
        
        if extra:
            params["extra"] = extra
        
        data = await self.http.get("/v1/feed", params=params)
        if isinstance(data, list):
            return data
        elif isinstance(data, dict) and "feed" in data:
            return data["feed"]
        return []
    
    async def get_notifications(self):
        """Get notifications."""
        data = await self.http.get("/v1/notification/my")
        from .models.social import Notification
        if isinstance(data, list):
            return [Notification(n) for n in data]
        elif isinstance(data, dict) and "notifications" in data:
            return [Notification(n) for n in data["notifications"]]
        return []
    
    # WebSocket event system
    
    def event(self, event_name: str):
        """
        Decorator for registering WebSocket event handlers.
        
        Args:
            event_name: Name of the event (e.g., 'on_message', 'on_typing')
            
        Example:
            @client.event('on_message')
            async def handle_message(data):
                print(f"New message: {data}")
        """
        if self._ws_client is None:
            self._ws_client = WebSocketClient(
                self.auth,
                config=self._websocket_config,
                enable_health_monitoring=self._enable_websocket_health_monitoring
            )
        return self._ws_client.on(event_name)
    
    async def start(self):
        """
        Start the client and connect WebSocket for real-time events.
        This method will run indefinitely until stopped.
        """
        if self._ws_client is None:
            self._ws_client = WebSocketClient(
                self.auth,
                config=self._websocket_config,
                enable_health_monitoring=self._enable_websocket_health_monitoring
            )
        
        print(f"🔧 WebSocket client event handlers: {list(self._ws_client.event_handlers.keys())}")
        await self._ws_client.start()
    
    async def connect_websocket(self):
        """Connect to WebSocket without blocking."""
        if self._ws_client is None:
            self._ws_client = WebSocketClient(
                self.auth,
                config=self._websocket_config,
                enable_health_monitoring=self._enable_websocket_health_monitoring
            )
        await self._ws_client.connect()
    
    async def disconnect_websocket(self):
        """Disconnect WebSocket."""
        if self._ws_client:
            await self._ws_client.disconnect()
    
    async def close(self):
        """Close all connections."""
        await self.http.close()
        if self._ws_client:
            await self._ws_client.disconnect()
        self.auth.clear_session()
    
    def get_session_info(self) -> Optional[Dict[str, Any]]:
        """
        Get information about stored session.
        
        Returns:
            Dictionary with session info or None if no session manager
        """
        if self._session_manager:
            return self._session_manager.get_session_info()
        return None
    
    def clear_saved_session(self):
        """Clear saved session file."""
        if self._session_manager:
            self._session_manager.clear_session()
            print("Saved session cleared")


    # State management methods

    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics from the state manager.

        Returns:
            Dictionary with cache statistics
        """
        return self.state.get_cache_stats()

    def clear_caches(self):
        """Clear all caches in the state manager."""
        self.state.clear_all_caches()

    def clear_user_cache(self):
        """Clear user cache."""
        self.state.clear_user_cache()

    def clear_message_cache(self):
        """Clear message cache."""
        self.state.clear_message_cache()

    def get_cached_user(self, user_id: str):
        """
        Get cached user by ID.

        Args:
            user_id: User ID

        Returns:
            Cached User or None
        """
        return self.state.get_cached_user(user_id)

    def get_cached_message(self, message_id: str):
        """
        Get cached message by ID.

        Args:
            message_id: Message ID

        Returns:
            Cached Message or None
        """
        return self.state.get_cached_message(message_id)
    
    def get_websocket_status(self) -> Optional[Dict[str, Any]]:
        """
        Get WebSocket connection status and health metrics.
        
        Returns:
            Dictionary with connection status or None if WebSocket not initialized
        """
        if self._ws_client:
            return self._ws_client.get_connection_status()
        return None
    
    def get_websocket_health(self) -> Optional[Dict[str, Any]]:
        """
        Get WebSocket health metrics.
        
        Returns:
            Dictionary with health metrics or None if WebSocket not initialized
        """
        if self._ws_client:
            return self._ws_client.get_health_metrics()
        return None
    
    def get_deduplication_stats(self) -> Optional[Dict[str, Any]]:
        """
        Get WebSocket event deduplication statistics.
        
        Shows how many duplicate events were blocked during hot-swap reconnections.
        
        Returns:
            Dictionary with deduplication stats or None if WebSocket not initialized
        """
        if self._ws_client:
            return self._ws_client.get_deduplication_stats()
        return None

