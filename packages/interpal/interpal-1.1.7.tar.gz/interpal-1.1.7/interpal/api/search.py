"""
User discovery and search API endpoints.
"""

from typing import List, Dict, Any, Optional
from ..models.user import User, Profile


class SearchAPI:
    """
    User discovery and search endpoints.
    """
    
    def __init__(self, http_client, state: Optional[Any] = None):
        """
        Initialize Search API.
        
        Args:
            http_client: HTTP client instance
            state: InterpalState instance for object caching
        """
        self.http = http_client
        self._state = state
    
    def search_users(
        self,
        query: Optional[str] = None,
        age_min: Optional[int] = None,
        age_max: Optional[int] = None,
        gender: Optional[str] = None,
        country: Optional[str] = None,
        city: Optional[str] = None,
        language: Optional[str] = None,
        looking_for: Optional[str] = None,
        online_only: bool = False,
        limit: int = 50,
        offset: int = 0,
        sort: Optional[str] = None,
        order: Optional[str] = None,
        username: Optional[str] = None,
        new: Optional[bool] = None,
        radius: Optional[int] = None,
        known_level_min: Optional[int] = None,
        lfor_friend: Optional[bool] = None,
        lfor_langex: Optional[bool] = None,
        lfor_meet: Optional[bool] = None,
        lfor_relation: Optional[bool] = None,
        lfor_snail: Optional[bool] = None,
        **kwargs
    ) -> List[Profile]:
        """
        Search for users with filters.
        
        Args:
            query: Search query string (text parameter in API)
            age_min: Minimum age (age1 in API)
            age_max: Maximum age (age2 in API)
            gender: Gender filter (sex in API)
            country: Country filter
            city: City filter
            language: Language filter
            looking_for: Looking for filter
            online_only: Only show online users
            limit: Maximum results
            offset: Pagination offset
            sort: Sort order (e.g., 'last_login', 'age', 'distance')
            order: Order direction ('asc' or 'desc')
            username: Search by username
            new: Only show new users
            radius: Search radius in km (for location-based searches)
            known_level_min: Minimum language knowledge level
            lfor_friend: Looking for friendship
            lfor_langex: Looking for language exchange
            lfor_meet: Looking to meet in person
            lfor_relation: Looking for relationship
            lfor_snail: Looking for snail mail pen pal
            **kwargs: Additional parameters
            
        Returns:
            List of Profile objects
        """
        params = {
            "text": query,
            "age1": age_min,
            "age2": age_max,
            "sex": gender,
            "country": country,
            "city": city,
            "language": language,
            "looking_for": looking_for,
            "online": online_only,
            "limit": limit,
            "offset": offset,
            "sort": sort,
            "order": order,
            "username": username,
            "new": new,
            "radius": radius,
            "knownlevelmin": known_level_min,
            "lfor_friend": lfor_friend,
            "lfor_langex": lfor_langex,
            "lfor_meet": lfor_meet,
            "lfor_relation": lfor_relation,
            "lfor_snail": lfor_snail,
        }
        
        # Add any additional kwargs
        params.update(kwargs)
        
        # Remove None values
        params = {k: v for k, v in params.items() if v is not None}
        
        data = self.http.get("/v1/search/user", params=params)
        
        if isinstance(data, list):
            if self._state:
                return [self._state.create_profile(user) for user in data]
            return [Profile(state=self._state, data=user) for user in data]
        elif isinstance(data, dict) and "results" in data:
            if self._state:
                return [self._state.create_profile(user) for user in data["results"]]
            return [Profile(state=self._state, data=user) for user in data["results"]]
        elif isinstance(data, dict) and "data" in data:
            if self._state:
                return [self._state.create_profile(user) for user in data["data"]]
            return [Profile(state=self._state, data=user) for user in data["data"]]
        return []
    
    def search_by_location(
        self,
        latitude: float,
        longitude: float,
        radius: int = 50,
        limit: int = 50,
    ) -> List[Profile]:
        """
        Search users by geographic location.
        
        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            radius: Search radius in kilometers
            limit: Maximum results
            
        Returns:
            List of Profile objects
        """
        params = {
            "lat": latitude,
            "lon": longitude,
            "radius": radius,
            "limit": limit,
        }
        
        data = self.http.get("/v1/search/geo", params=params)
        
        if isinstance(data, list):
            if self._state:
                return [self._state.create_profile(user) for user in data]
            return [Profile(state=self._state, data=user) for user in data]
        elif isinstance(data, dict) and "results" in data:
            if self._state:
                return [self._state.create_profile(user) for user in data["results"]]
            return [Profile(state=self._state, data=user) for user in data["results"]]
        return []
    
    def get_feed(
        self,
        feed_type: str = "global",
        limit: int = 20,
        offset: int = 0,
        extra: Optional[str] = "photos.user",
        owner_id: Optional[str] = None,
        owner_only: Optional[bool] = None,
        post_type: Optional[str] = None,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Get main content feed.
        
        Args:
            feed_type: Type of feed - "global" or "following" (default: "global")
            limit: Maximum items (default: 20)
            offset: Pagination offset
            extra: Extra data to include (default: "photos.user")
            owner_id: Filter by owner/user ID
            owner_only: Only show posts from the owner
            post_type: Filter by post type
            **kwargs: Additional parameters
            
        Returns:
            List of feed items
        """
        params = {
            "type": feed_type,
            "limit": limit,
            "offset": offset,
            "extra": extra,
            "owner_id": owner_id,
            "owner_only": owner_only,
            "post_type": post_type,
        }
        
        # Add any additional kwargs
        params.update(kwargs)
        
        # Remove None values
        params = {k: v for k, v in params.items() if v is not None}
        
        response = self.http.get("/v1/feed", params=params)
        
        # Response format: {'data': [...], 'user': {...}, ...}
        if isinstance(response, dict) and "data" in response:
            return response["data"]
        elif isinstance(response, list):
            return response
        
        # Fallback
        return []
    
    def get_nearby_users(self, limit: int = 50) -> List[Profile]:
        """
        Get nearby users based on current location.
        
        Args:
            limit: Maximum results
            
        Returns:
            List of Profile objects
        """
        params = {"limit": limit}
        data = self.http.get("/v1/nearby", params=params)
        
        if isinstance(data, list):
            if self._state:
                return [self._state.create_profile(user) for user in data]
            return [Profile(state=self._state, data=user) for user in data]
        elif isinstance(data, dict) and "users" in data:
            if self._state:
                return [self._state.create_profile(user) for user in data["users"]]
            return [Profile(state=self._state, data=user) for user in data["users"]]
        return []
    
    def get_suggestions(self, limit: int = 20) -> List[Profile]:
        """
        Get suggested users based on profile and interests.
        
        Args:
            limit: Maximum results
            
        Returns:
            List of Profile objects
        """
        params = {"limit": limit}
        data = self.http.get("/v1/suggestions", params=params)
        
        if isinstance(data, list):
            if self._state:
                return [self._state.create_profile(user) for user in data]
            return [Profile(state=self._state, data=user) for user in data]
        elif isinstance(data, dict) and "suggestions" in data:
            if self._state:
                return [self._state.create_profile(user) for user in data["suggestions"]]
            return [Profile(state=self._state, data=user) for user in data["suggestions"]]
        return []

