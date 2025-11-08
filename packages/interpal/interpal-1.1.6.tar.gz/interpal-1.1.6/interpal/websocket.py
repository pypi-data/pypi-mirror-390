"""
WebSocket client for real-time events and notifications.
Enhanced with improved stability, health monitoring, and reconnection logic.
"""

import json
import asyncio
import websockets
import threading
import inspect
import logging
from typing import Optional, Dict, Any, Callable, List
from .exceptions import (
    WebSocketError,
    WebSocketConnectionError,
    WebSocketTimeoutError,
    WebSocketAuthenticationError
)
from .auth import AuthManager
from .models.events import ThreadNewMessageEvent, ThreadTypingEvent, CounterUpdateEvent
from .websocket_config import WebSocketConfig, ConnectionProfile
from .connection_manager import ConnectionManager, ConnectionState
from .event_deduplicator import EventDeduplicator
from .hotswap_manager import HotSwapManager

# Configure logging
logger = logging.getLogger(__name__)


class WebSocketClient:
    """
    Asynchronous WebSocket client for real-time Interpals events.
    Enhanced with improved stability, health monitoring, and adaptive reconnection.
    """
    
    WS_URL = "wss://api.interpals.net/v1/ws"
    
    def __init__(
        self,
        auth_manager: AuthManager,
        config: Optional[WebSocketConfig] = None,
        enable_health_monitoring: bool = True
    ):
        """
        Initialize WebSocket client.
        
        Args:
            auth_manager: Authentication manager instance
            config: WebSocket configuration (uses defaults if not provided)
            enable_health_monitoring: Enable connection health monitoring
        """
        self.auth = auth_manager
        self.config = config or WebSocketConfig()
        self.websocket: Optional[websockets.WebSocketClientProtocol] = None
        self.event_handlers: Dict[str, List[Callable]] = {}
        self._running = False
        self._enable_health_monitoring = enable_health_monitoring
        
        # Initialize connection manager
        self.connection_manager = ConnectionManager(
            config=self.config,
            on_state_change=self._on_state_change
        )
        
        # Event deduplicator (prevents duplicate events during hot-swap)
        self.event_deduplicator = EventDeduplicator(
            max_cache_size=1000,
            expiration_seconds=60.0
        )
        
        # Hot-swap manager for seamless reconnection
        self.hotswap_manager = HotSwapManager(
            config=self.config,
            connection_manager=self.connection_manager,
            auth_manager=self.auth,
            ws_url=self.WS_URL
        )
        
        # Health monitoring task
        self._health_check_task: Optional[asyncio.Task] = None
        
        # Proactive reconnection task (Interpals server closes every ~30s, we reconnect at 29s)
        self._proactive_reconnect_task: Optional[asyncio.Task] = None
        self._proactive_reconnect_interval = 29  # Reconnect every 29 seconds (before server's 30s)
    
    def _on_state_change(self, new_state: ConnectionState):
        """
        Handle connection state changes.
        
        Args:
            new_state: New connection state
        """
        logger.info(f"WebSocket state changed to: {new_state.value}")
        
        # Emit state change events (but skip on_ready as it's emitted in connect())
        state_event_map = {
            # ConnectionState.CONNECTED: 'on_ready',  # Emitted in connect() to avoid duplication
            ConnectionState.DISCONNECTED: 'on_disconnect',
            ConnectionState.RECONNECTING: 'on_reconnecting',
            ConnectionState.FAILED: 'on_connection_failed',
        }
        
        event_name = state_event_map.get(new_state)
        if event_name:
            # Schedule event emission
            try:
                asyncio.create_task(self.emit_event(event_name))
            except RuntimeError:
                # No event loop running, skip async event emission
                pass
    
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
                    logger.error(f"Error in event handler for {event_name}: {e}")
    
    async def connect(self):
        """
        Establish WebSocket connection with enhanced configuration.
        
        Raises:
            WebSocketAuthenticationError: If not authenticated
            WebSocketConnectionError: If connection fails
        """
        if not self.auth.is_authenticated:
            raise WebSocketAuthenticationError("Not authenticated - cannot connect to WebSocket")
        
        # Check if connection is allowed by connection manager
        if not self.connection_manager.can_connect():
            max_attempts = self.config.get('max_reconnect_attempts', 10)
            if self.connection_manager._reconnect_attempts >= max_attempts:
                raise WebSocketConnectionError(
                    f"Maximum reconnection attempts ({max_attempts}) reached"
                )
            if self.connection_manager.circuit_breaker and self.connection_manager.circuit_breaker.is_open:
                raise WebSocketConnectionError("Circuit breaker is open - connection attempts suspended")
        
        try:
            # Build WebSocket URL with token query parameter
            token = self.auth.auth_token or self.auth.session_cookie
            if not token:
                raise WebSocketAuthenticationError("No authentication token available")
            
            ws_url = f"{self.WS_URL}?token={token}"
            
            # Build connection headers with auth
            headers = self.auth.get_headers()
            
            # Update state
            self.connection_manager.state = ConnectionState.CONNECTING
            
            # Connect to WebSocket with enhanced configuration
            # Enable ping/pong with proper intervals to prevent 30-second disconnection
            self.websocket = await asyncio.wait_for(
                websockets.connect(
                    ws_url,
                    extra_headers=headers,
                    ping_interval=self.config.get('ping_interval', 30),
                    ping_timeout=self.config.get('ping_timeout', 15),
                    close_timeout=self.config.get('close_timeout', 1),
                    max_size=self.config.get('max_size', 2**20),
                    max_queue=self.config.get('max_queue', 1024),
                ),
                timeout=self.config.get('connection_timeout', 30)
            )
            
            self._running = True
            
            # Record successful connection
            self.connection_manager.on_connect_success()
            
            # Start health monitoring if enabled
            if self._enable_health_monitoring:
                self._start_health_monitoring()
            
            # Start proactive reconnection timer (reconnect before server closes at 30s)
            self._start_proactive_reconnect()
            
            # Emit ready event
            await self.emit_event('on_ready')
            
            logger.info("✅ WebSocket connected successfully")
            
        except asyncio.TimeoutError:
            logger.error("❌ WebSocket connection timeout")
            self.connection_manager.on_connect_failure()
            raise WebSocketTimeoutError("Connection timeout")
        except websockets.InvalidURI as e:
            logger.error(f"❌ Invalid WebSocket URI: {e}")
            self.connection_manager.on_connect_failure()
            raise WebSocketConnectionError(f"Invalid URI: {str(e)}")
        except websockets.InvalidHandshake as e:
            logger.error(f"❌ WebSocket handshake failed: {e}")
            self.connection_manager.on_connect_failure()
            raise WebSocketAuthenticationError(f"Authentication failed: {str(e)}")
        except Exception as e:
            logger.error(f"❌ WebSocket connection failed: {str(e)}")
            self.connection_manager.on_connect_failure()
            raise WebSocketConnectionError(f"Failed to connect to WebSocket: {str(e)}")
    
    def _start_health_monitoring(self):
        """Start background health monitoring task."""
        if self._health_check_task and not self._health_check_task.done():
            return  # Already running
        
        self._health_check_task = asyncio.create_task(self._health_monitoring_loop())
    
    def _start_proactive_reconnect(self):
        """Start proactive reconnection timer."""
        # Cancel existing timer if running
        if self._proactive_reconnect_task and not self._proactive_reconnect_task.done():
            self._proactive_reconnect_task.cancel()
        
        # Start new timer
        self._proactive_reconnect_task = asyncio.create_task(self._proactive_reconnect_loop())
    
    async def _health_monitoring_loop(self):
        """Background task for monitoring connection health."""
        while self._running and self.websocket:
            try:
                # Wait for health check interval
                await asyncio.sleep(self.config.get('health_check_interval', 60))
                
                # Perform health check
                if self.connection_manager.should_perform_health_check():
                    is_healthy = await self.connection_manager.perform_health_check(self.websocket)
                    
                    if not is_healthy:
                        logger.warning("⚠️  Connection health check failed")
                        await self.emit_event('on_health_warning')
                    
                    # Emit health status event
                    await self.emit_event('on_health_update', self.connection_manager.health.get_status())
            
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in health monitoring: {e}")
    
    async def _proactive_reconnect_loop(self):
        """
        Proactive hot-swap reconnection loop.
        
        The Interpals server closes connections every ~30 seconds.
        We proactively hot-swap at 29 seconds to avoid being disconnected.
        This ensures zero missed events with seamless overlapping connections.
        """
        try:
            while self._running:
                # Wait for proactive reconnection interval (29 seconds)
                await asyncio.sleep(self._proactive_reconnect_interval)
                
                if not self._running:
                    break
                
                logger.debug(f"🔄 Proactive hot-swap triggered (every {self._proactive_reconnect_interval}s)")
                
                # Perform hot-swap reconnection
                await self._perform_hotswap_reconnect()
                
        except asyncio.CancelledError:
            logger.debug("Proactive hot-swap loop cancelled")
        except Exception as e:
            logger.error(f"Error in proactive hot-swap loop: {e}")
    
    async def disconnect(self):
        """Close WebSocket connection gracefully."""
        self._running = False
        
        # Cancel proactive reconnection timer
        if self._proactive_reconnect_task and not self._proactive_reconnect_task.done():
            self._proactive_reconnect_task.cancel()
            try:
                await self._proactive_reconnect_task
            except asyncio.CancelledError:
                pass
        
        # Cancel health monitoring
        if self._health_check_task and not self._health_check_task.done():
            self._health_check_task.cancel()
            try:
                await self._health_check_task
            except asyncio.CancelledError:
                pass
        
        # Close WebSocket
        if self.websocket:
            try:
                await self.websocket.close()
            except Exception as e:
                logger.error(f"Error closing WebSocket: {e}")
            finally:
                self.websocket = None
        
        # Update state
        self.connection_manager.state = ConnectionState.DISCONNECTED
        
        logger.info("WebSocket disconnected")
    
    async def _handle_message(self, message: str):
        """
        Parse and handle incoming WebSocket message.
        
        Args:
            message: Raw message string from WebSocket
        """
        try:
            # Record message received
            self.connection_manager.health.metrics.record_message_received()
            self.connection_manager.health.record_successful_operation()
            
            data = json.loads(message)
            event_type = data.get('type', data.get('event'))
            
            if not event_type:
                return
            
            # Check for duplicate events (during hot-swap overlap)
            if not self.event_deduplicator.should_process_event(data):
                logger.debug(f"Skipping duplicate event: {event_type}")
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
            logger.error(f"Failed to parse WebSocket message: {message}")
            self.connection_manager.health.record_error()
        except Exception as e:
            logger.error(f"Error handling WebSocket message: {e}")
            self.connection_manager.health.record_error()
    
    async def listen(self):
        """
        Listen for incoming WebSocket messages.
        This should be run as a background task.
        
        We proactively reconnect every 28 seconds (before server closes at 30s).
        If server closes before that, we handle it gracefully.
        """
        if not self.websocket:
            await self.connect()
        
        try:
            async for message in self.websocket:
                await self._handle_message(message)
        
        except websockets.ConnectionClosed as e:
            # Server closed connection (either we missed the 28s timer, or server closed early)
            # This is normal behavior - reconnect immediately as fallback
            if self._running:
                logger.debug(f"Server closed connection - reconnecting immediately (fallback)...")
                # Don't count as error - this is expected server behavior
                await self._immediate_reconnect()
            else:
                logger.info("WebSocket stopped by user")
        
        except Exception as e:
            logger.error(f"❌ WebSocket error: {e}")
            self.connection_manager.health.record_error()
            
            if self._running:
                await self._reconnect()
    
    async def _perform_hotswap_reconnect(self):
        """
        Perform hot-swap reconnection.
        
        Creates new connection BEFORE closing old one to ensure zero missed events.
        Old and new connections briefly overlap, with deduplication preventing duplicate events.
        """
        try:
            # Use hot-swap manager to create new connection while keeping old alive
            old_websocket = self.websocket
            
            # Perform the hot-swap
            new_websocket = await self.hotswap_manager.hot_swap_connection(
                current_websocket=old_websocket,
                on_new_connection=None  # No special setup needed
            )
            
            # Update to new connection
            self.websocket = new_websocket
            
            # Record successful reconnection (hot-swap doesn't count as an error)
            self.connection_manager.on_connect_success()
            
            # Restart proactive timer (it was restarted when connect() was called in hot-swap)
            # No need to do anything, timer is already running
            
            logger.debug("✅ Hot-swap completed successfully")
            
        except Exception as e:
            # If hot-swap fails, fall back to normal reconnection with backoff
            logger.warning(f"Hot-swap failed: {e}, using normal reconnection...")
            self.websocket = None  # Clear failed connection
            await self._reconnect()
    
    async def _immediate_reconnect(self):
        """
        Immediately reconnect after server-initiated close (fallback).
        No delay, no error counting - this is a fallback if server closes before our proactive cycle.
        """
        try:
            # Don't count this as a reconnection attempt - it's normal behavior
            logger.debug("Performing immediate reconnect (fallback for server-side close)...")
            
            # Close old connection if still open
            if self.websocket:
                try:
                    await self.websocket.close()
                except Exception:
                    pass
                self.websocket = None
            
            # Reconnect immediately
            await self.connect()
            
            # Continue listening
            await self.listen()
            
        except Exception as e:
            # If immediate reconnect fails, fall back to normal reconnection with backoff
            logger.warning(f"Immediate reconnect failed: {e}, using normal reconnection...")
            await self._reconnect()
    
    async def _reconnect(self):
        """
        Attempt to reconnect to WebSocket with improved backoff strategy.
        Used for actual errors (not normal server-side closes).
        Includes jitter and circuit breaker pattern.
        """
        # Check if reconnection is allowed
        if not self.connection_manager.can_connect():
            logger.error("Reconnection not allowed by connection manager")
            self._running = False
            await self.emit_event('on_disconnect')
            return
        
        # Update state
        self.connection_manager.state = ConnectionState.RECONNECTING
        
        # Calculate delay with jitter
        delay = self.connection_manager.calculate_reconnect_delay()
        
        attempt = self.connection_manager._reconnect_attempts + 1
        max_attempts = self.config.get('max_reconnect_attempts', 10)
        
        logger.info(f"🔄 Reconnecting in {delay:.1f} seconds... (attempt {attempt}/{max_attempts})")
        await self.emit_event('on_reconnect_attempt', {'attempt': attempt, 'delay': delay})
        
        await asyncio.sleep(delay)
        
        try:
            # Record reconnection attempt
            self.connection_manager.health.metrics.record_reconnection()
            
            # Attempt to connect
            await self.connect()
            
            # If successful, start listening again
            await self.listen()
            
        except Exception as e:
            logger.error(f"❌ Reconnection failed: {e}")
            
            # Record failure
            self.connection_manager.on_connect_failure()
            
            # Try again if allowed
            if self.connection_manager.can_connect():
                await self._reconnect()
            else:
                logger.error(f"Maximum reconnection attempts ({max_attempts}) reached or circuit breaker opened")
                self._running = False
                self.connection_manager.state = ConnectionState.FAILED
                await self.emit_event('on_disconnect')
    
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
            
            # Record message sent
            self.connection_manager.health.metrics.record_message_sent()
            self.connection_manager.health.record_successful_operation()
            
        except Exception as e:
            self.connection_manager.health.record_error()
            raise WebSocketError(f"Failed to send message: {str(e)}")
    
    async def start(self):
        """
        Start the WebSocket client and begin listening.
        This is a convenience method that connects and listens.
        """
        await self.connect()
        await self.listen()
    
    def get_connection_status(self) -> Dict[str, Any]:
        """
        Get comprehensive connection status information.
        
        Returns:
            Dictionary with connection status and metrics
        """
        return self.connection_manager.get_status()
    
    def get_health_metrics(self) -> Dict[str, Any]:
        """
        Get connection health metrics.
        
        Returns:
            Dictionary with health metrics
        """
        return self.connection_manager.health.get_status()
    
    def get_deduplication_stats(self) -> Dict[str, Any]:
        """
        Get event deduplication statistics.
        
        Returns:
            Dictionary with deduplication stats
        """
        return self.event_deduplicator.get_stats()


