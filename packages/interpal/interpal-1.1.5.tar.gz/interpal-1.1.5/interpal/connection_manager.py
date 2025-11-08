"""
Advanced connection management for WebSocket connections.
Provides connection pooling, circuit breaker pattern, and adaptive reconnection strategies.
"""

import time
import random
import asyncio
from typing import Optional, Dict, Any, Callable, List
from enum import Enum
from .websocket_utils.connection_health import ConnectionHealth, NetworkQuality
from .websocket_config import WebSocketConfig


class ConnectionState(Enum):
    """WebSocket connection states."""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    RECONNECTING = "reconnecting"
    FAILED = "failed"
    CIRCUIT_OPEN = "circuit_open"


class CircuitBreaker:
    """
    Circuit breaker pattern implementation for connection failures.
    
    Prevents repeated connection attempts when failures indicate a systemic issue.
    """
    
    def __init__(
        self,
        failure_threshold: int = 5,
        cooldown_period: float = 60.0,
        success_threshold: int = 2
    ):
        """
        Initialize circuit breaker.
        
        Args:
            failure_threshold: Number of failures before opening circuit
            cooldown_period: Time to wait before attempting to close circuit (seconds)
            success_threshold: Number of successes needed to close circuit
        """
        self.failure_threshold = failure_threshold
        self.cooldown_period = cooldown_period
        self.success_threshold = success_threshold
        
        self._failure_count = 0
        self._success_count = 0
        self._state = "closed"  # closed, open, half_open
        self._last_failure_time: Optional[float] = None
    
    def record_success(self):
        """Record a successful operation."""
        if self._state == "half_open":
            self._success_count += 1
            if self._success_count >= self.success_threshold:
                self._close_circuit()
        elif self._state == "closed":
            self._failure_count = 0
    
    def record_failure(self):
        """Record a failed operation."""
        self._last_failure_time = time.time()
        
        if self._state == "half_open":
            self._open_circuit()
        elif self._state == "closed":
            self._failure_count += 1
            if self._failure_count >= self.failure_threshold:
                self._open_circuit()
    
    def _open_circuit(self):
        """Open the circuit (stop allowing operations)."""
        self._state = "open"
        self._failure_count = 0
        self._success_count = 0
    
    def _close_circuit(self):
        """Close the circuit (resume normal operations)."""
        self._state = "closed"
        self._failure_count = 0
        self._success_count = 0
    
    def can_attempt(self) -> bool:
        """Check if an operation attempt is allowed."""
        if self._state == "closed":
            return True
        
        if self._state == "open":
            # Check if cooldown period has elapsed
            if self._last_failure_time:
                elapsed = time.time() - self._last_failure_time
                if elapsed >= self.cooldown_period:
                    self._state = "half_open"
                    self._success_count = 0
                    return True
            return False
        
        # half_open state
        return True
    
    @property
    def is_open(self) -> bool:
        """Check if circuit is open."""
        return self._state == "open"
    
    @property
    def state(self) -> str:
        """Get current circuit state."""
        return self._state
    
    def reset(self):
        """Reset circuit breaker to initial state."""
        self._failure_count = 0
        self._success_count = 0
        self._state = "closed"
        self._last_failure_time = None


class ReconnectionStrategy:
    """
    Adaptive reconnection strategy with multiple backoff algorithms.
    """
    
    def __init__(
        self,
        base_delay: float = 2.0,
        max_delay: float = 60.0,
        jitter: float = 0.1,
        exponential: bool = True
    ):
        """
        Initialize reconnection strategy.
        
        Args:
            base_delay: Base delay between attempts (seconds)
            max_delay: Maximum delay between attempts (seconds)
            jitter: Random jitter factor (0.0-1.0)
            exponential: Use exponential backoff
        """
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.jitter = jitter
        self.exponential = exponential
    
    def calculate_delay(self, attempt: int) -> float:
        """
        Calculate delay for next reconnection attempt.
        
        Args:
            attempt: Current attempt number (1-indexed)
            
        Returns:
            Delay in seconds
        """
        if self.exponential:
            # Exponential backoff: delay = base * (2 ^ (attempt - 1))
            delay = self.base_delay * (2 ** (attempt - 1))
        else:
            # Linear backoff: delay = base * attempt
            delay = self.base_delay * attempt
        
        # Cap at max delay
        delay = min(delay, self.max_delay)
        
        # Add jitter
        if self.jitter > 0:
            jitter_amount = delay * self.jitter
            delay += random.uniform(-jitter_amount, jitter_amount)
        
        return max(0, delay)
    
    def adjust_for_quality(self, delay: float, quality: NetworkQuality) -> float:
        """
        Adjust delay based on network quality.
        
        Args:
            delay: Base delay
            quality: Current network quality
            
        Returns:
            Adjusted delay
        """
        adjustments = {
            NetworkQuality.EXCELLENT: 0.8,
            NetworkQuality.GOOD: 1.0,
            NetworkQuality.FAIR: 1.2,
            NetworkQuality.POOR: 1.5,
            NetworkQuality.CRITICAL: 2.0,
        }
        multiplier = adjustments.get(quality, 1.0)
        return delay * multiplier


