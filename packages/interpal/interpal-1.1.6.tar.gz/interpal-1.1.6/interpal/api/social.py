"""
Social features and relationships API endpoints.
"""

from typing import List, Dict, Any, Optional
from ..models.social import Relationship, Bookmark, Like


class SocialAPI:
    """
    Social features and relationships endpoints.
    """
    
    def __init__(self, http_client, state: Optional[Any] = None):
        """
        Initialize Social API.
        
        Args:
            http_client: HTTP client instance
            state: InterpalState instance for object caching
        """
        self.http = http_client
        self._state = state
    
    def get_relations(self, user_id: str) -> List[Relationship]:
        """
        Get user relationships.
        
        Args:
            user_id: User ID
            
        Returns:
            List of Relationship objects
        """
        data = self.http.get(f"/v1/user/{user_id}/relations")
        
        if isinstance(data, list):
            return [Relationship(state=self._state, data=rel) for rel in data]
        elif isinstance(data, dict) and "relations" in data:
            return [Relationship(state=self._state, data=rel) for rel in data["relations"]]
        return []
    
    def get_friends(self, user_id: Optional[str] = None) -> List[Relationship]:
        """
        Get friends list.
        
        Args:
            user_id: User ID (defaults to self)
            
        Returns:
            List of Relationship objects
        """
        endpoint = f"/v1/user/{user_id}/friends" if user_id else "/v1/friends"
        data = self.http.get(endpoint)
        
        if isinstance(data, list):
            return [Relationship(state=self._state, data=rel) for rel in data]
        elif isinstance(data, dict) and "friends" in data:
            return [Relationship(state=self._state, data=rel) for rel in data["friends"]]
        return []
    
    def block_user(self, user_id: str) -> Dict[str, Any]:
        """
        Block a user.
        
        Args:
            user_id: User ID to block
            
        Returns:
            Response data
        """
        return self.http.put(f"/v1/relation/{user_id}/block")
    
    def unblock_user(self, user_id: str) -> Dict[str, Any]:
        """
        Unblock a user.
        
        Args:
            user_id: User ID to unblock
            
        Returns:
            Response data
        """
        return self.http.put(f"/v1/relation/{user_id}/unblock")
    
    def get_blocked_users(self) -> List[Relationship]:
        """
        Get list of blocked users.
        
        Returns:
            List of Relationship objects
        """
        data = self.http.get("/v1/blocked")
        
        if isinstance(data, list):
            return [Relationship(state=self._state, data=rel) for rel in data]
        elif isinstance(data, dict) and "blocked" in data:
            return [Relationship(state=self._state, data=rel) for rel in data["blocked"]]
        return []
    
    def bookmark_user(self, user_id: str, note: Optional[str] = None) -> Bookmark:
        """
        Bookmark a user.
        
        Args:
            user_id: User ID to bookmark
            note: Optional note about the bookmark
            
        Returns:
            Bookmark object
        """
        data = {"user_id": user_id}
        if note:
            data["note"] = note
        
        response = self.http.post("/v1/bookmark", data=data)
        return Bookmark(state=self._state, data=response)
    
    def remove_bookmark(self, user_id: str) -> Dict[str, Any]:
        """
        Remove a user bookmark.
        
        Args:
            user_id: User ID to unbookmark
            
        Returns:
            Response data
        """
        return self.http.delete(f"/v1/bookmark/{user_id}")
    
    def get_bookmarks(self) -> List[Bookmark]:
        """
        Get bookmarked users.
        
        Returns:
            List of Bookmark objects
        """
        data = self.http.get("/v1/bookmarks")
        
        if isinstance(data, list):
            return [Bookmark(state=self._state, data=bm) for bm in data]
        elif isinstance(data, dict) and "bookmarks" in data:
            return [Bookmark(state=self._state, data=bm) for bm in data["bookmarks"]]
        return []
    
    def like_content(
        self,
        content_id: str,
        content_type: str = "photo"
    ) -> Like:
        """
        Like content (photo, post, etc.).
        
        Args:
            content_id: Content ID to like
            content_type: Type of content (photo, post, profile)
            
        Returns:
            Like object
        """
        data = {
            "content_id": content_id,
            "content_type": content_type,
        }
        response = self.http.post("/v1/like", data=data)
        return Like(state=self._state, data=response)
    
    def unlike_content(self, content_id: str) -> Dict[str, Any]:
        """
        Unlike content.
        
        Args:
            content_id: Content ID to unlike
            
        Returns:
            Response data
        """
        return self.http.delete(f"/v1/like/{content_id}")
    
    def get_likes(self, content_id: str) -> List[Like]:
        """
        Get likes for content.
        
        Args:
            content_id: Content ID
            
        Returns:
            List of Like objects
        """
        data = self.http.get(f"/v1/likes/{content_id}")
        
        if isinstance(data, list):
            return [Like(state=self._state, data=like) for like in data]
        elif isinstance(data, dict) and "likes" in data:
            return [Like(state=self._state, data=like) for like in data["likes"]]
        return []

