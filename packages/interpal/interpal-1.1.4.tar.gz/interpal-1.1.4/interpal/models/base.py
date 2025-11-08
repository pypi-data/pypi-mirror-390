"""
Base model class for all Interpals data models.
"""

from typing import Dict, Any, Optional
import json


class BaseModel:
    """
    Base class for all data models with common functionality.
    Provides automatic attribute assignment, JSON conversion, and string representation.
    """

    def __init__(self, state: Optional[Any] = None, data: Optional[Dict[str, Any]] = None):
        """
        Initialize the model from a dictionary.

        Args:
            state: InterpalState instance for caching and factory operations
            data: Dictionary containing model data
        """
        self._state = state
        self._data = data or {}

        if data:
            self._from_dict(data)
    
    def _from_dict(self, data: Dict[str, Any]):
        """
        Populate model attributes from dictionary.
        Override this in subclasses for custom parsing.

        Args:
            data: Dictionary containing model data
        """
        for key, value in data.items():
            setattr(self, key, value)

    def _update(self, data: Dict[str, Any]):
        """
        Update model with new data.
        This is called by the state when an object is updated.

        Args:
            data: New data dictionary
        """
        # Store the old data for reference
        self._data.update(data)

        # Update attributes
        self._from_dict(data)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert model to dictionary.
        
        Returns:
            Dictionary representation of the model
        """
        result = {}
        for key, value in self.__dict__.items():
            if key.startswith('_'):
                continue
            
            if isinstance(value, BaseModel):
                result[key] = value.to_dict()
            elif isinstance(value, list):
                result[key] = [
                    item.to_dict() if isinstance(item, BaseModel) else item
                    for item in value
                ]
            else:
                result[key] = value
        
        return result
    
    def to_json(self, indent: Optional[int] = None) -> str:
        """
        Convert model to JSON string.
        
        Args:
            indent: Number of spaces for indentation
            
        Returns:
            JSON string representation
        """
        return json.dumps(self.to_dict(), indent=indent, default=str)
    
    def __repr__(self) -> str:
        """String representation of the model."""
        class_name = self.__class__.__name__
        attrs = ', '.join(
            f"{k}={repr(v)}"
            for k, v in self.__dict__.items()
            if not k.startswith('_')
        )
        return f"{class_name}({attrs})"
    
    def __str__(self) -> str:
        """Human-readable string representation."""
        return self.__repr__()
    
    def __eq__(self, other) -> bool:
        """Check equality based on all attributes."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

