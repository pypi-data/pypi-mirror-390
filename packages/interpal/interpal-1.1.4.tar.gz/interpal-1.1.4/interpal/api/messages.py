"""
Messaging system API endpoints.
"""

from typing import List, Dict, Any, Optional
from ..models.message import Message, Thread
import random
import string

class MessagesAPI:
    """
    Messaging system endpoints.
    """

    def __init__(self, http_client, state: Optional[Any] = None):
        """
        Initialize Messages API.

        Args:
            http_client: HTTP client instance
            state: InterpalState instance for object caching
        """
        self.http = http_client
        self._state = state
    
    def get_threads(self, limit: int = 50, offset: int = 0) -> List[Thread]:
        """
        Get message threads list.

        Args:
            limit: Maximum number of threads to return
            offset: Offset for pagination

        Returns:
            List of Thread objects
        """
        params = {"limit": limit, "offset": offset}
        data = self.http.get("/v1/user/self/threads", params=params)

        if isinstance(data, list):
            if self._state:
                return [self._state.create_thread(thread) for thread in data]
            return [Thread(state=self._state, data=thread) for thread in data]
        elif isinstance(data, dict) and "threads" in data:
            if self._state:
                return [self._state.create_thread(thread) for thread in data["threads"]]
            return [Thread(state=self._state, data=thread) for thread in data["threads"]]
        return []
    
    def get_user_thread(self, user_id: str) -> Thread:
        """
        Get or create a thread with a specific user.

        Args:
            user_id: User ID to get thread for

        Returns:
            Thread object
        """
        data = self.http.get(f"/v1/user-thread/{user_id}")
        if self._state:
            return self._state.create_thread(data)
        return Thread(state=self._state, data=data)
    
    def get_thread_messages(
        self,
        thread_id: str,
        limit: int = 50,
        offset: int = 0
    ) -> List[Message]:
        """
        Get messages in a thread.

        Args:
            thread_id: Thread ID
            limit: Maximum number of messages
            offset: Offset for pagination

        Returns:
            List of Message objects
        """
        params = {"limit": limit, "offset": offset}
        data = self.http.get(f"/v1/thread/{thread_id}/messages", params=params)

        if isinstance(data, list):
            if self._state:
                return [self._state.create_message(msg) for msg in data]
            return [Message(state=self._state, data=msg) for msg in data]
        elif isinstance(data, dict) and "messages" in data:
            if self._state:
                return [self._state.create_message(msg) for msg in data["messages"]]
            return [Message(state=self._state, data=msg) for msg in data["messages"]]
        return []
    
    def send_message(self, thread_id: str, content: str, **kwargs) -> Message:
        """
        Send a message in a thread.

        Args:
            thread_id: Thread ID to send message to
            content: Message content
            **kwargs: Additional parameters

        Returns:
            Sent Message object
        """
        # API expects 'message' field, not 'content'
        data = {
            "thread_id": thread_id,
            "message": content,
            **kwargs
        }
        response = self.http.post("/v1/message", data=data)
        if self._state:
            return self._state.create_message(response)
        return Message(state=self._state, data=response)
    
    def start_conversation(self, user_id: str, content: str) -> Dict[str, Any]:
        """
        Start a new conversation with a user.
        
        Args:
            user_id: User ID to message
            content: Initial message content
            
        Returns:
            Response data with thread and message info
        """
        data = {
            "recipient_id": user_id,
            "content": content,
        }
        return self.http.post("/v1/message", data=data)
    
    def mark_thread_viewed(self, thread_id: str) -> Dict[str, Any]:
        """
        Mark a thread as viewed/read.
        
        Args:
            thread_id: Thread ID
            
        Returns:
            Response data
        """
        return self.http.put(f"/v1/thread/{thread_id}/viewed")
    
    def read_message(self, thread_id: str, message_id: str) -> Dict[str, Any]:
        """
        Mark a specific message as read within a thread.

        Args:
            thread_id: Thread ID that contains the message
            message_id: Message ID to mark as read

        Returns:
            Response data from the API
        """
        data = {"message_id": message_id}
        return self.http.put(f"/v1/thread/{thread_id}/viewed", data=data)

    def set_typing(self, thread_id: str, typing: bool = True) -> Dict[str, Any]:
        """
        Send typing indicator.
        
        Args:
            thread_id: Thread ID
            typing: Whether user is typing
            
        Returns:
            Response data
        """
        data = {"typing": typing}
        return self.http.put(f"/v1/thread/{thread_id}/typing", data=data)
    
    def delete_message(self, message_id: str, thread_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Delete a message.
        
        Args:
            message_id: Message ID to delete
            thread_id: Optional thread ID required by API for scoped deletion
            
        Returns:
            Response data
        """
        endpoint = f"/v1/message/{message_id}"
        if thread_id:
            endpoint = f"{endpoint}?thread_id={thread_id}"
        return self.http.delete(endpoint)
    
    def get_unread_count(self) -> int:
        """
        Get count of unread messages from user counters.
        
        Returns:
            Number of unread messages
        """
        # Get unread count from user-counters endpoint
        data = self.http.get("/v1/user-counters")
        if isinstance(data, dict):
            return data.get("unread_messages", data.get("messages", 0))
        return 0
    
    def delete_thread(self, thread_id: str) -> Dict[str, Any]:
        """
        Delete a message thread.
        
        Args:
            thread_id: Thread ID to delete
            
        Returns:
            Response data
        """
        return self.http.delete(f"/v1/thread/{thread_id}")
    
    def archive_thread(self, thread_id: str) -> Dict[str, Any]:
        """
        Archive a message thread.
        
        Args:
            thread_id: Thread ID to archive
            
        Returns:
            Response data
        """
        return self.http.put(f"/v1/thread/{thread_id}/archive")
    
    def unarchive_thread(self, thread_id: str) -> Dict[str, Any]:
        """
        Unarchive a message thread.
        
        Args:
            thread_id: Thread ID to unarchive
            
        Returns:
            Response data
        """
        return self.http.put(f"/v1/thread/{thread_id}/unarchive")
    
    def send_gif(
        self, 
        thread_id: str, 
        gif_url: str, 
        tmp_id: Optional[str] = None
    ) -> Message:
        """
        Send a GIF as a message in a thread.
        
        Args:
            thread_id: Thread ID to send the GIF to
            gif_url: URL of the GIF to send
            tmp_id: Temporary ID for the message (optional, defaults to '34bc')
            
        Returns:
            Sent Message object with GIF attachment
        """
        data = {
            'thread_id': thread_id,
            'attachment_type': 'gif',
            'tmp_id': tmp_id or '34bc',
            'gif_attachment_url': gif_url,
        }
        response = self.http.post("/v1/message", data=data)
        if self._state:
            return self._state.create_message(response)
        return Message(state=self._state, data=response)

    def send_message_correction(
        self,
        thread_id: str,
        message: str,
        attachment_id: str,
        tmp_id: Optional[str] = None,
    ) -> Message:
        """
        Send a correction attachment message within a thread.

        Args:
            thread_id: Thread ID to send the correction to
            message: Correction text/content
            attachment_id: ID of the message being corrected
            tmp_id: Optional temporary ID for tracking

        Returns:
            Sent Message object
        """
        data = {
            "thread_id": thread_id,
            "message": message,
            "attachment_type": "correction",
            "attachment_id": attachment_id,
            "tmp_id": tmp_id or ''.join(random.choices(string.ascii_lowercase + string.digits, k=4)),
        }
        response = self.http.post("/v1/message", data=data)
        if self._state:
            return self._state.create_message(response)
        return Message(state=self._state, data=response)

