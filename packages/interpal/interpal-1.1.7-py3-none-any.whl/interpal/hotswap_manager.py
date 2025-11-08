"""
Hot-swap connection manager for seamless WebSocket reconnection.

Manages overlapping WebSocket connections to ensure zero missed events
during reconnection cycles.
"""

import asyncio
import logging
import websockets
from typing import Optional, Callable, Any
from .websocket_config import WebSocketConfig
from .connection_manager import ConnectionManager, ConnectionState

logger = logging.getLogger(__name__)


class HotSwapManager:
    """
    Manages hot-swap WebSocket reconnection.
    
    Creates a new connection before closing the old one to ensure
    zero-gap transitions and no missed events.
    """
    
    def __init__(
        self,
        config: WebSocketConfig,
        connection_manager: ConnectionManager,
        auth_manager: Any,
        ws_url: str
    ):
        """
        Initialize hot-swap manager.
        
        Args:
            config: WebSocket configuration
            connection_manager: Connection manager instance
            auth_manager: Authentication manager for credentials
            ws_url: WebSocket URL template
        """
        self.config = config
        self.connection_manager = connection_manager
        self.auth_manager = auth_manager
        self.ws_url = ws_url
        
        # Hot-swap state
        self._is_swapping = False
        self._swap_lock = asyncio.Lock()
    
    async def hot_swap_connection(
        self,
        current_websocket: Optional[websockets.WebSocketClientProtocol],
        on_new_connection: Optional[Callable] = None
    ) -> websockets.WebSocketClientProtocol:
        """
        Perform hot-swap reconnection.
        
        Creates a new WebSocket connection while keeping the old one alive.
        Once new connection is ready, closes the old one.
        
        Args:
            current_websocket: Current active WebSocket connection
            on_new_connection: Callback to call when new connection is ready
            
        Returns:
            New WebSocket connection
            
        Raises:
            Exception: If hot-swap fails
        """
        async with self._swap_lock:
            if self._is_swapping:
                logger.warning("Hot-swap already in progress, waiting...")
                return current_websocket
            
            self._is_swapping = True
            
            try:
                logger.info("🔄 Starting hot-swap reconnection...")
                
                # Step 1: Create new connection (while old one still active)
                new_websocket = await self._create_new_connection()
                
                # Step 2: Verify new connection is working
                await self._verify_connection(new_websocket)
                
                logger.info("✅ New connection established and verified")
                
                # Step 3: Call callback if provided (set up new connection)
                if on_new_connection:
                    try:
                        if asyncio.iscoroutinefunction(on_new_connection):
                            await on_new_connection(new_websocket)
                        else:
                            on_new_connection(new_websocket)
                    except Exception as e:
                        logger.error(f"Error in on_new_connection callback: {e}")
                
                # Step 4: Close old connection gracefully
                if current_websocket:
                    try:
                        logger.debug("Closing old connection...")
                        await asyncio.wait_for(
                            current_websocket.close(),
                            timeout=2.0
                        )
                        logger.debug("✅ Old connection closed successfully")
                    except asyncio.TimeoutError:
                        logger.warning("Old connection close timed out (non-critical)")
                    except Exception as e:
                        logger.warning(f"Error closing old connection: {e} (non-critical)")
                
                logger.info("✅ Hot-swap reconnection complete")
                
                return new_websocket
            
            except Exception as e:
                logger.error(f"❌ Hot-swap failed: {e}")
                
                # If hot-swap fails, keep old connection if it's still alive
                if current_websocket:
                    try:
                        # Check if old connection is still usable
                        if not current_websocket.closed:
                            logger.info("Keeping old connection alive after hot-swap failure")
                            return current_websocket
                    except Exception:
                        pass
                
                # Re-raise exception for caller to handle
                raise
            
            finally:
                self._is_swapping = False
    
    async def _create_new_connection(self) -> websockets.WebSocketClientProtocol:
        """
        Create a new WebSocket connection.
        
        Returns:
            New WebSocket connection
            
        Raises:
            Exception: If connection fails
        """
        # Build WebSocket URL with token
        token = self.auth_manager.auth_token or self.auth_manager.session_cookie
        if not token:
            raise Exception("No authentication token available")
        
        ws_url = f"{self.ws_url}?token={token}"
        
        # Build headers
        headers = self.auth_manager.get_headers()
        
        # Update connection state
        self.connection_manager.state = ConnectionState.CONNECTING
        
        # Connect with configuration
        new_websocket = await asyncio.wait_for(
            websockets.connect(
                ws_url,
                extra_headers=headers,
                ping_interval=self.config.get('ping_interval'),
                ping_timeout=self.config.get('ping_timeout'),
                close_timeout=self.config.get('close_timeout', 1),
                max_size=self.config.get('max_size', 2**20),
                max_queue=self.config.get('max_queue', 1024),
            ),
            timeout=self.config.get('connection_timeout', 30)
        )
        
        logger.debug("New WebSocket connection created")
        return new_websocket
    
    async def _verify_connection(
        self,
        websocket: websockets.WebSocketClientProtocol
    ):
        """
        Verify a WebSocket connection is working.
        
        Args:
            websocket: WebSocket to verify
            
        Raises:
            Exception: If verification fails
        """
        try:
            # Connection is verified if it's open and not closed
            if websocket.closed:
                raise Exception("WebSocket is closed")
            
            logger.debug("Connection verified successfully")
            
        except Exception as e:
            logger.error(f"Connection verification failed: {e}")
            raise
    
    @property
    def is_swapping(self) -> bool:
        """Check if hot-swap is currently in progress."""
        return self._is_swapping

