"""
Social relationship and interaction data models.
"""

from typing import Optional, Dict, Any
from datetime import datetime
from .base import BaseModel
from .user import User
from ..utils import parse_timestamp


class Relationship(BaseModel):
    """
    User relationship model (friend, blocked, etc.).
    """
    
    def __init__(self, state: Optional[Any] = None, data: Optional[Dict[str, Any]] = None):
        self.id: Optional[str] = None
        self.user: Optional[User] = None
        self.user_id: Optional[str] = None
        self.type: Optional[str] = None  # friend, blocked, pending
        self.created_at: Optional[datetime] = None
        
        super().__init__(state=state, data=data)
    
    def _from_dict(self, data: Dict[str, Any]):
        """Parse relationship data from API response."""
        self.id = str(data.get('id', data.get('relation_id', '')))
        
        # Parse user information
        user_data = data.get('user', data.get('profile'))
        if user_data:
            if self._state:
                self.user = self._state.create_user(user_data)
            else:
                self.user = User(state=self._state, data=user_data)
        self.user_id = str(data.get('user_id', ''))
        
        self.type = data.get('type', data.get('relation_type'))
        self.created_at = parse_timestamp(data.get('created_at'))


class Bookmark(BaseModel):
    """
    Bookmarked user model.
    """
    
    def __init__(self, state: Optional[Any] = None, data: Optional[Dict[str, Any]] = None):
        self.id: Optional[str] = None
        self.user: Optional[User] = None
        self.user_id: Optional[str] = None
        self.note: Optional[str] = None
        self.created_at: Optional[datetime] = None
        
        super().__init__(state=state, data=data)
    
    def _from_dict(self, data: Dict[str, Any]):
        """Parse bookmark data from API response."""
        self.id = str(data.get('id', data.get('bookmark_id', '')))
        
        # Parse user information
        user_data = data.get('user', data.get('profile'))
        if user_data:
            if self._state:
                self.user = self._state.create_user(user_data)
            else:
                self.user = User(state=self._state, data=user_data)
        self.user_id = str(data.get('user_id', ''))
        
        self.note = data.get('note')
        self.created_at = parse_timestamp(data.get('created_at'))


class Like(BaseModel):
    """
    Content like model.
    """
    
    def __init__(self, state: Optional[Any] = None, data: Optional[Dict[str, Any]] = None):
        self.id: Optional[str] = None
        self.content_id: Optional[str] = None
        self.content_type: Optional[str] = None  # photo, post, profile
        self.user: Optional[User] = None
        self.user_id: Optional[str] = None
        self.created_at: Optional[datetime] = None
        
        super().__init__(state=state, data=data)
    
    def _from_dict(self, data: Dict[str, Any]):
        """Parse like data from API response."""
        self.id = str(data.get('id', data.get('like_id', '')))
        self.content_id = str(data.get('content_id', ''))
        self.content_type = data.get('content_type', data.get('type'))
        
        # Parse user information
        user_data = data.get('user')
        if user_data:
            if self._state:
                self.user = self._state.create_user(user_data)
            else:
                self.user = User(state=self._state, data=user_data)
        self.user_id = str(data.get('user_id', ''))
        
        self.created_at = parse_timestamp(data.get('created_at'))


class Notification(BaseModel):
    """
    User notification model.
    """
    
    def __init__(self, state: Optional[Any] = None, data: Optional[Dict[str, Any]] = None):
        self.id: Optional[str] = None
        self.type: Optional[str] = None  # message, like, friend_request, etc.
        self.title: Optional[str] = None
        self.message: Optional[str] = None
        self.actor: Optional[User] = None
        self.actor_id: Optional[str] = None
        self.read: bool = False
        self.action_url: Optional[str] = None
        self.created_at: Optional[datetime] = None
        
        super().__init__(state=state, data=data)
    
    def _from_dict(self, data: Dict[str, Any]):
        """Parse notification data from API response."""
        self.id = str(data.get('id', data.get('notification_id', '')))
        self.type = data.get('type', data.get('notification_type'))
        self.title = data.get('title')
        self.message = data.get('message', data.get('body'))
        
        # Parse actor information
        actor_data = data.get('actor', data.get('from_user'))
        if actor_data:
            if self._state:
                self.actor = self._state.create_user(actor_data)
            else:
                self.actor = User(state=self._state, data=actor_data)
        self.actor_id = str(data.get('actor_id', data.get('from_id', '')))
        
        self.read = data.get('read', data.get('is_read', False))
        self.action_url = data.get('action_url', data.get('url'))
        self.created_at = parse_timestamp(data.get('created_at'))

