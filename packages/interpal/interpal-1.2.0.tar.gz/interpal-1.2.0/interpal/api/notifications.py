"""
Notifications API endpoints.
"""

from typing import List, Dict, Any, Optional


class NotificationsAPI:
    """
    Notifications endpoints.
    """
    
    def __init__(self, http_client, state: Optional[Any] = None):
        """
        Initialize Notifications API.
        
        Args:
            http_client: HTTP client instance
            state: InterpalState instance for object caching
        """
        self.http = http_client
        self._state = state
    
    def get_notifications(
        self,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get user notifications.
        
        Args:
            limit: Maximum number of notifications to return
            offset: Offset for pagination
            
        Returns:
            List of notification objects
        """
        params = {"limit": limit, "offset": offset}
        data = self.http.get("/v1/notification/my", params=params)
        
        if isinstance(data, list):
            return data
        elif isinstance(data, dict) and "data" in data:
            return data["data"]
        elif isinstance(data, dict) and "notifications" in data:
            return data["notifications"]
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
    
    def mark_all_read(self) -> Dict[str, Any]:
        """
        Mark all notifications as read.
        
        Returns:
            Response data
        """
        return self.http.put("/v1/notification/read-all")
    
    def delete_notification(self, notification_id: str) -> Dict[str, Any]:
        """
        Delete a notification.
        
        Args:
            notification_id: Notification ID to delete
            
        Returns:
            Response data
        """
        return self.http.delete(f"/v1/notification/{notification_id}")

