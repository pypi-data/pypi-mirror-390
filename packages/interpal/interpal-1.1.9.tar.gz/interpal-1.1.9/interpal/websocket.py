"""
Production-grade WebSocket client built on the standalone implementation found in
`websockelogic.py`, adapted for the Interpal library.

This module wires the production client into the existing Interpal event system,
providing both asynchronous and synchronous interfaces.
"""

from __future__ import annotations

import asyncio
import inspect
import json
import logging
import random
import threading
import time
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Coroutine, Dict, List, Optional

import websocket

from .auth import AuthManager
from .exceptions import (
    WebSocketAuthenticationError,
    WebSocketConnectionError,
    WebSocketError,
    WebSocketTimeoutError,
)
from .models.events import CounterUpdateEvent, ThreadNewMessageEvent, ThreadTypingEvent

logger = logging.getLogger(__name__)


class ConnectionState(Enum):
    """WebSocket connection states."""

    DISCONNECTED = 0
    CONNECTING = 1
    CONNECTED = 2
    RECONNECTING = 3
    CLOSED = 4


class WebSocketConfig:
    """Configuration matching the production client defaults."""

    # Connection timeouts
    CONNECT_TIMEOUT = 10  # seconds
    SOCKET_TIMEOUT = 60

    # Keep-alive
    PING_INTERVAL = 20
    PING_TIMEOUT = 10

    # Reconnection strategy
    RECONNECT_BASE_DELAY = 2
    RECONNECT_MAX_DELAY = 60
    RECONNECT_BACKOFF = 1.5
    MAX_RECONNECT_ATTEMPTS = None  # Infinite by default

    # Message handling
    MAX_MESSAGE_SIZE = 16 * 1024 * 1024  # 16 MB
    MAX_QUEUE_SIZE = 100

    # Compression
    COMPRESSION = "permessage-deflate"


