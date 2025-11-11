"""
Photo and album data models.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from .base import BaseModel
from .user import User
from ..utils import parse_timestamp


class Photo(BaseModel):
    """
    Photo model with metadata.
    """

    def __init__(self, state: Optional[Any] = None, data: Optional[Dict[str, Any]] = None):
        self.id: Optional[str] = None
        self.url: Optional[str] = None
        self.thumbnail_url: Optional[str] = None
        self.thumb_small: Optional[str] = None
        self.thumb_medium: Optional[str] = None
        self.thumb_large: Optional[str] = None
        self.caption: Optional[str] = None
        self.owner: Optional[User] = None
        self.owner_id: Optional[str] = None
        self.upload_date: Optional[datetime] = None
        self.likes: int = 0
        self.comments: int = 0
        self.width: Optional[int] = None
        self.height: Optional[int] = None
        self.likes_comments: Optional[Dict[str, Any]] = None

        super().__init__(state=state, data=data)
    
    def _from_dict(self, data: Dict[str, Any]):
        """Parse photo data from API response."""
        self.id = str(data.get('id', data.get('photo_id', '')))
        self.url = data.get('url', data.get('image_url'))
        self.thumbnail_url = data.get('thumbnail_url', data.get('thumb_url'))
        self.thumb_small = data.get('thumb_small')
        self.thumb_medium = data.get('thumb_medium')
        self.thumb_large = data.get('thumb_large')
        if not self.thumbnail_url:
            # Prefer medium thumbnail when generic thumbnail isn't provided
            self.thumbnail_url = self.thumb_medium or self.thumb_small or self.thumb_large
        self.caption = data.get('caption', data.get('description'))

        # Parse owner information
        owner_data = data.get('owner', data.get('user'))
        if owner_data:
            if self._state:
                self.owner = self._state.create_user(owner_data)
            else:
                self.owner = User(state=self._state, data=owner_data)
        self.owner_id = str(data.get('owner_id', data.get('user_id', '')))

        self.upload_date = parse_timestamp(data.get('upload_date', data.get('created_at', data.get('created'))))
        likes_comments = data.get('likes_comments')
        if isinstance(likes_comments, dict):
            self.likes_comments = likes_comments
            self.likes = likes_comments.get('likes', likes_comments.get('total_likes', 0))
            self.comments = likes_comments.get('comments', 0)
        else:
            self.likes = data.get('likes', data.get('like_count', 0))
            self.comments = data.get('comments', data.get('comment_count', 0))
        self.width = data.get('width')
        self.height = data.get('height')


class Album(BaseModel):
    """
    Photo album model.
    """

    def __init__(self, state: Optional[Any] = None, data: Optional[Dict[str, Any]] = None):
        self.id: Optional[str] = None
        self.name: Optional[str] = None
        self.description: Optional[str] = None
        self.photos: List[Photo] = []
        self.owner: Optional[User] = None
        self.owner_id: Optional[str] = None
        self.created_at: Optional[datetime] = None
        self.updated_at: Optional[datetime] = None
        self.photo_count: int = 0
        self.type: Optional[str] = None
        self.title: Optional[str] = None
        self.updated: Optional[datetime] = None
        self.privacy: Optional[str] = None
        self.view_acl: Optional[str] = None
        self.comment_acl: Optional[str] = None
        self.album_cover_id: Optional[str] = None
        self.can_comment: Optional[bool] = None
        self.profile_photos: bool = False
        self.cover: Optional[Photo] = None
        self.photo_ids: List[str] = []

        super().__init__(state=state, data=data)
    
    def _from_dict(self, data: Dict[str, Any]):
        """Parse album data from API response."""
        self.id = str(data.get('id', data.get('album_id', '')))
        self.name = data.get('name', data.get('title'))
        self.title = data.get('title', self.name)
        self.description = data.get('description')
        self.type = data.get('type')
        self.privacy = data.get('privacy')
        self.view_acl = data.get('view_acl')
        self.comment_acl = data.get('comment_acl')
        self.photo_ids = [str(pid) for pid in data.get('photo_ids', [])]
        self.album_cover_id = str(data.get('album_cover_id', '')) or None
        self.can_comment = data.get('can_comment')
        self.profile_photos = data.get('profile_photos', data.get('is_profile_album', False))

        # Parse photos
        photos_data = data.get('photos', [])
        if self._state:
            self.photos = [self._state.create_photo(p) for p in photos_data]
        else:
            self.photos = [Photo(state=self._state, data=p) for p in photos_data]

        # Parse owner information
        owner_data = data.get('owner', data.get('user'))
        if owner_data:
            if self._state:
                self.owner = self._state.create_user(owner_data)
            else:
                self.owner = User(state=self._state, data=owner_data)
        self.owner_id = str(data.get('owner_id', data.get('user_id', '')))

        cover_data = data.get('cover')
        if cover_data:
            if self._state:
                self.cover = self._state.create_photo(cover_data)
            else:
                self.cover = Photo(state=self._state, data=cover_data)

        self.created_at = parse_timestamp(data.get('created_at'))
        self.updated_at = parse_timestamp(data.get('updated_at', data.get('updated')))
        self.updated = parse_timestamp(data.get('updated'))
        self.photo_count = data.get('photo_count', len(self.photos))


class MediaUpload(BaseModel):
    """
    Media upload status and progress model.
    """

    def __init__(self, state: Optional[Any] = None, data: Optional[Dict[str, Any]] = None):
        self.upload_id: Optional[str] = None
        self.status: str = "pending"  # pending, uploading, completed, failed
        self.progress: float = 0.0
        self.url: Optional[str] = None
        self.error: Optional[str] = None

        super().__init__(state=state, data=data)
    
    def _from_dict(self, data: Dict[str, Any]):
        """Parse upload data from API response."""
        self.upload_id = str(data.get('upload_id', data.get('id', '')))
        self.status = data.get('status', 'pending')
        self.progress = data.get('progress', 0.0)
        self.url = data.get('url')
        self.error = data.get('error')


class PhotoUploadStatus(BaseModel):
    """
    Photo upload status response from /v1/upload-status/{token} endpoint.
    
    Response structure:
    {
        "payload": {
            "id": "1833140430847619072",
            "uid": "1445989835698485079",
            "url": "https://ipstatic.net/photos/...",
            "thumb_small": "https://...",
            "thumb_medium": "https://...",
            "thumb_large": "https://...",
            "width": 735,
            "height": 651,
            "created": "2025-11-06T12:05:37Z",
            "aid": "",
            "hidden": false,
            "likes_comments": {...},
            "is_stub": false,
            "description": ""
        },
        "status": "success"
    }
    """

    def __init__(self, state: Optional[Any] = None, data: Optional[Dict[str, Any]] = None):
        self.status: str = "pending"
        self.photo_id: Optional[str] = None
        self.user_id: Optional[str] = None
        self.url: Optional[str] = None
        self.thumb_small: Optional[str] = None
        self.thumb_medium: Optional[str] = None
        self.thumb_large: Optional[str] = None
        self.width: Optional[int] = None
        self.height: Optional[int] = None
        self.created: Optional[datetime] = None
        self.album_id: Optional[str] = None
        self.hidden: bool = False
        self.description: Optional[str] = None
        self.likes: int = 0
        self.comments: int = 0

        super().__init__(state=state, data=data)
    
    def _from_dict(self, data: Dict[str, Any]):
        """Parse photo upload status from API response."""
        self.status = data.get('status', 'pending')
        
        # Extract payload data
        payload = data.get('payload', {})
        if payload:
            self.photo_id = str(payload.get('id', ''))
            self.user_id = str(payload.get('uid', ''))
            self.url = payload.get('url')
            self.thumb_small = payload.get('thumb_small')
            self.thumb_medium = payload.get('thumb_medium')
            self.thumb_large = payload.get('thumb_large')
            self.width = payload.get('width')
            self.height = payload.get('height')
            self.created = parse_timestamp(payload.get('created'))
            self.album_id = payload.get('aid') or None
            self.hidden = payload.get('hidden', False)
            self.description = payload.get('description')
            
            # Parse likes_comments if present
            likes_comments = payload.get('likes_comments', {})
            if likes_comments:
                self.likes = likes_comments.get('likes', 0)
                self.comments = likes_comments.get('comments', 0)
