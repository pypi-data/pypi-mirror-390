"""
Utility functions for the Interpals library.
"""

import re
from typing import Optional, Dict, Any
from datetime import datetime


def parse_user_id(user_id: Any) -> str:
    """
    Parse and validate a user ID.
    
    Args:
        user_id: User ID as string or integer
        
    Returns:
        String representation of the user ID
        
    Raises:
        ValidationError: If user ID is invalid
    """
    from .exceptions import ValidationError
    
    if user_id is None:
        raise ValidationError("User ID cannot be None")
    
    user_id_str = str(user_id)
    if not user_id_str.isdigit():
        raise ValidationError(f"Invalid user ID format: {user_id}")
    
    return user_id_str


def parse_timestamp(timestamp: Any) -> Optional[datetime]:
    """
    Parse various timestamp formats into datetime objects.
    
    Args:
        timestamp: Timestamp as string, integer, or datetime
        
    Returns:
        datetime object or None if parsing fails
    """
    if timestamp is None:
        return None
    
    if isinstance(timestamp, datetime):
        return timestamp
    
    if isinstance(timestamp, (int, float)):
        # Unix timestamp
        return datetime.fromtimestamp(timestamp)
    
    if isinstance(timestamp, str):
        # Try various ISO formats
        formats = [
            "%Y-%m-%dT%H:%M:%S.%fZ",
            "%Y-%m-%dT%H:%M:%SZ",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d",
        ]
        for fmt in formats:
            try:
                return datetime.strptime(timestamp, fmt)
            except ValueError:
                continue
    
    return None


def validate_email(email: str) -> bool:
    """
    Validate email format.
    
    Args:
        email: Email address to validate
        
    Returns:
        True if valid, False otherwise
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def build_query_params(params: Dict[str, Any]) -> Dict[str, str]:
    """
    Build query parameters, filtering out None values.
    
    Args:
        params: Dictionary of parameters
        
    Returns:
        Dictionary with None values removed and all values as strings
    """
    return {
        k: str(v) for k, v in params.items()
        if v is not None
    }


def extract_cookie(cookie_string: str, cookie_name: str) -> Optional[str]:
    """
    Extract a specific cookie value from a cookie string.
    
    Args:
        cookie_string: Full cookie string
        cookie_name: Name of the cookie to extract
        
    Returns:
        Cookie value or None if not found
    """
    if not cookie_string:
        return None
    
    for cookie in cookie_string.split(';'):
        cookie = cookie.strip()
        if '=' in cookie:
            name, value = cookie.split('=', 1)
            if name.strip() == cookie_name:
                return value.strip()
    
    return None


def format_user_agent(version: str = "1.0.0") -> str:
    """
    Format a user agent string for API requests.
    
    Args:
        version: Library version
        
    Returns:
        Formatted user agent string
    """
    return f"interpal-python-lib/{version}"


def safe_get(data: Dict[str, Any], *keys, default=None) -> Any:
    """
    Safely get nested dictionary values.
    
    Args:
        data: Dictionary to search
        *keys: Sequence of keys to traverse
        default: Default value if key not found
        
    Returns:
        Value at the nested key or default
    """
    current = data
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return default
    return current