class ProductionWebSocketClient:
    """
    Production-ready WebSocket client based on Android APK analysis.

    This implementation provides ping/pong keep-alive, exponential backoff,
    explicit state tracking, and message queueing.
    """

    def __init__(
        self,
        url: str,
        on_message: Optional[Callable[[str], None]] = None,
        on_connected: Optional[Callable[[], None]] = None,
        on_disconnected: Optional[Callable[[int, str], None]] = None,
        on_error: Optional[Callable[[Exception], None]] = None,
        config: Optional[WebSocketConfig] = None,
        headers: Optional[List[str]] = None,
    ):
        self.url = url
        self.config = config or WebSocketConfig()
        self.headers = headers or []

        # Callbacks
        self.on_message_callback = on_message
        self.on_connected_callback = on_connected
        self.on_disconnected_callback = on_disconnected
        self.on_error_callback = on_error

        # State management
        self.state = ConnectionState.DISCONNECTED
        self.ws: Optional[websocket.WebSocketApp] = None
        self.thread: Optional[threading.Thread] = None
        self.running = False
        self.reconnect_attempts = 0

        # Statistics
        self.connect_time: Optional[datetime] = None
        self.last_message_time: Optional[datetime] = None
        self.messages_sent = 0
        self.messages_received = 0
        self.pings_sent = 0
        self.pongs_received = 0

        logger.info("WebSocket client initialized for %s", url)
        logger.info(
            "Ping interval: %ss (enables keep-alive missing in Android client)",
            self.config.PING_INTERVAL,
        )

    def connect(self) -> None:
        """Start WebSocket connection with automatic reconnection."""
        if self.state == ConnectionState.CLOSED:
            raise RuntimeError("Cannot connect: client has been closed")

        if self.state in {ConnectionState.CONNECTING, ConnectionState.CONNECTED}:
            logger.warning("Already connected or connecting")
            return

        logger.info("Starting WebSocket connection...")
        self.running = True
        self.state = ConnectionState.CONNECTING
        self._start_connection_thread()

    def _start_connection_thread(self) -> None:
        """Create and start the connection thread."""
        self.ws = websocket.WebSocketApp(
            self.url,
            header=self.headers,
            on_open=self._on_open,
            on_message=self._on_message,
            on_error=self._on_error,
            on_close=self._on_close,
            on_ping=self._on_ping,
            on_pong=self._on_pong,
        )

        self.thread = threading.Thread(
            target=self._run_forever,
            daemon=True,
            name="WebSocket-Client",
        )
        self.thread.start()
        logger.info("Connection thread started")

    def _run_forever(self) -> None:
        """Main connection loop with automatic reconnection."""
        while self.running:
            try:
                logger.info("Attempting to connect to %s", self.url)
                self.ws.run_forever(
                    ping_interval=self.config.PING_INTERVAL,
                    ping_timeout=self.config.PING_TIMEOUT,
                    skip_utf8_validation=False,
                )
            except Exception as exc:  # pragma: no cover - defensive logging
                logger.error("WebSocket run_forever error: %s", exc, exc_info=True)

            if self.running and self.state != ConnectionState.CLOSED:
                self._handle_reconnection()

        logger.info("Connection loop exited")

    def _handle_reconnection(self) -> None:
        """Handle reconnection with exponential backoff and jitter."""
        if self.state == ConnectionState.CLOSED:
            return

        self.state = ConnectionState.RECONNECTING
        self.reconnect_attempts += 1

        delay = min(
            self.config.RECONNECT_BASE_DELAY
            * (self.config.RECONNECT_BACKOFF ** (self.reconnect_attempts - 1)),
            self.config.RECONNECT_MAX_DELAY,
        )

        jitter = delay * 0.2 * (random.random() * 2 - 1)
        delay = max(0.1, delay + jitter)

        logger.warning(
            "Reconnecting in %.1fs (attempt %s)",
            delay,
            self.reconnect_attempts,
        )

        if (
            self.config.MAX_RECONNECT_ATTEMPTS is not None
            and self.reconnect_attempts >= self.config.MAX_RECONNECT_ATTEMPTS
        ):
            logger.error("Max reconnection attempts reached")
            self.close()
            return

        time.sleep(delay)

    def _on_open(self, ws: websocket.WebSocketApp) -> None:
        """Handle successful connection establishment."""
        self.state = ConnectionState.CONNECTED
        self.connect_time = datetime.now()
        self.reconnect_attempts = 0

        logger.info("✅ WebSocket connected successfully")
        logger.info(
            "Ping/pong keep-alive enabled (every %ss)", self.config.PING_INTERVAL
        )

        if self.on_connected_callback:
            try:
                self.on_connected_callback()
            except Exception as exc:  # pragma: no cover - user callback
                logger.error("Error in on_connected callback: %s", exc)

    def _on_message(self, ws: websocket.WebSocketApp, message: str) -> None:
        """Handle incoming messages."""
        self.last_message_time = datetime.now()
        self.messages_received += 1

        if self.on_message_callback:
            try:
                self.on_message_callback(message)
            except Exception as exc:  # pragma: no cover - user callback
                logger.error("Error in on_message callback: %s", exc)

    def _on_error(self, ws: websocket.WebSocketApp, error: Exception) -> None:
        """Handle connection errors."""
        logger.error("WebSocket error: %s", error)

        if self.on_error_callback:
            try:
                self.on_error_callback(error)
            except Exception as exc:  # pragma: no cover - user callback
                logger.error("Error in on_error callback: %s", exc)

    def _on_close(
        self,
        ws: websocket.WebSocketApp,
        close_status_code: int,
        close_msg: str,
    ) -> None:
        """Handle closed connection."""
        if self.connect_time:
            duration = (datetime.now() - self.connect_time).total_seconds()
            logger.info(
                "WebSocket closed: %s - %s (connected for %.1fs)",
                close_status_code,
                close_msg,
                duration,
            )
        else:
            logger.info("WebSocket closed: %s - %s", close_status_code, close_msg)

        if self.state != ConnectionState.CLOSED:
            self.state = ConnectionState.DISCONNECTED

        if self.on_disconnected_callback:
            try:
                self.on_disconnected_callback(close_status_code, close_msg)
            except Exception as exc:  # pragma: no cover - user callback
                logger.error("Error in on_disconnected callback: %s", exc)

    def _on_ping(self, ws: websocket.WebSocketApp, message: bytes) -> None:
        """Handle server ping."""
        logger.debug("Received ping from server")

    def _on_pong(self, ws: websocket.WebSocketApp, message: bytes) -> None:
        """Handle server pong responses."""
        self.pongs_received += 1
        logger.debug("Received pong from server (total: %s)", self.pongs_received)

    def send(self, message: str) -> bool:
        """Send a message if connected."""
        if self.state == ConnectionState.CONNECTED and self.ws:
            try:
                self.ws.send(message)
                self.messages_sent += 1
                logger.debug("Sent message (%d bytes)", len(message))
                return True
            except Exception as exc:
                logger.error("Failed to send message: %s", exc)
                return False
        logger.error(
            "Cannot send message: not connected (state: %s)", self.state.name
        )
        return False

    def close(self, code: int = 1000, reason: str = "Client closing") -> None:
        """Gracefully close the connection."""
        logger.info("Closing WebSocket: %s - %s", code, reason)
        self.running = False
        self.state = ConnectionState.CLOSED

        if self.ws:
            try:
                self.ws.close(code, reason)
            except Exception as exc:
                logger.error("Error closing WebSocket: %s", exc)

        if self.thread and threading.current_thread() is not self.thread:
            logger.info("Waiting for connection thread to exit...")
            self.thread.join(timeout=5)
            if self.thread.is_alive():
                logger.warning("Connection thread did not exit cleanly")
            else:
                logger.info("Connection thread exited")

    def get_state(self) -> ConnectionState:
        """Return the current connection state."""
        return self.state

    def get_statistics(self) -> Dict[str, Any]:
        """Return connection statistics."""
        uptime = None
        if self.connect_time and self.state == ConnectionState.CONNECTED:
            uptime = (datetime.now() - self.connect_time).total_seconds()

        return {
            "state": self.state.name,
            "uptime_seconds": uptime,
            "messages_sent": self.messages_sent,
            "messages_received": self.messages_received,
            "pongs_received": self.pongs_received,
            "reconnect_attempts": self.reconnect_attempts,
        }

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return (
            f"<WebSocketClient url={self.url} "
            f"state={self.state.name} "
            f"messages_rx={self.messages_received}>"
        )


