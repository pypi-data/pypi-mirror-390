"""
WebSocket configuration management for Interpals library.
Provides configurable settings and presets for different network conditions.
"""

import os
from typing import Optional, Dict, Any
from enum import Enum


class ConnectionProfile(Enum):
    """Predefined connection profiles for different network conditions."""
    STABLE = "stable"
    MOBILE = "mobile"
    UNSTABLE_NETWORK = "unstable_network"
    CUSTOM = "custom"


class WebSocketConfig:
    """
    Configuration class for WebSocket connections.
    
    Attributes:
        ping_interval: Interval between ping frames (seconds)
        ping_timeout: Timeout waiting for pong response (seconds)
        close_timeout: Timeout for graceful connection closure (seconds)
        max_size: Maximum message size in bytes
        max_queue: Maximum message queue size
        max_reconnect_attempts: Maximum number of reconnection attempts
        reconnect_delay: Base delay for exponential backoff (seconds)
        reconnect_jitter: Random jitter factor (0.0-1.0)
        health_check_interval: Interval for connection health checks (seconds)
        connection_timeout: Overall connection establishment timeout (seconds)
        enable_circuit_breaker: Enable circuit breaker pattern
        circuit_breaker_threshold: Failures before circuit breaker activates
        circuit_breaker_cooldown: Cooldown period after circuit breaker activation (seconds)
    """
    
    # Default configuration values
    # NOTE: Interpals server doesn't respond to WebSocket-level pings,
    # so ping_interval/ping_timeout are set to None by default
    DEFAULT_CONFIG = {
        'ping_interval': None,  # Disabled - server doesn't respond to WebSocket pings
        'ping_timeout': None,   # Disabled - server sends own heartbeats
        'close_timeout': 1,
        'max_size': 2**20,  # 1MB
        'max_queue': 1024,
        'max_reconnect_attempts': 10,
        'reconnect_delay': 2,
        'reconnect_jitter': 0.1,
        'health_check_interval': 60,
        'connection_timeout': 30,
        'enable_circuit_breaker': True,
        'circuit_breaker_threshold': 5,
        'circuit_breaker_cooldown': 60,
    }
    
    # Profile-specific configurations
    PROFILES: Dict[ConnectionProfile, Dict[str, Any]] = {
        ConnectionProfile.STABLE: {
            'ping_interval': None,  # Disabled for Interpals
            'ping_timeout': None,   # Disabled for Interpals
            'max_reconnect_attempts': 10,
            'reconnect_delay': 2,
            'health_check_interval': 60,
        },
        ConnectionProfile.MOBILE: {
            'ping_interval': None,  # Disabled for Interpals
            'ping_timeout': None,   # Disabled for Interpals
            'max_reconnect_attempts': 15,
            'reconnect_delay': 3,
            'health_check_interval': 90,
        },
        ConnectionProfile.UNSTABLE_NETWORK: {
            'ping_interval': None,  # Disabled for Interpals
            'ping_timeout': None,   # Disabled for Interpals
            'max_reconnect_attempts': 20,
            'reconnect_delay': 5,
            'health_check_interval': 120,
            'circuit_breaker_threshold': 3,
        }
    }
    
    def __init__(
        self,
        profile: ConnectionProfile = ConnectionProfile.STABLE,
        **overrides
    ):
        """
        Initialize WebSocket configuration.
        
        Args:
            profile: Connection profile preset
            **overrides: Override specific configuration values
        """
        # Start with default config
        self.config = self.DEFAULT_CONFIG.copy()
        
        # Apply profile settings
        if profile != ConnectionProfile.CUSTOM:
            profile_config = self.PROFILES.get(profile, {})
            self.config.update(profile_config)
        
        # Apply any overrides
        self.config.update(overrides)
        
        # Load from environment variables if set
        self._load_from_env()
        
        # Validate configuration
        self._validate()
    
    def _load_from_env(self):
        """Load configuration from environment variables."""
        env_mappings = {
            'INTERPAL_WS_PING_INTERVAL': ('ping_interval', int),
            'INTERPAL_WS_PING_TIMEOUT': ('ping_timeout', int),
            'INTERPAL_WS_MAX_RETRIES': ('max_reconnect_attempts', int),
            'INTERPAL_WS_ENABLE_DEBUG': ('enable_debug_logging', lambda x: x.lower() == 'true'),
            'INTERPAL_WS_CONNECTION_TIMEOUT': ('connection_timeout', int),
            'INTERPAL_WS_CIRCUIT_BREAKER': ('enable_circuit_breaker', lambda x: x.lower() == 'true'),
        }
        
        for env_var, (config_key, converter) in env_mappings.items():
            value = os.getenv(env_var)
            if value is not None:
                try:
                    self.config[config_key] = converter(value)
                except (ValueError, TypeError):
                    pass  # Ignore invalid environment values
    
    def _validate(self):
        """Validate configuration values."""
        # Ensure positive values (or None for ping settings)
        positive_keys = [
            'close_timeout',
            'max_size', 'max_queue', 'max_reconnect_attempts',
            'reconnect_delay', 'health_check_interval',
            'connection_timeout', 'circuit_breaker_threshold',
            'circuit_breaker_cooldown'
        ]
        
        for key in positive_keys:
            if key in self.config and self.config[key] is not None and self.config[key] <= 0:
                raise ValueError(f"{key} must be positive, got {self.config[key]}")
        
        # Ensure jitter is between 0 and 1
        if not 0 <= self.config.get('reconnect_jitter', 0.1) <= 1:
            raise ValueError("reconnect_jitter must be between 0 and 1")
        
        # Ping timeout should be less than ping interval (if both are set)
        ping_interval = self.config.get('ping_interval')
        ping_timeout = self.config.get('ping_timeout')
        if ping_interval is not None and ping_timeout is not None:
            if ping_timeout >= ping_interval:
                raise ValueError("ping_timeout must be less than ping_interval")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        return self.config.get(key, default)
    
    def __getitem__(self, key: str) -> Any:
        """Get configuration value using dict syntax."""
        return self.config[key]
    
    def __setitem__(self, key: str, value: Any):
        """Set configuration value using dict syntax."""
        self.config[key] = value
    
    def to_dict(self) -> Dict[str, Any]:
        """Export configuration as dictionary."""
        return self.config.copy()
    
    @classmethod
    def from_profile(cls, profile_name: str, **overrides) -> 'WebSocketConfig':
        """
        Create configuration from profile name.
        
        Args:
            profile_name: Name of the profile ('stable', 'mobile', 'unstable_network')
            **overrides: Override specific values
            
        Returns:
            WebSocketConfig instance
        """
        try:
            profile = ConnectionProfile(profile_name.lower())
        except ValueError:
            profile = ConnectionProfile.STABLE
        
        return cls(profile=profile, **overrides)
    
    @classmethod
    def from_env(cls, **overrides) -> 'WebSocketConfig':
        """
        Create configuration primarily from environment variables.
        
        Args:
            **overrides: Override specific values
            
        Returns:
            WebSocketConfig instance
        """
        profile_name = os.getenv('INTERPAL_WS_CONFIG_PROFILE', 'stable')
        return cls.from_profile(profile_name, **overrides)

