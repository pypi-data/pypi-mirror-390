"""
WebSocket client for real-time events and notifications.
"""

import json
import asyncio
import websockets
import threading
import inspect
from typing import Optional, Dict, Any, Callable, List
from .exceptions import WebSocketError
from .auth import AuthManager
from .models.events import ThreadNewMessageEvent, ThreadTypingEvent, CounterUpdateEvent


class WebSocketClient:
    """
    Asynchronous WebSocket client for real-time Interpals events.
    """
    
    WS_URL = "wss://api.interpals.net/v1/ws"
    
    def __init__(self, auth_manager: AuthManager):
        """
        Initialize WebSocket client.
        
        Args:
            auth_manager: Authentication manager instance
        """
        self.auth = auth_manager
        self.websocket: Optional[websockets.WebSocketClientProtocol] = None
        self.event_handlers: Dict[str, List[Callable]] = {}
        self._running = False
        self._reconnect_attempts = 0
        self._max_reconnect_attempts = 5
        self._reconnect_delay = 2
    
    def on(self, event_name: str):
        """
        Decorator for registering event handlers.
        
        Args:
            event_name: Name of the event to listen for
            
        Example:
            @ws_client.on('on_message')
            async def handle_message(data):
                print(f"New message: {data}")
        """
        def decorator(func: Callable):
            if event_name not in self.event_handlers:
                self.event_handlers[event_name] = []
            self.event_handlers[event_name].append(func)
            return func
        return decorator
    
    def register_event(self, event_name: str, handler: Callable):
        """
        Register an event handler programmatically.
        
        Args:
            event_name: Name of the event
            handler: Async function to handle the event
        """
        if event_name not in self.event_handlers:
            self.event_handlers[event_name] = []
        self.event_handlers[event_name].append(handler)
    
    async def emit_event(self, event_name: str, data: Any = None):
        """
        Emit an event to all registered handlers.
        
        Args:
            event_name: Name of the event
            data: Event data to pass to handlers
        """
        if event_name in self.event_handlers:
            for handler in self.event_handlers[event_name]:
                try:
                    # Check function signature to see if it accepts parameters
                    sig = inspect.signature(handler)
                    params = [p for p in sig.parameters.values() if p.kind not in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD)]
                    
                    # Call handler with or without data based on signature
                    if asyncio.iscoroutinefunction(handler):
                        if len(params) == 0:
                            # Handler takes no arguments (e.g., on_ready)
                            await handler()
                        else:
                            # Handler takes at least one argument
                            await handler(data)
                    else:
                        if len(params) == 0:
                            handler()
                        else:
                            handler(data)
                except Exception as e:
                    print(f"Error in event handler for {event_name}: {e}")
    
    async def connect(self):
        """
        Establish WebSocket connection.
        
        Raises:
            WebSocketError: If connection fails
        """
        if not self.auth.is_authenticated:
            raise WebSocketError("Not authenticated - cannot connect to WebSocket")
        
        try:
            # Build WebSocket URL with token query parameter
            token = self.auth.auth_token or self.auth.session_cookie
            if not token:
                raise WebSocketError("No authentication token available")
            
            ws_url = f"{self.WS_URL}?token={token}"
            
            # Build connection headers with auth
            headers = self.auth.get_headers()
            
            # Connect to WebSocket
            self.websocket = await websockets.connect(
                ws_url,
                extra_headers=headers,
                ping_interval=20,
                ping_timeout=10,
            )
            
            self._running = True
            self._reconnect_attempts = 0
            
            # Emit ready event
            await self.emit_event('on_ready')
            
        except Exception as e:
            print(f"❌ WebSocket connection failed: {str(e)}")
            raise WebSocketError(f"Failed to connect to WebSocket: {str(e)}")
    
    async def disconnect(self):
        """Close WebSocket connection."""
        self._running = False
        if self.websocket:
            await self.websocket.close()
            self.websocket = None
    
    async def _handle_message(self, message: str):
        """
        Parse and handle incoming WebSocket message.
        
        Args:
            message: Raw message string from WebSocket
        """
        try:
            data = json.loads(message)
            event_type = data.get('type', data.get('event'))
            
            if not event_type:
                return
            
            # Map Interpals event types to handler names
            event_map = {
                'THREAD_NEW_MESSAGE': 'on_message',
                'THREAD_TYPING': 'on_typing',
                'COUNTER_UPDATE': 'on_notification',
                'notification': 'on_notification',
                'status': 'on_status_change',
                'user_online': 'on_user_online',
                'user_offline': 'on_user_offline',
            }
            
            event_name = event_map.get(event_type, f'on_{event_type.lower()}')
            
            
            # Convert raw event data to proper models
            if event_type == 'THREAD_NEW_MESSAGE':
                # Create ThreadNewMessageEvent model with all data
                event = ThreadNewMessageEvent(state=None, data=data)
                # print(f"Message event: {event}")
                await self.emit_event(event_name, event)
            
            elif event_type == 'THREAD_TYPING':
                # Create ThreadTypingEvent model
                event = ThreadTypingEvent(state=None, data=data)
                await self.emit_event(event_name, event)
            
            elif event_type == 'COUNTER_UPDATE':
                # Create CounterUpdateEvent model
                event = CounterUpdateEvent(state=None, data=data)
                await self.emit_event(event_name, event)
            
            else:
                # For other events, pass raw data
                await self.emit_event(event_name, data.get('data', data))
        
        except json.JSONDecodeError:
            print(f"Failed to parse WebSocket message: {message}")
        except Exception as e:
            print(f"Error handling WebSocket message: {e}")
    
    async def listen(self):
        """
        Listen for incoming WebSocket messages.
        This should be run as a background task.
        """
        if not self.websocket:
            await self.connect()
        
        try:
            async for message in self.websocket:
                await self._handle_message(message)
        
        except websockets.ConnectionClosed as e:
            print(f"⚠️  WebSocket connection closed: {e}")
            if self._running:
                # Attempt to reconnect
                await self._reconnect()
        
        except Exception as e:
            print(f"❌ WebSocket error: {e}")
            if self._running:
                await self._reconnect()
    
    async def _reconnect(self):
        """
        Attempt to reconnect to WebSocket with exponential backoff.
        """
        if self._reconnect_attempts >= self._max_reconnect_attempts:
            print(f"Max reconnection attempts ({self._max_reconnect_attempts}) reached")
            self._running = False
            await self.emit_event('on_disconnect')
            return
        
        self._reconnect_attempts += 1
        delay = self._reconnect_delay * (2 ** (self._reconnect_attempts - 1))
        
        print(f"Reconnecting in {delay} seconds... (attempt {self._reconnect_attempts})")
        await asyncio.sleep(delay)
        
        try:
            await self.connect()
            await self.listen()
        except Exception as e:
            print(f"Reconnection failed: {e}")
            await self._reconnect()
    
    async def send(self, data: Dict[str, Any]):
        """
        Send data through WebSocket.
        
        Args:
            data: Dictionary to send as JSON
            
        Raises:
            WebSocketError: If not connected or send fails
        """
        if not self.websocket:
            raise WebSocketError("WebSocket not connected")
        
        try:
            message = json.dumps(data)
            await self.websocket.send(message)
        except Exception as e:
            raise WebSocketError(f"Failed to send message: {str(e)}")
    
    async def start(self):
        """
        Start the WebSocket client and begin listening.
        This is a convenience method that connects and listens.
        """
        await self.connect()
        await self.listen()