class WebSocketClient:
    """Async wrapper integrating the production client with event handlers."""

    WS_URL = "wss://api.interpals.net/v1/ws"

    def __init__(
        self,
        auth_manager: AuthManager,
        config: Optional[WebSocketConfig] = None,
    ) -> None:
        self.auth = auth_manager
        self.config = config or WebSocketConfig()
        self.event_handlers: Dict[str, List[Callable]] = {}

        self._client: Optional[ProductionWebSocketClient] = None
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._connected_event: Optional[asyncio.Event] = None
        self._stop_event: Optional[asyncio.Event] = None
        self._manual_close = False
        self._running = False
        self._last_error: Optional[Exception] = None

    # ------------------------------------------------------------------
    # Event registration helpers
    # ------------------------------------------------------------------

    def on(self, event_name: str) -> Callable:
        """Decorator for subscribing to WebSocket events."""

        def decorator(func: Callable) -> Callable:
            self.event_handlers.setdefault(event_name, []).append(func)
            return func

        return decorator

    def register_event(self, event_name: str, handler: Callable) -> None:
        """Register an event handler programmatically."""
        self.event_handlers.setdefault(event_name, []).append(handler)

    async def emit_event(self, event_name: str, data: Any = None) -> None:
        """Invoke all handlers registered for the given event."""
        handlers = self.event_handlers.get(event_name, [])
        if not handlers:
            return

        for handler in handlers:
            try:
                signature = inspect.signature(handler)
                accepts_args = any(
                    param.kind
                    not in (
                        inspect.Parameter.VAR_POSITIONAL,
                        inspect.Parameter.VAR_KEYWORD,
                    )
                    for param in signature.parameters.values()
                )

                if asyncio.iscoroutinefunction(handler):
                    if accepts_args:
                        await handler(data)
                    else:
                        await handler()
                else:
                    if accepts_args:
                        handler(data)
                    else:
                        handler()
            except Exception as exc:  # pragma: no cover - handler isolation
                logger.exception("Error in '%s' handler: %s", event_name, exc)

    # ------------------------------------------------------------------
    # Connection management
    # ------------------------------------------------------------------

    async def connect(self) -> None:
        """Establish the WebSocket connection."""
        if not self.auth.is_authenticated:
            raise WebSocketAuthenticationError(
                "Not authenticated - cannot connect to WebSocket"
            )

        token = self.auth.auth_token or self.auth.session_cookie
        if not token:
            raise WebSocketAuthenticationError("No authentication token available")

        headers_dict = self.auth.get_headers()
        header_list = [
            f"{key}: {value}"
            for key, value in headers_dict.items()
            if value is not None
        ]
        url = f"{self.WS_URL}?token={token}"

        self._loop = asyncio.get_running_loop()
        self._connected_event = asyncio.Event()
        self._stop_event = asyncio.Event()
        self._manual_close = False
        self._running = False
        self._last_error = None

        self._client = ProductionWebSocketClient(
            url=url,
            on_message=self._handle_raw_message,
            on_connected=self._handle_connected,
            on_disconnected=self._handle_disconnected,
            on_error=self._handle_error,
            config=self.config,
            headers=header_list,
        )

        await asyncio.to_thread(self._client.connect)

        try:
            await asyncio.wait_for(
                self._connected_event.wait(),
                timeout=self.config.CONNECT_TIMEOUT,
            )
        except asyncio.TimeoutError as exc:
            await asyncio.to_thread(self._client.close)
            self._client = None
            message = str(self._last_error) if self._last_error else "Connection timeout"
            raise WebSocketTimeoutError(message) from exc
        except Exception as exc:
            await asyncio.to_thread(self._client.close)
            self._client = None
            raise WebSocketConnectionError(str(exc)) from exc

    async def disconnect(self) -> None:
        """Close the WebSocket connection."""
        if not self._client:
            return
        
        self._manual_close = True
        await asyncio.to_thread(self._client.close)

        if self._loop and self._stop_event:
            self._loop.call_soon_threadsafe(self._stop_event.set)

        self._client = None
        self._running = False

    async def start(self) -> None:
        """Convenience coroutine that connects and then waits for closure."""
        await self.connect()
        await self.listen()

    async def listen(self) -> None:
        """Block until the connection is fully closed."""
        if self._stop_event is None:
            self._stop_event = asyncio.Event()
        await self._stop_event.wait()

    async def send(self, data: Dict[str, Any]) -> None:
        """Send a JSON payload through the WebSocket."""
        if not self._client:
            raise WebSocketError("WebSocket not connected")

        message = json.dumps(data)
        success = await asyncio.to_thread(self._client.send, message)
        if not success:
            raise WebSocketError("Failed to send message")

    # ------------------------------------------------------------------
    # Callback handlers (executed on background threads)
    # ------------------------------------------------------------------

    def _schedule(self, coro: Coroutine[Any, Any, Any]) -> None:
        """Schedule a coroutine safely on the stored event loop."""
        if not self._loop:
            return
        asyncio.run_coroutine_threadsafe(coro, self._loop)

    def _handle_connected(self) -> None:
        self._running = True
        if self._loop and self._connected_event:
            self._loop.call_soon_threadsafe(self._connected_event.set)
        self._schedule(self.emit_event("on_ready"))

    def _handle_disconnected(self, code: int, reason: str) -> None:
        self._running = False
        client_closed = self._client and self._client.get_state() == ConnectionState.CLOSED

        if self._manual_close or client_closed:
            if self._loop and self._stop_event:
                self._loop.call_soon_threadsafe(self._stop_event.set)
            self._schedule(self.emit_event("on_disconnect"))
            self._manual_close = False

    def _handle_error(self, error: Exception) -> None:
        self._last_error = error
        self._schedule(self.emit_event("on_error", error))

    def _handle_raw_message(self, message: str) -> None:
        self._schedule(self._dispatch_message(message))

    async def _dispatch_message(self, message: str) -> None:
        try:
            data = json.loads(message)
        except json.JSONDecodeError:
            logger.warning("Failed to decode WebSocket message: %s", message)
            return

        event_type = data.get("type", data.get("event"))
        if not event_type:
            return

        event_map = {
            "THREAD_NEW_MESSAGE": "on_message",
            "THREAD_TYPING": "on_typing",
            "COUNTER_UPDATE": "on_notification",
            "notification": "on_notification",
            "status": "on_status_change",
            "user_online": "on_user_online",
            "user_offline": "on_user_offline",
        }
        event_name = event_map.get(event_type, f"on_{event_type.lower()}")

        if event_type == "THREAD_NEW_MESSAGE":
            payload = ThreadNewMessageEvent(state=None, data=data)
        elif event_type == "THREAD_TYPING":
            payload = ThreadTypingEvent(state=None, data=data)
        elif event_type == "COUNTER_UPDATE":
            payload = CounterUpdateEvent(state=None, data=data)
        else:
            payload = data.get("data", data)

        await self.emit_event(event_name, payload)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @property
    def is_connected(self) -> bool:
        """Return True when the underlying connection is active."""
        return bool(
            self._client
            and self._client.get_state() == ConnectionState.CONNECTED
            and self._running
        )

    def get_statistics(self) -> Optional[Dict[str, Any]]:
        """Expose statistics from the production client."""
        if self._client:
            return self._client.get_statistics()
        return None


