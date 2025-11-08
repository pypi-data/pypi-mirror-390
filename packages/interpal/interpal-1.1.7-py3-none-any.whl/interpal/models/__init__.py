"""
Data models for the Interpals library.
"""

from .base import BaseModel
from .user import User, Profile, UserSettings, UserCounters
from .message import Message, Thread, TypingIndicator
from .media import Photo, Album, MediaUpload, PhotoUploadStatus
from .social import Relationship, Bookmark, Like, Notification
from .post import Post, Comment, Trip
from .events import (
    EventCounters,
    MessageEventData,
    ThreadNewMessageEvent,
    ThreadTypingEvent,
    CounterUpdateEvent,
)

__all__ = [
    "BaseModel",
    "User",
    "Profile",
    "UserSettings",
    "UserCounters",
    "Message",
    "Thread",
    "TypingIndicator",
    "Photo",
    "Album",
    "MediaUpload",
    "PhotoUploadStatus",
    "Relationship",
    "Bookmark",
    "Like",
    "Notification",
    "Post",
    "Comment",
    "Trip",
    "EventCounters",
    "MessageEventData",
    "ThreadNewMessageEvent",
    "ThreadTypingEvent",
    "CounterUpdateEvent",
]