class SyncWebSocketClient:
    """
    Synchronous wrapper for WebSocket client using threading.
    Enhanced with improved stability and configuration support.
    """
    
    def __init__(
        self,
        auth_manager: AuthManager,
        config: Optional[WebSocketConfig] = None,
        enable_health_monitoring: bool = True
    ):
        """
        Initialize synchronous WebSocket client.
        
        Args:
            auth_manager: Authentication manager instance
            config: WebSocket configuration (uses defaults if not provided)
            enable_health_monitoring: Enable connection health monitoring
        """
        self.auth = auth_manager
        self._async_client = WebSocketClient(
            auth_manager,
            config=config,
            enable_health_monitoring=enable_health_monitoring
        )
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
    
    def get_connection_status(self) -> Dict[str, Any]:
        """
        Get comprehensive connection status information.
        
        Returns:
            Dictionary with connection status and metrics
        """
        return self._async_client.get_connection_status()
    
    def get_health_metrics(self) -> Dict[str, Any]:
        """
        Get connection health metrics.
        
        Returns:
            Dictionary with health metrics
        """
        return self._async_client.get_health_metrics()
    
    def get_deduplication_stats(self) -> Dict[str, Any]:
        """
        Get event deduplication statistics.
        
        Returns:
            Dictionary with deduplication stats
        """
        return self._async_client.get_deduplication_stats()
