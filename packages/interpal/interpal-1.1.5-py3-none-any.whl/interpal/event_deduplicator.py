"""
Event deduplication system for WebSocket hot-swap reconnection.

During hot-swap, two connections may briefly overlap and receive the same events.
This module ensures each event is processed only once.
"""

import time
import logging
from typing import Optional, Set, Dict, Any
from collections import OrderedDict

logger = logging.getLogger(__name__)


class EventDeduplicator:
    """
    Deduplicates WebSocket events during hot-swap connections.
    
    Uses a sliding window of recently seen event IDs to filter duplicates.
    Automatically expires old entries to prevent memory growth.
    """
    
    def __init__(
        self,
        max_cache_size: int = 1000,
        expiration_seconds: float = 60.0
    ):
        """
        Initialize event deduplicator.
        
        Args:
            max_cache_size: Maximum number of event IDs to track
            expiration_seconds: How long to remember an event ID
        """
        self.max_cache_size = max_cache_size
        self.expiration_seconds = expiration_seconds
        
        # Track seen event IDs with timestamps
        # OrderedDict maintains insertion order for efficient expiration
        self._seen_events: OrderedDict[str, float] = OrderedDict()
        
        # Statistics
        self._total_events = 0
        self._duplicates_blocked = 0
    
    def _generate_event_id(self, event_data: Dict[str, Any]) -> Optional[str]:
        """
        Generate a unique ID for an event based on its data.
        
        Args:
            event_data: Raw event data from WebSocket
            
        Returns:
            Unique event ID, or None if event cannot be identified
        """
        try:
            event_type = event_data.get('type', event_data.get('event'))
            
            # For message events, use message ID
            if event_type == 'THREAD_NEW_MESSAGE':
                message_id = event_data.get('message_id')
                thread_id = event_data.get('thread_id')
                if message_id and thread_id:
                    return f"msg_{thread_id}_{message_id}"
            
            # For typing events, use thread + user combination with timestamp
            elif event_type == 'THREAD_TYPING':
                thread_id = event_data.get('thread_id')
                user_id = event_data.get('user_id')
                # Typing events are transient, use a short-lived ID
                # We don't need perfect deduplication for typing indicators
                if thread_id and user_id:
                    # Round to nearest second to catch immediate duplicates
                    timestamp = int(time.time())
                    return f"typing_{thread_id}_{user_id}_{timestamp}"
            
            # For counter updates, use counter type
            elif event_type == 'COUNTER_UPDATE':
                # Counter updates should be processed even if duplicate
                # as they represent state changes
                # Use timestamp to allow same counter to update multiple times
                timestamp = time.time()
                return f"counter_{timestamp}"
            
            # For other events, create ID from type and key fields
            else:
                # Try to find identifying fields
                event_id = event_data.get('id')
                if event_id:
                    return f"{event_type}_{event_id}"
                
                # Fallback: allow all unidentifiable events through
                # Better to process duplicate than miss an event
                return None
        
        except Exception as e:
            logger.warning(f"Error generating event ID: {e}")
            return None
    
    def _cleanup_expired(self):
        """Remove expired event IDs to prevent memory growth."""
        if not self._seen_events:
            return
        
        current_time = time.time()
        cutoff_time = current_time - self.expiration_seconds
        
        # Remove expired entries from the front (oldest)
        while self._seen_events:
            oldest_id, oldest_time = next(iter(self._seen_events.items()))
            if oldest_time < cutoff_time:
                del self._seen_events[oldest_id]
            else:
                break  # Rest are newer, stop checking
        
        # Also enforce max size limit
        while len(self._seen_events) > self.max_cache_size:
            # Remove oldest
            self._seen_events.popitem(last=False)
    
    def is_duplicate(self, event_data: Dict[str, Any]) -> bool:
        """
        Check if an event is a duplicate.
        
        Args:
            event_data: Raw event data from WebSocket
            
        Returns:
            True if this is a duplicate event, False otherwise
        """
        self._total_events += 1
        
        # Generate unique ID for this event
        event_id = self._generate_event_id(event_data)
        
        # If we can't generate an ID, assume it's not a duplicate
        # Better to process than to drop
        if event_id is None:
            return False
        
        # Check if we've seen this event before
        current_time = time.time()
        
        if event_id in self._seen_events:
            # This is a duplicate!
            self._duplicates_blocked += 1
            logger.debug(f"🚫 Blocked duplicate event: {event_id}")
            return True
        
        # New event - record it
        self._seen_events[event_id] = current_time
        
        # Periodic cleanup of old entries
        if len(self._seen_events) % 100 == 0:
            self._cleanup_expired()
        
        return False
    
    def should_process_event(self, event_data: Dict[str, Any]) -> bool:
        """
        Determine if an event should be processed.
        
        This is the main method to use - returns True if event is new.
        
        Args:
            event_data: Raw event data from WebSocket
            
        Returns:
            True if event should be processed, False if duplicate
        """
        return not self.is_duplicate(event_data)
    
    def reset(self):
        """Reset deduplicator state."""
        self._seen_events.clear()
        self._total_events = 0
        self._duplicates_blocked = 0
        logger.debug("Event deduplicator reset")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get deduplication statistics.
        
        Returns:
            Dictionary with statistics
        """
        return {
            'total_events': self._total_events,
            'duplicates_blocked': self._duplicates_blocked,
            'unique_events': self._total_events - self._duplicates_blocked,
            'cache_size': len(self._seen_events),
            'duplicate_rate': (
                self._duplicates_blocked / self._total_events * 100
                if self._total_events > 0 else 0
            )
        }
    
    def __repr__(self) -> str:
        stats = self.get_stats()
        return (
            f"EventDeduplicator("
            f"total={stats['total_events']}, "
            f"blocked={stats['duplicates_blocked']}, "
            f"rate={stats['duplicate_rate']:.1f}%)"
        )

