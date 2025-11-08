"""
API endpoint modules for Interpals.
"""

from .user import UserAPI
from .messages import MessagesAPI
from .search import SearchAPI
from .media import MediaAPI
from .social import SocialAPI
from .realtime import RealtimeAPI
from .notifications import NotificationsAPI
from .posts import PostsAPI

__all__ = [
    "UserAPI",
    "MessagesAPI",
    "SearchAPI",
    "MediaAPI",
    "SocialAPI",
    "RealtimeAPI",
    "NotificationsAPI",
    "PostsAPI",
]