class ConnectionManager:
    """
    Advanced connection manager for WebSocket connections.
    
    Handles connection lifecycle, health monitoring, reconnection strategies,
    and circuit breaker pattern.
    """
    
    def __init__(
        self,
        config: Optional[WebSocketConfig] = None,
        on_state_change: Optional[Callable[[ConnectionState], None]] = None
    ):
        """
        Initialize connection manager.
        
        Args:
            config: WebSocket configuration
            on_state_change: Callback for state changes
        """
        self.config = config or WebSocketConfig()
        self.on_state_change = on_state_change
        
        # Connection state
        self._state = ConnectionState.DISCONNECTED
        self._connection_start_time: Optional[float] = None
        
        # Health monitoring
        self.health = ConnectionHealth()
        
        # Circuit breaker
        self.circuit_breaker: Optional[CircuitBreaker] = None
        if self.config.get('enable_circuit_breaker'):
            self.circuit_breaker = CircuitBreaker(
                failure_threshold=self.config.get('circuit_breaker_threshold', 5),
                cooldown_period=self.config.get('circuit_breaker_cooldown', 60),
            )
        
        # Reconnection strategy
        self.reconnection_strategy = ReconnectionStrategy(
            base_delay=self.config.get('reconnect_delay', 2.0),
            jitter=self.config.get('reconnect_jitter', 0.1),
        )
        
        # Reconnection tracking
        self._reconnect_attempts = 0
        self._last_reconnect_time: Optional[float] = None
    
    @property
    def state(self) -> ConnectionState:
        """Get current connection state."""
        return self._state
    
    @state.setter
    def state(self, new_state: ConnectionState):
        """Set connection state and trigger callback."""
        if new_state != self._state:
            old_state = self._state
            self._state = new_state
            
            # Call state change callback if provided
            if self.on_state_change:
                try:
                    self.on_state_change(new_state)
                except Exception:
                    pass  # Don't let callback errors affect state management
    
    def can_connect(self) -> bool:
        """
        Check if a connection attempt is allowed.
        
        Returns:
            True if connection attempt is allowed
        """
        # Check circuit breaker
        if self.circuit_breaker and not self.circuit_breaker.can_attempt():
            self.state = ConnectionState.CIRCUIT_OPEN
            return False
        
        # Check max reconnection attempts
        max_attempts = self.config.get('max_reconnect_attempts', 10)
        if self._reconnect_attempts >= max_attempts:
            return False
        
        return True
    
    def on_connect_success(self):
        """Handle successful connection."""
        self.state = ConnectionState.CONNECTED
        self._connection_start_time = time.time()
        self._reconnect_attempts = 0
        
        # Reset circuit breaker
        if self.circuit_breaker:
            self.circuit_breaker.record_success()
        
        # Reset health monitoring
        self.health.reset()
    
    def on_connect_failure(self):
        """Handle connection failure."""
        self._reconnect_attempts += 1
        
        # Record failure in circuit breaker
        if self.circuit_breaker:
            self.circuit_breaker.record_failure()
        
        # Record error in health
        self.health.record_error()
        
        # Update state
        if self.circuit_breaker and self.circuit_breaker.is_open:
            self.state = ConnectionState.CIRCUIT_OPEN
        else:
            self.state = ConnectionState.RECONNECTING
    
    def calculate_reconnect_delay(self) -> float:
        """
        Calculate delay before next reconnection attempt.
        
        Returns:
            Delay in seconds
        """
        delay = self.reconnection_strategy.calculate_delay(self._reconnect_attempts)
        
        # Adjust for network quality
        delay = self.reconnection_strategy.adjust_for_quality(
            delay,
            self.health.quality
        )
        
        return delay
    
    def reset_reconnection(self):
        """Reset reconnection counter."""
        self._reconnect_attempts = 0
        self._last_reconnect_time = None
    
    def get_connection_uptime(self) -> float:
        """Get connection uptime in seconds."""
        if self._connection_start_time and self.state == ConnectionState.CONNECTED:
            return time.time() - self._connection_start_time
        return 0.0
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get comprehensive connection status.
        
        Returns:
            Dictionary with connection status information
        """
        status = {
            'state': self._state.value,
            'uptime': self.get_connection_uptime(),
            'reconnect_attempts': self._reconnect_attempts,
            'health': self.health.get_status(),
        }
        
        if self.circuit_breaker:
            status['circuit_breaker'] = {
                'state': self.circuit_breaker.state,
                'is_open': self.circuit_breaker.is_open,
            }
        
        return status
    
    def should_perform_health_check(self) -> bool:
        """
        Check if a health check should be performed.
        
        Returns:
            True if health check is due
        """
        if self.state != ConnectionState.CONNECTED:
            return False
        
        interval = self.config.get('health_check_interval', 60)
        if not hasattr(self.health, '_last_health_check'):
            return True
        
        elapsed = time.time() - self.health._last_health_check
        return elapsed >= interval
    
    async def perform_health_check(self, websocket) -> bool:
        """
        Perform connection health check.
        
        Args:
            websocket: WebSocket connection to check
            
        Returns:
            True if connection is healthy
        """
        try:
            # Record ping
            self.health.metrics.record_ping()
            
            # Send ping (websockets library handles this automatically)
            await websocket.ping()
            
            # Record pong (will be called when pong is received)
            self.health.metrics.record_pong()
            
            # Update health
            self.health.update_health()
            
            return self.health.is_healthy
        except Exception:
            self.health.record_error()
            return False