class SyncWebSocketClient:
    """Threaded wrapper around :class:`WebSocketClient` for synchronous usage."""
    
    def __init__(
        self,
        auth_manager: AuthManager,
        config: Optional[WebSocketConfig] = None,
    ) -> None:
        self.auth = auth_manager
        self._async_client = WebSocketClient(auth_manager, config=config)
        self._thread: Optional[threading.Thread] = None
        self._loop: Optional[asyncio.AbstractEventLoop] = None
    
    def on(self, event_name: str) -> Callable:
        """Decorator for registering event handlers."""
        return self._async_client.on(event_name)
    
    def register_event(self, event_name: str, handler: Callable) -> None:
        """Register a handler programmatically."""
        self._async_client.register_event(event_name, handler)
    
    def connect(self) -> None:
        """Start the WebSocket client in a background thread."""
        if self._thread and self._thread.is_alive():
            return
        
        def run_loop() -> None:
            loop = asyncio.new_event_loop()
            self._loop = loop
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(self._async_client.start())
            finally:
                loop.close()
        
        self._thread = threading.Thread(target=run_loop, daemon=True)
        self._thread.start()
    
    def disconnect(self) -> None:
        """Stop the WebSocket client."""
        if not self._loop:
            return

        future = asyncio.run_coroutine_threadsafe(
                self._async_client.disconnect(),
            self._loop,
        )
        try:
            future.result(timeout=5)
        except Exception:
            logger.warning("Timed out waiting for WebSocket disconnect")

        self._loop.call_soon_threadsafe(self._loop.stop)
        if self._thread:
            self._thread.join(timeout=5)

        self._loop = None
        self._thread = None

    def send(self, data: Dict[str, Any]) -> None:
        """Send data via the underlying async client."""
        if not self._loop:
            raise WebSocketError("WebSocket not connected")

        future = asyncio.run_coroutine_threadsafe(
                self._async_client.send(data),
            self._loop,
        )
        future.result()

    @property
    def is_connected(self) -> bool:
        """Return True if the async client reports an active connection."""
        return self._async_client.is_connected

    def get_statistics(self) -> Optional[Dict[str, Any]]:
        """Proxy statistics from the underlying async client."""
        return self._async_client.get_statistics()
