"""
Session persistence manager for Interpals API.
Handles saving and loading sessions with automatic expiration.
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any


class SessionManager:
    """
    Manages persistent sessions with automatic expiration.
    Saves sessions to a file and reuses them until they expire.
    """
    
    DEFAULT_SESSION_FILE = ".interpals_session.json"
    DEFAULT_EXPIRATION_HOURS = 24
    
    def __init__(
        self,
        session_file: Optional[str] = None,
        expiration_hours: int = DEFAULT_EXPIRATION_HOURS
    ):
        """
        Initialize session manager.
        
        Args:
            session_file: Path to session file (default: .interpals_session.json in current directory)
            expiration_hours: Hours until session expires (default: 24)
        """
        if session_file:
            self.session_file = Path(session_file)
        else:
            # Default to current directory
            self.session_file = Path.cwd() / self.DEFAULT_SESSION_FILE
        
        self.expiration_hours = expiration_hours
    
    def save_session(
        self,
        session_cookie: str,
        auth_token: Optional[str] = None,
        username: Optional[str] = None,
        bot_id: Optional[str] = None,
    ) -> None:
        """
        Save session to file with timestamp.
        
        Args:
            session_cookie: Session cookie value
            auth_token: Optional auth token
            username: Optional username for reference
        """
        session_data = {
            "session_cookie": session_cookie,
            "auth_token": auth_token,
            "username": username,
            "bot_id": str(bot_id) if bot_id is not None else None,
            "created_at": datetime.now().isoformat(),
            "expires_at": (datetime.now() + timedelta(hours=self.expiration_hours)).isoformat()
        }
        
        try:
            # Create directory if it doesn't exist
            self.session_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Write session data
            with open(self.session_file, 'w') as f:
                json.dump(session_data, f, indent=2)
            
            # Set file permissions to user-only (on Unix systems)
            if os.name != 'nt':  # Not Windows
                os.chmod(self.session_file, 0o600)
                
        except Exception as e:
            print(f"Warning: Failed to save session: {e}")
    
    def load_session(self) -> Optional[Dict[str, Any]]:
        """
        Load session from file if it exists and is valid.
        
        Returns:
            Dictionary with session data if valid, None otherwise
        """
        if not self.session_file.exists():
            return None
        
        try:
            with open(self.session_file, 'r') as f:
                session_data = json.load(f)
            
            # Check if session has expired
            if self.is_session_expired(session_data):
                print(f"Session expired. Removing old session file.")
                self.clear_session()
                return None
            
            return session_data
            
        except Exception as e:
            print(f"Warning: Failed to load session: {e}")
            return None
    
    def is_session_expired(self, session_data: Dict[str, Any]) -> bool:
        """
        Check if session has expired.
        
        Args:
            session_data: Session data dictionary
            
        Returns:
            True if expired, False otherwise
        """
        try:
            expires_at = datetime.fromisoformat(session_data.get("expires_at", ""))
            return datetime.now() >= expires_at
        except (ValueError, TypeError):
            # If we can't parse the date, consider it expired
            return True
    
    def clear_session(self) -> None:
        """Delete session file."""
        try:
            if self.session_file.exists():
                self.session_file.unlink()
        except Exception as e:
            print(f"Warning: Failed to clear session: {e}")
    
    def get_session_info(self) -> Optional[Dict[str, Any]]:
        """
        Get information about stored session without loading it.
        
        Returns:
            Dictionary with session info or None if no session exists
        """
        session_data = self.load_session()
        if not session_data:
            return None
        
        created_at = datetime.fromisoformat(session_data["created_at"])
        expires_at = datetime.fromisoformat(session_data["expires_at"])
        time_remaining = expires_at - datetime.now()
        
        return {
            "username": session_data.get("username"),
            "bot_id": session_data.get("bot_id"),
            "created_at": created_at,
            "expires_at": expires_at,
            "time_remaining": str(time_remaining).split('.')[0],  # Remove microseconds
            "is_expired": self.is_session_expired(session_data)
        }

