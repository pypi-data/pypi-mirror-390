"""
Feed posts and comments API endpoints.
"""

from typing import List, Dict, Any, Optional


class PostsAPI:
    """
    Feed posts and comments endpoints.
    """
    
    def __init__(self, http_client, state: Optional[Any] = None):
        """
        Initialize Posts API.
        
        Args:
            http_client: HTTP client instance
            state: InterpalState instance for object caching
        """
        self.http = http_client
        self._state = state
    
    def create_post(
        self,
        content: str,
        privacy: str = "public",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create a new feed post.
        
        Args:
            content: Post content/text
            privacy: Post privacy level (public, friends, private)
            **kwargs: Additional parameters (photo_id, etc.)
            
        Returns:
            Created post object
        """
        data = {
            "content": content,
            "privacy": privacy,
            **kwargs
        }
        return self.http.post("/v1/post", data=data)
    
    def get_post(self, post_id: str, **kwargs) -> Dict[str, Any]:
        """
        Get a specific post.
        
        Args:
            post_id: Post ID
            **kwargs: Additional parameters
            
        Returns:
            Post object
        """
        return self.http.get(f"/v1/post/{post_id}", params=kwargs)
    
    def update_post(
        self,
        post_id: str,
        content: Optional[str] = None,
        privacy: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Update a post.
        
        Args:
            post_id: Post ID
            content: New post content
            privacy: New privacy level
            **kwargs: Additional parameters
            
        Returns:
            Updated post object
        """
        data = {}
        if content:
            data["content"] = content
        if privacy:
            data["privacy"] = privacy
        data.update(kwargs)
        
        return self.http.put(f"/v1/post/{post_id}", data=data)
    
    def delete_post(self, post_id: str) -> Dict[str, Any]:
        """
        Delete a post.
        
        Args:
            post_id: Post ID to delete
            
        Returns:
            Response data
        """
        return self.http.delete(f"/v1/post/{post_id}")
    
    def get_comments(
        self,
        post_id: str,
        limit: int = 50,
        offset: int = 0,
        nest_replies: bool = True,
        feed_owner_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get comments for a post.
        
        Args:
            post_id: Post ID
            limit: Maximum number of comments
            offset: Pagination offset
            nest_replies: Whether to nest replies
            feed_owner_id: Feed owner ID (if applicable)
            
        Returns:
            List of comment objects
        """
        params = {
            "limit": limit,
            "offset": offset,
            "nest_replies": nest_replies
        }
        if feed_owner_id:
            params["feed_owner_id"] = feed_owner_id
        
        data = self.http.get(f"/v1/post/{post_id}/comments", params=params)
        
        if isinstance(data, list):
            return data
        elif isinstance(data, dict) and "data" in data:
            return data["data"]
        elif isinstance(data, dict) and "comments" in data:
            return data["comments"]
        return []
    
    def create_comment(
        self,
        post_id: str,
        content: str,
        parent_id: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create a comment on a post.
        
        Args:
            post_id: Post ID to comment on
            content: Comment content
            parent_id: Parent comment ID (for replies)
            **kwargs: Additional parameters
            
        Returns:
            Created comment object
        """
        data = {
            "post_id": post_id,
            "content": content,
            **kwargs
        }
        if parent_id:
            data["parent_id"] = parent_id
        
        return self.http.post("/v1/comment", data=data)
    
    def update_comment(
        self,
        comment_id: str,
        content: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Update a comment.
        
        Args:
            comment_id: Comment ID
            content: New comment content
            **kwargs: Additional parameters
            
        Returns:
            Updated comment object
        """
        data = {"content": content, **kwargs}
        return self.http.put(f"/v1/comment/{comment_id}", data=data)
    
    def delete_comment(self, comment_id: str) -> Dict[str, Any]:
        """
        Delete a comment.
        
        Args:
            comment_id: Comment ID to delete
            
        Returns:
            Response data
        """
        return self.http.delete(f"/v1/comment/{comment_id}")

