"""
User management API endpoints.
"""

from typing import Dict, Any, Optional, List
from ..models.user import User, Profile, UserSettings, UserCounters


class UserAPI:
    """
    User management endpoints.
    """

    def __init__(self, http_client, state: Optional[Any] = None):
        """
        Initialize User API.

        Args:
            http_client: HTTP client instance (HTTPClient or AsyncHTTPClient)
            state: InterpalState instance for object caching
        """
        self.http = http_client
        self._state = state
    
    def get_self(self) -> Profile:
        """
        Get current user's profile.

        Returns:
            Profile object for the authenticated user
        """
        data = self.http.get("/v1/account/self")
        if self._state:
            return self._state.create_profile(data)
        return Profile(state=self._state, data=data)
    
    def update_self(self, **kwargs) -> Profile:
        """
        Update current user's profile.

        Args:
            **kwargs: Profile fields to update (name, bio, age, etc.)

        Returns:
            Updated Profile object
        """
        data = self.http.put("/v1/account/self", data=kwargs)
        if self._state:
            return self._state.create_profile(data)
        return Profile(state=self._state, data=data)
    
    def get_user(self, user_id: str) -> Profile:
        """
        Get a user's profile by ID.

        Args:
            user_id: User ID to fetch

        Returns:
            Profile object for the user
        """
        data = self.http.get(f"/v1/profile/{user_id}")
        if self._state:
            return self._state.create_profile(data)
        return Profile(state=self._state, data=data)
    
    def get_account(self, user_id: str) -> Profile:
        """
        Get account information by ID.

        Args:
            user_id: User ID to fetch

        Returns:
            Profile object
        """
        data = self.http.get(f"/v1/account/{user_id}")
        if self._state:
            return self._state.create_profile(data)
        return Profile(state=self._state, data=data)
    
    def get_counters(self) -> UserCounters:
        """
        Get user statistics and counters.

        Returns:
            UserCounters object with statistics
        """
        data = self.http.get("/v1/user-counters")
        return UserCounters(state=self._state, data=data)
    
    def get_settings(self) -> UserSettings:
        """
        Get user settings.

        Returns:
            UserSettings object
        """
        data = self.http.get("/v1/settings/self")
        return UserSettings(state=self._state, data=data)
    
    def update_settings(self, **kwargs) -> UserSettings:
        """
        Update user settings.

        Args:
            **kwargs: Settings to update

        Returns:
            Updated UserSettings object
        """
        data = self.http.put("/v1/settings/self", data=kwargs)
        return UserSettings(state=self._state, data=data)
    
    def get_activity(self) -> Dict[str, Any]:
        """
        Get user activity information.
        
        Returns:
            Activity data dictionary
        """
        return self.http.get("/v1/activity/self")
    
    def get_user_trips(
        self,
        user_id: str,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get user's travel plans/trips.
        
        Args:
            user_id: User ID
            limit: Maximum number of trips
            offset: Pagination offset
            
        Returns:
            List of trip objects
        """
        params = {"limit": limit, "offset": offset}
        data = self.http.get(f"/v1/user/{user_id}/trips", params=params)
        
        if isinstance(data, list):
            return data
        elif isinstance(data, dict) and "data" in data:
            return data["data"]
        elif isinstance(data, dict) and "trips" in data:
            return data["trips"]
        return []
    
    def get_my_trips(
        self,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get current user's travel plans/trips.
        
        Args:
            limit: Maximum number of trips
            offset: Pagination offset
            
        Returns:
            List of trip objects
        """
        params = {"limit": limit, "offset": offset}
        data = self.http.get("/v1/user/self/trips", params=params)
        
        if isinstance(data, list):
            return data
        elif isinstance(data, dict) and "data" in data:
            return data["data"]
        elif isinstance(data, dict) and "trips" in data:
            return data["trips"]
        return []
    
    def create_trip(
        self,
        destination: str,
        start_date: str,
        end_date: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create a new trip/travel plan.
        
        Args:
            destination: Trip destination
            start_date: Start date (ISO format)
            end_date: End date (ISO format, optional)
            **kwargs: Additional trip details
            
        Returns:
            Created trip object
        """
        data = {
            "destination": destination,
            "start_date": start_date,
            **kwargs
        }
        if end_date:
            data["end_date"] = end_date
        
        return self.http.post("/v1/trip", data=data)
    
    def update_trip(
        self,
        trip_id: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Update a trip/travel plan.
        
        Args:
            trip_id: Trip ID
            **kwargs: Fields to update
            
        Returns:
            Updated trip object
        """
        return self.http.put(f"/v1/trip/{trip_id}", data=kwargs)
    
    def delete_trip(self, trip_id: str) -> Dict[str, Any]:
        """
        Delete a trip/travel plan.
        
        Args:
            trip_id: Trip ID to delete
            
        Returns:
            Response data
        """
        return self.http.delete(f"/v1/trip/{trip_id}")

