"""
User and profile data models.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from .base import BaseModel
from ..utils import parse_timestamp, parse_user_id


class User(BaseModel):
    """
    Basic user information model.
    """

    def __init__(self, state: Optional[Any] = None, data: Optional[Dict[str, Any]] = None):
        self.id: Optional[str] = None
        self.username: Optional[str] = None
        self.name: Optional[str] = None
        self.age: Optional[int] = None
        self.gender: Optional[str] = None
        self.country: Optional[str] = None
        self.country_code: Optional[str] = None
        self.home_country_code: Optional[str] = None
        self.city: Optional[str] = None
        self.birthday: Optional[str] = None
        self.avatar_url: Optional[str] = None
        self.avatar_thumb_small: Optional[str] = None
        self.avatar_thumb_medium: Optional[str] = None
        self.avatar_thumb_large: Optional[str] = None
        self.is_online: bool = False
        self.last_active: Optional[datetime] = None
        self.last_login: Optional[datetime] = None
        self.mod_status: Optional[str] = None
        self.status: Optional[str] = None
        
        super().__init__(state=state, data=data)
    
    def _from_dict(self, data: Dict[str, Any]):
        """Parse user data from API response."""
        self.id = parse_user_id(data.get('id', data.get('user_id')))
        self.username = data.get('username')
        self.name = data.get('name', data.get('display_name'))
        self.age = data.get('age')
        self.gender = data.get('gender', data.get('sex'))
        self.country = data.get('country')
        self.country_code = data.get('country_code')
        self.home_country_code = data.get('home_country_code')
        self.city = data.get('city')
        self.birthday = data.get('birthday')
        
        # Handle avatar data - can be URL string or object
        avatar_data = data.get('avatar')
        if isinstance(avatar_data, dict):
            self.avatar_url = avatar_data.get('url')
            self.avatar_thumb_small = avatar_data.get('thumb_small')
            self.avatar_thumb_medium = avatar_data.get('thumb_medium')
            self.avatar_thumb_large = avatar_data.get('thumb_large')
        else:
            self.avatar_url = data.get('avatar_url', data.get('profile_picture', avatar_data))
        
        self.is_online = data.get('is_online', data.get('online', False))
        self.last_active = parse_timestamp(data.get('last_active'))
        self.last_login = parse_timestamp(data.get('last_login'))
        self.mod_status = data.get('mod_status')
        self.status = data.get('status')


class Profile(User):
    """
    Extended profile data model with additional information.
    """
    
    def __init__(self, state: Optional[Any] = None, data: Optional[Dict[str, Any]] = None):
        # Extended profile fields
        self.bio: Optional[str] = None
        self.interests: List[str] = []
        self.languages: List[str] = []
        self.looking_for: Optional[str] = None
        self.relationship_status: Optional[str] = None
        self.education_level: Optional[str] = None
        self.occupation: Optional[str] = None
        self.height: Optional[int] = None
        self.ethnicity: Optional[str] = None
        self.religion: Optional[str] = None
        self.zodiac: Optional[str] = None
        self.smoking: Optional[str] = None
        self.drinking: Optional[str] = None
        self.children: Optional[str] = None
        self.latitude: Optional[float] = None
        self.longitude: Optional[float] = None
        self.verified: bool = False
        self.created_at: Optional[datetime] = None
        
        super().__init__(state=state, data=data)
    
    def _from_dict(self, data: Dict[str, Any]):
        """Parse profile data from API response."""
        # Parse base user fields
        super()._from_dict(data)
        
        # Parse extended profile fields
        self.bio = data.get('bio', data.get('about'))
        self.interests = data.get('interests', [])
        self.languages = data.get('languages', [])
        self.looking_for = data.get('looking_for')
        self.relationship_status = data.get('relationship_status')
        self.education_level = data.get('education_level')
        self.occupation = data.get('occupation')
        self.height = data.get('height')
        self.ethnicity = data.get('ethnicity')
        self.religion = data.get('religion')
        self.zodiac = data.get('zodiac')
        self.smoking = data.get('smoking')
        self.drinking = data.get('drinking')
        self.children = data.get('children')
        self.latitude = data.get('latitude')
        self.longitude = data.get('longitude')
        self.verified = data.get('verified', False)
        self.created_at = parse_timestamp(data.get('created_at'))


class UserSettings(BaseModel):
    """
    User preferences and settings model.
    """
    
    def __init__(self, state: Optional[Any] = None, data: Optional[Dict[str, Any]] = None):
        self.email: Optional[str] = None
        self.email_notifications: bool = True
        self.push_notifications: bool = True
        self.message_notifications: bool = True
        self.privacy_level: Optional[str] = None
        self.show_online_status: bool = True
        self.allow_friend_requests: bool = True
        self.language: str = "en"
        self.timezone: Optional[str] = None
        
        super().__init__(state=state, data=data)
    
    def _from_dict(self, data: Dict[str, Any]):
        """Parse settings data from API response."""
        self.email = data.get('email')
        self.email_notifications = data.get('email_notifications', True)
        self.push_notifications = data.get('push_notifications', True)
        self.message_notifications = data.get('message_notifications', True)
        self.privacy_level = data.get('privacy_level')
        self.show_online_status = data.get('show_online_status', True)
        self.allow_friend_requests = data.get('allow_friend_requests', True)
        self.language = data.get('language', 'en')
        self.timezone = data.get('timezone')


class UserCounters(BaseModel):
    """
    User statistics and counters model.
    """
    
    def __init__(self, state: Optional[Any] = None, data: Optional[Dict[str, Any]] = None):
        self.messages: int = 0
        self.friends: int = 0
        self.photos: int = 0
        self.views: int = 0
        self.likes: int = 0
        self.favorites: int = 0
        
        super().__init__(state=state, data=data)
    
    def _from_dict(self, data: Dict[str, Any]):
        """Parse counters data from API response."""
        self.messages = data.get('messages', data.get('message_count', 0))
        self.friends = data.get('friends', data.get('friend_count', 0))
        self.photos = data.get('photos', data.get('photo_count', 0))
        self.views = data.get('views', data.get('view_count', 0))
        self.likes = data.get('likes', data.get('like_count', 0))
        self.favorites = data.get('favorites', data.get('favorite_count', 0))