class SyncWebSocketClient:
    """
    Synchronous wrapper for WebSocket client using threading.
    """
    
    def __init__(self, auth_manager: AuthManager):
        """
        Initialize synchronous WebSocket client.
        
        Args:
            auth_manager: Authentication manager instance
        """
        self.auth = auth_manager
        self._async_client = WebSocketClient(auth_manager)
        self._thread: Optional[threading.Thread] = None
        self._loop: Optional[asyncio.AbstractEventLoop] = None
    
    def on(self, event_name: str):
        """
        Decorator for registering event handlers.
        
        Args:
            event_name: Name of the event to listen for
        """
        return self._async_client.on(event_name)
    
    def register_event(self, event_name: str, handler: Callable):
        """
        Register an event handler.
        
        Args:
            event_name: Name of the event
            handler: Function to handle the event
        """
        self._async_client.register_event(event_name, handler)
    
    def connect(self):
        """Establish WebSocket connection in a background thread."""
        if self._thread and self._thread.is_alive():
            return
        
        def run_loop():
            self._loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._loop)
            self._loop.run_until_complete(self._async_client.start())
        
        self._thread = threading.Thread(target=run_loop, daemon=True)
        self._thread.start()
    
    def disconnect(self):
        """Close WebSocket connection."""
        if self._loop:
            asyncio.run_coroutine_threadsafe(
                self._async_client.disconnect(),
                self._loop
            )
    
    def send(self, data: Dict[str, Any]):
        """
        Send data through WebSocket.
        
        Args:
            data: Dictionary to send as JSON
        """
        if self._loop:
            asyncio.run_coroutine_threadsafe(
                self._async_client.send(data),
                self._loop
            )

