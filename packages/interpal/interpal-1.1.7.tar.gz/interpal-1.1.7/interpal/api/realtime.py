"""
Real-time and notification API endpoints.
"""

from typing import List, Dict, Any, Optional
from ..models.social import Notification


class RealtimeAPI:
    """
    Real-time and notification endpoints.
    """
    
    def __init__(self, http_client, state: Optional[Any] = None):
        """
        Initialize Realtime API.
        
        Args:
            http_client: HTTP client instance
            state: InterpalState instance for object caching
        """
        self.http = http_client
        self._state = state
    
    def get_notifications(
        self,
        limit: int = 50,
        offset: int = 0,
        unread_only: bool = False
    ) -> List[Notification]:
        """
        Get user notifications.
        
        Args:
            limit: Maximum notifications
            offset: Pagination offset
            unread_only: Only return unread notifications
            
        Returns:
            List of Notification objects
        """
        params = {
            "limit": limit,
            "offset": offset,
            "unread_only": unread_only,
        }
        
        data = self.http.get("/v1/notification/my", params=params)
        
        if isinstance(data, list):
            return [Notification(state=self._state, data=notif) for notif in data]
        elif isinstance(data, dict) and "notifications" in data:
            return [Notification(state=self._state, data=notif) for notif in data["notifications"]]
        return []
    
    def mark_notification_read(self, notification_id: str) -> Dict[str, Any]:
        """
        Mark a notification as read.
        
        Args:
            notification_id: Notification ID
            
        Returns:
            Response data
        """
        return self.http.put(f"/v1/notification/{notification_id}/read")
    
    def mark_all_notifications_read(self) -> Dict[str, Any]:
        """
        Mark all notifications as read.
        
        Returns:
            Response data
        """
        return self.http.put("/v1/notification/mark-all-read")
    
    def delete_notification(self, notification_id: str) -> Dict[str, Any]:
        """
        Delete a notification.
        
        Args:
            notification_id: Notification ID
            
        Returns:
            Response data
        """
        return self.http.delete(f"/v1/notification/{notification_id}")
    
    def register_push_token(
        self,
        token: str,
        platform: str = "web"
    ) -> Dict[str, Any]:
        """
        Register device for push notifications.
        
        Args:
            token: Push notification token
            platform: Platform type (web, android, ios)
            
        Returns:
            Response data
        """
        data = {
            "token": token,
            "platform": platform,
        }
        return self.http.post("/v1/push-token", data=data)
    
    def unregister_push_token(self, token: str) -> Dict[str, Any]:
        """
        Unregister device from push notifications.
        
        Args:
            token: Push notification token
            
        Returns:
            Response data
        """
        return self.http.delete(f"/v1/push-token/{token}")
    
    def get_views(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get profile views.
        
        Args:
            limit: Maximum views
            
        Returns:
            List of view data
        """
        params = {"limit": limit}
        data = self.http.get("/v1/views/self", params=params)
        
        if isinstance(data, list):
            return data
        elif isinstance(data, dict) and "views" in data:
            return data["views"]
        return []
    
    def reset_view_stats(self) -> Dict[str, Any]:
        """
        Reset profile view statistics.
        
        Returns:
            Response data
        """
        # Note: The actual endpoint might need a specific ID
        return self.http.put("/v1/views-stats/reset")
    
    def get_online_users(self) -> List[Dict[str, Any]]:
        """
        Get currently online users.
        
        Returns:
            List of online user data
        """
        data = self.http.get("/v1/online-users")
        
        if isinstance(data, list):
            return data
        elif isinstance(data, dict) and "users" in data:
            return data["users"]
        return []

