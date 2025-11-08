"""
WebSocket event data models.
"""

from typing import Optional, Dict, Any
from datetime import datetime
from .base import BaseModel
from .user import User
from .message import Message
from ..utils import parse_timestamp


class EventCounters(BaseModel):
    """
    Real-time event counters model.
    """
    
    def __init__(self, state: Optional[Any] = None, data: Optional[Dict[str, Any]] = None):
        self.new_friend_requests: int = 0
        self.new_messages: int = 0
        self.new_notifications: int = 0
        self.new_views: int = 0
        self.total_threads: int = 0
        self.unread_threads: int = 0
        
        super().__init__(state=state, data=data)
    
    def _from_dict(self, data: Dict[str, Any]):
        """Parse counters data from WebSocket event."""
        self.new_friend_requests = data.get('new_friend_requests', 0)
        self.new_messages = data.get('new_messages', 0)
        self.new_notifications = data.get('new_notifications', 0)
        self.new_views = data.get('new_views', 0)
        self.total_threads = data.get('total_threads', 0)
        self.unread_threads = data.get('unread_threads', 0)


class MessageEventData(BaseModel):
    """
    Message data from WebSocket event.
    """
    
    def __init__(self, state: Optional[Any] = None, data: Optional[Dict[str, Any]] = None):
        self.id: Optional[str] = None
        self.created: Optional[datetime] = None
        self.thread_id: Optional[str] = None
        self.sender_id: Optional[str] = None
        self.message: Optional[str] = None
        self.fake_id: Optional[str] = None
        self.tmp_id: Optional[str] = None
        
        super().__init__(state=state, data=data)
    
    def _from_dict(self, data: Dict[str, Any]):
        """Parse message data from WebSocket event."""
        self.id = str(data.get('id', ''))
        self.created = parse_timestamp(data.get('created'))
        self.thread_id = str(data.get('thread_id', ''))
        self.sender_id = str(data.get('sender_id', ''))
        self.message = data.get('message', '')
        self.fake_id = data.get('fake_id')
        self.tmp_id = data.get('tmp_id')


class ThreadNewMessageEvent(BaseModel):
    """
    Complete THREAD_NEW_MESSAGE WebSocket event model.
    """
    
    def __init__(self, state: Optional[Any] = None, data: Optional[Dict[str, Any]] = None):
        self.type: Optional[str] = None
        self.counters: Optional[EventCounters] = None
        self.click_url: Optional[str] = None
        self.sender: Optional[User] = None
        self.data: Optional[MessageEventData] = None
        
        super().__init__(state=state, data=data)
    
    def _from_dict(self, data: Dict[str, Any]):
        """Parse THREAD_NEW_MESSAGE event from WebSocket."""
        self.type = data.get('type', 'THREAD_NEW_MESSAGE')
        
        # Parse counters
        counters_data = data.get('counters', {})
        self.counters = EventCounters(state=self._state, data=counters_data)
        
        self.click_url = data.get('click_url')
        
        # Parse sender
        sender_data = data.get('sender', {})
        if sender_data:
            if self._state:
                self.sender = self._state.create_user(sender_data)
            else:
                self.sender = User(state=self._state, data=sender_data)
        
        # Parse message data
        message_data = data.get('data', {})
        self.data = MessageEventData(state=self._state, data=message_data)
    
    @property
    def message(self) -> Optional[str]:
        """Convenience property to get message text."""
        return self.data.message if self.data else None
    
    @property
    def message_id(self) -> Optional[str]:
        """Convenience property to get message ID."""
        return self.data.id if self.data else None
    
    @property
    def thread_id(self) -> Optional[str]:
        """Convenience property to get thread ID."""
        return self.data.thread_id if self.data else None


class ThreadTypingEvent(BaseModel):
    """
    THREAD_TYPING WebSocket event model.
    """
    
    def __init__(self, state: Optional[Any] = None, data: Optional[Dict[str, Any]] = None):
        self.type: Optional[str] = None
        self.thread_id: Optional[str] = None
        self.user: Optional[User] = None
        self.user_id: Optional[str] = None
        self.is_typing: bool = False
        
        super().__init__(state=state, data=data)
    
    def _from_dict(self, data: Dict[str, Any]):
        """Parse THREAD_TYPING event from WebSocket."""
        self.type = data.get('type', 'THREAD_TYPING')
        self.thread_id = str(data.get('thread_id', ''))
        self.is_typing = data.get('is_typing', data.get('typing', False))
        
        # Parse user data
        user_data = data.get('user', {})
        if user_data:
            if self._state:
                self.user = self._state.create_user(user_data)
            else:
                self.user = User(state=self._state, data=user_data)
        
        self.user_id = str(data.get('user_id', ''))


class CounterUpdateEvent(BaseModel):
    """
    COUNTER_UPDATE WebSocket event model.
    """
    
    def __init__(self, state: Optional[Any] = None, data: Optional[Dict[str, Any]] = None):
        self.type: Optional[str] = None
        self.counters: Optional[EventCounters] = None
        
        super().__init__(state=state, data=data)
    
    def _from_dict(self, data: Dict[str, Any]):
        """Parse COUNTER_UPDATE event from WebSocket."""
        self.type = data.get('type', 'COUNTER_UPDATE')
        
        # Parse counters
        counters_data = data.get('counters', data.get('data', {}))
        self.counters = EventCounters(state=self._state, data=counters_data)

