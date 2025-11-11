"""
Feed post and comment models.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from .base import BaseModel
from .user import User
from .media import Photo, Album


def parse_timestamp(timestamp_str: Any) -> Optional[datetime]:
    """Parse various timestamp formats."""
    if not timestamp_str:
        return None
    
    if isinstance(timestamp_str, datetime):
        return timestamp_str
    
    if isinstance(timestamp_str, (int, float)):
        try:
            from datetime import timezone
            return datetime.fromtimestamp(timestamp_str, tz=timezone.utc)
        except (ValueError, OSError):
            return None
    
    # Try parsing ISO format string
    if isinstance(timestamp_str, str):
        try:
            # Handle various ISO formats
            timestamp_str = timestamp_str.replace('Z', '+00:00')
            return datetime.fromisoformat(timestamp_str)
        except (ValueError, AttributeError):
            return None
    
    return None


class LikesComments(BaseModel):
    """
    Aggregated like/comment reaction counts.
    """

    def __init__(self, state: Optional[Any] = None, data: Optional[Dict[str, Any]] = None):
        self.comments: int = 0
        self.likes: int = 0
        self.likes_like: int = 0
        self.likes_adore: int = 0
        self.likes_laugh: int = 0
        self.likes_wonder: int = 0
        self.likes_tears: int = 0
        self.likes_anger: int = 0
        self.user_liked: bool = False

        super().__init__(state=state, data=data)

    def _from_dict(self, data: Dict[str, Any]):
        self.comments = data.get("comments", 0)
        self.likes = data.get("likes", data.get("total_likes", 0))
        self.likes_like = data.get("likes_like", 0)
        self.likes_adore = data.get("likes_adore", 0)
        self.likes_laugh = data.get("likes_laugh", 0)
        self.likes_wonder = data.get("likes_wonder", 0)
        self.likes_tears = data.get("likes_tears", 0)
        self.likes_anger = data.get("likes_anger", 0)
        self.user_liked = data.get("user_liked", data.get("userLikes", False))


class Post(BaseModel):
    """
    Feed post model.
    """
    
    def __init__(self, state: Optional[Any] = None, data: Optional[Dict[str, Any]] = None):
        self.id: Optional[str] = None
        self.user_id: Optional[str] = None
        self.user: Optional[User] = None
        self.poster_id: Optional[str] = None
        self.feed_owner_id: Optional[str] = None
        self.feed_owner: Optional[User] = None
        self.content: Optional[str] = None
        self.post_type: Optional[str] = None
        self.privacy: Optional[str] = None
        self.created_at: Optional[datetime] = None
        self.updated_at: Optional[datetime] = None
        self.likes_count: int = 0
        self.comments_count: int = 0
        self.photos: List[Photo] = []
        self.is_liked: bool = False
        self.can_edit: bool = False
        self.can_delete: bool = False
        self.view_acl: Optional[str] = None
        self.language: Optional[str] = None
        self.pinned: bool = False
        self.poster_is_group: bool = False
        self.photo_ids: List[str] = []
        self.likes_comments: Optional[LikesComments] = None
        self.album: Optional[Album] = None
        
        super().__init__(state=state, data=data)
    
    def _from_dict(self, data: Dict[str, Any]):
        """Parse post data from API response."""
        post_id = data.get('id', data.get('post_id'))
        self.id = str(post_id) if post_id is not None else None

        self.poster_id = str(data.get('poster_uid', data.get('uid', ''))) or None
        self.feed_owner_id = str(data.get('feed_owner_id', data.get('owner_id', ''))) or None
        self.user_id = str(data.get('user_id', self.poster_id or '')) or None
        
        # Parse user information (poster)
        user_data = data.get('user', data.get('author'))
        if user_data:
            if self._state:
                self.user = self._state.create_user(user_data)
            else:
                self.user = User(state=self._state, data=user_data)
        
        # Feed owner (profile whose feed we're viewing)
        feed_owner_data = data.get('feed_owner')
        if feed_owner_data:
            if self._state:
                self.feed_owner = self._state.create_user(feed_owner_data)
            else:
                self.feed_owner = User(state=self._state, data=feed_owner_data)
        
        self.content = data.get('content', data.get('message', data.get('text', data.get('body'))))
        self.post_type = data.get('post_type', data.get('type'))
        self.privacy = data.get('privacy', data.get('view_acl'))
        self.view_acl = data.get('view_acl')
        self.language = data.get('language')
        self.pinned = data.get('pinned', False)
        self.poster_is_group = data.get('poster_is_group', False)
        self.photo_ids = [str(photo_id) for photo_id in data.get('photo_ids', [])]
        
        time_value = data.get('created_at', data.get('created', data.get('time')))
        self.created_at = parse_timestamp(time_value)
        self.updated_at = parse_timestamp(data.get('updated_at', data.get('updated', data.get('modified'))))
        
        # Parse reaction counts
        likes_comments_data = data.get('likes_comments')
        if likes_comments_data:
            self.likes_comments = LikesComments(state=self._state, data=likes_comments_data)
            self.likes_count = self.likes_comments.likes
            self.comments_count = self.likes_comments.comments
            self.is_liked = self.likes_comments.user_liked
        else:
            self.likes_count = data.get('likes_count', data.get('likes', 0))
            self.comments_count = data.get('comments_count', data.get('comments', 0))
            self.is_liked = data.get('is_liked', data.get('user_liked', False))
        
        # Parse photos
        photos_data = data.get('photos', [])
        if isinstance(photos_data, list):
            if self._state:
                self.photos = [self._state.create_photo(photo) for photo in photos_data]
            else:
                self.photos = [Photo(state=self._state, data=photo) for photo in photos_data]
        
        # Parse album (for album-photos feed items)
        album_data = data.get('album')
        if album_data:
            if self._state:
                self.album = self._state.create_album(album_data)
            else:
                self.album = Album(state=self._state, data=album_data)
        
        # Parse flags
        self.can_edit = data.get('can_edit', False)
        self.can_delete = data.get('can_delete', False)


class Comment(BaseModel):
    """
    Post comment model.
    """
    
    def __init__(self, state: Optional[Any] = None, data: Optional[Dict[str, Any]] = None):
        self.id: Optional[str] = None
        self.post_id: Optional[str] = None
        self.user_id: Optional[str] = None
        self.user: Optional[User] = None
        self.content: Optional[str] = None
        self.parent_id: Optional[str] = None
        self.created_at: Optional[datetime] = None
        self.updated_at: Optional[datetime] = None
        self.likes_count: int = 0
        self.replies_count: int = 0
        self.replies: List['Comment'] = []
        self.is_liked: bool = False
        self.can_edit: bool = False
        self.can_delete: bool = False
        
        super().__init__(state=state, data=data)
    
    def _from_dict(self, data: Dict[str, Any]):
        """Parse comment data from API response."""
        self.id = str(data.get('id', data.get('comment_id', '')))
        self.post_id = str(data.get('post_id', ''))
        self.user_id = str(data.get('user_id', data.get('uid', '')))
        
        # Parse user information
        user_data = data.get('user', data.get('author'))
        if user_data:
            if self._state:
                self.user = self._state.create_user(user_data)
            else:
                self.user = User(state=self._state, data=user_data)
        
        self.content = data.get('content', data.get('text', data.get('body')))
        self.parent_id = str(data.get('parent_id', '')) if data.get('parent_id') else None
        
        self.created_at = parse_timestamp(data.get('created_at', data.get('created')))
        self.updated_at = parse_timestamp(data.get('updated_at', data.get('updated')))
        
        # Parse counts
        self.likes_count = data.get('likes_count', data.get('likes', 0))
        self.replies_count = data.get('replies_count', data.get('replies', 0))
        
        # Parse nested replies
        replies_data = data.get('replies', [])
        if isinstance(replies_data, list):
            self.replies = [Comment(state=self._state, data=reply) for reply in replies_data]
        
        # Parse flags
        self.is_liked = data.get('is_liked', data.get('user_liked', False))
        self.can_edit = data.get('can_edit', False)
        self.can_delete = data.get('can_delete', False)


class Trip(BaseModel):
    """
    User travel plan/trip model.
    """
    
    def __init__(self, state: Optional[Any] = None, data: Optional[Dict[str, Any]] = None):
        self.id: Optional[str] = None
        self.user_id: Optional[str] = None
        self.user: Optional[User] = None
        self.destination: Optional[str] = None
        self.country: Optional[str] = None
        self.city: Optional[str] = None
        self.start_date: Optional[datetime] = None
        self.end_date: Optional[datetime] = None
        self.description: Optional[str] = None
        self.created_at: Optional[datetime] = None
        self.updated_at: Optional[datetime] = None
        
        super().__init__(state=state, data=data)
    
    def _from_dict(self, data: Dict[str, Any]):
        """Parse trip data from API response."""
        self.id = str(data.get('id', data.get('trip_id', '')))
        self.user_id = str(data.get('user_id', data.get('uid', '')))
        
        # Parse user information
        user_data = data.get('user')
        if user_data:
            if self._state:
                self.user = self._state.create_user(user_data)
            else:
                self.user = User(state=self._state, data=user_data)
        
        self.destination = data.get('destination')
        self.country = data.get('country')
        self.city = data.get('city')
        
        self.start_date = parse_timestamp(data.get('start_date'))
        self.end_date = parse_timestamp(data.get('end_date'))
        
        self.description = data.get('description', data.get('notes'))
        
        self.created_at = parse_timestamp(data.get('created_at', data.get('created')))
        self.updated_at = parse_timestamp(data.get('updated_at', data.get('updated')))

