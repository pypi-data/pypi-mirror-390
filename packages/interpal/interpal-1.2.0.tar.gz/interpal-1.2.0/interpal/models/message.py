"""
Message and thread data models.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from .base import BaseModel
from .user import User
from ..utils import parse_timestamp


class Message(BaseModel):
    """
    Individual message model.
    """

    def __init__(self, state: Optional[Any] = None, data: Optional[Dict[str, Any]] = None):
        self.id: Optional[str] = None
        self.thread_id: Optional[str] = None
        self.sender: Optional[User] = None
        self.sender_id: Optional[str] = None
        self.content: Optional[str] = None
        self.timestamp: Optional[datetime] = None
        self.read: bool = False
        self.attachments: List[str] = []

        super().__init__(state=state, data=data)
    
    def _from_dict(self, data: Dict[str, Any]):
        """Parse message data from API response."""
        self.id = str(data.get('id', data.get('message_id', '')))
        self.thread_id = str(data.get('thread_id', ''))

        # Parse sender information
        sender_data = data.get('sender', data.get('from'))
        if sender_data:
            if self._state:
                self.sender = self._state.create_user(sender_data)
            else:
                self.sender = User(state=self._state, data=sender_data)
        self.sender_id = str(data.get('sender_id', data.get('from_id', '')))

        self.content = data.get('content', data.get('body', data.get('text')))
        self.timestamp = parse_timestamp(data.get('timestamp', data.get('created_at')))
        self.read = data.get('read', data.get('is_read', False))
        self.attachments = data.get('attachments', [])


class Thread(BaseModel):
    """
    Message thread model.
    """

    def __init__(self, state: Optional[Any] = None, data: Optional[Dict[str, Any]] = None):
        self.id: Optional[str] = None
        self.participants: List[User] = []
        self.last_message: Optional[Message] = None
        self.unread_count: int = 0
        self.total_count: int = 0
        self.new_count: int = 0
        self.created_at: Optional[datetime] = None
        self.updated_at: Optional[datetime] = None
        self.uid: Optional[str] = None
        self.target_id: Optional[str] = None
        self.last_msg_id: Optional[str] = None
        self.last_msg_sender_id: Optional[str] = None
        self.last_msg_type: Optional[str] = None
        self.last_msg_datetime: Optional[datetime] = None
        self.user: Optional[User] = None
        self.target_last_read_msg_id: Optional[str] = None

        super().__init__(state=state, data=data)
    
    def _from_dict(self, data: Dict[str, Any]):
        """Parse thread data from API response."""
        thread_id = data.get('id', data.get('thread_id'))
        self.id = str(thread_id) if thread_id is not None else None

        uid = data.get('uid')
        self.uid = str(uid) if uid is not None and uid != '' else None

        target_id = data.get('target_id')
        self.target_id = str(target_id) if target_id is not None and target_id != '' else None

        # Parse participants
        participants_data = data.get('participants', data.get('users', []))
        if self._state:
            self.participants = [self._state.create_user(p) for p in participants_data]
        else:
            self.participants = [User(state=self._state, data=p) for p in participants_data]

        # Some endpoints return a single user object instead of participants
        if not participants_data and data.get("user"):
            if self._state:
                user = self._state.create_user(data["user"])
            else:
                user = User(state=self._state, data=data["user"])
            self.user = user
            self.participants = [user]

        # Parse last message
        last_msg_data = data.get('last_message', data.get('latest_message'))
        if last_msg_data:
            if self._state:
                self.last_message = self._state.create_message(last_msg_data)
            else:
                self.last_message = Message(state=self._state, data=last_msg_data)

        self.unread_count = data.get('unread_count', data.get('unread', 0))
        self.total_count = data.get('total', data.get('message_total', self.total_count))
        self.new_count = data.get('new', data.get('new_messages', self.new_count))

        last_msg_id = data.get('last_msg_id')
        if last_msg_id is not None and last_msg_id != '':
            self.last_msg_id = str(last_msg_id)

        last_msg_sender_id = data.get('last_msg_sender_id')
        if last_msg_sender_id is not None and last_msg_sender_id != '':
            self.last_msg_sender_id = str(last_msg_sender_id)
        self.last_msg_type = data.get('last_msg_type', self.last_msg_type)
        self.last_msg_datetime = parse_timestamp(data.get('last_msg_datetime'))

        self.created_at = parse_timestamp(data.get('created_at', data.get('created')))
        self.updated_at = parse_timestamp(data.get('updated_at'))
        target_last_read_msg_id = data.get('target_last_read_msg_id')
        self.target_last_read_msg_id = (
            str(target_last_read_msg_id)
            if target_last_read_msg_id is not None and target_last_read_msg_id != ''
            else None
        )


class TypingIndicator(BaseModel):
    """
    Real-time typing indicator model.
    """

    def __init__(self, state: Optional[Any] = None, data: Optional[Dict[str, Any]] = None):
        self.thread_id: Optional[str] = None
        self.user: Optional[User] = None
        self.user_id: Optional[str] = None
        self.is_typing: bool = False
        self.timestamp: Optional[datetime] = None

        super().__init__(state=state, data=data)
    
    def _from_dict(self, data: Dict[str, Any]):
        """Parse typing indicator data from WebSocket message."""
        self.thread_id = str(data.get('thread_id', ''))

        user_data = data.get('user')
        if user_data:
            if self._state:
                self.user = self._state.create_user(user_data)
            else:
                self.user = User(state=self._state, data=user_data)
        self.user_id = str(data.get('user_id', ''))

        self.is_typing = data.get('is_typing', data.get('typing', False))
        self.timestamp = parse_timestamp(data.get('timestamp'))

