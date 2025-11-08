"""
Interpals Python Library
A comprehensive Python library for the Interpals API with sync/async support.
Similar to discord.py in design and functionality.

Author: Interpals Python Library Contributors
License: MIT
Version: 1.1.5
"""

__version__ = "1.1.5"
__author__ = "Interpals Python Library Contributors"
__license__ = "MIT"

# Core client classes
from .client import InterpalClient, AsyncInterpalClient

# Data models
from .models.user import User, Profile, UserSettings, UserCounters
from .models.message import Message, Thread, TypingIndicator
from .models.media import Photo, Album, MediaUpload
from .models.social import Relationship, Bookmark, Like, Notification
from .models.post import Post, Comment, Trip

# Exceptions
from .exceptions import (
    InterpalException,
    AuthenticationError,
    APIError,
    RateLimitError,
    WebSocketError,
    WebSocketConnectionError,
    WebSocketTimeoutError,
    WebSocketAuthenticationError,
    WebSocketRateLimitError,
    ValidationError,
)

# WebSocket configuration
from .websocket_config import WebSocketConfig, ConnectionProfile

# Connection management
from .connection_manager import ConnectionState, ConnectionManager

# Extensions (imported on demand)
# from .ext import commands  # Use: from interpal.ext.commands import Bot

__all__ = [
    # Client
    "InterpalClient",
    "AsyncInterpalClient",
    
    # User models
    "User",
    "Profile",
    "UserSettings",
    "UserCounters",
    
    # Message models
    "Message",
    "Thread",
    "TypingIndicator",
    
    # Media models
    "Photo",
    "Album",
    "MediaUpload",
    
    # Social models
    "Relationship",
    "Bookmark",
    "Like",
    "Notification",
    
    # Post/Feed models
    "Post",
    "Comment",
    "Trip",
    
    # Exceptions
    "InterpalException",
    "AuthenticationError",
    "APIError",
    "RateLimitError",
    "WebSocketError",
    "WebSocketConnectionError",
    "WebSocketTimeoutError",
    "WebSocketAuthenticationError",
    "WebSocketRateLimitError",
    "ValidationError",
    
    # WebSocket configuration
    "WebSocketConfig",
    "ConnectionProfile",
    "ConnectionState",
    "ConnectionManager",
]

