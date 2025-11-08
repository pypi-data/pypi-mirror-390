# WebSocket Event Models

This guide explains how to use the structured event models for WebSocket events in the Interpal library.

## Overview

WebSocket events are now wrapped in structured model classes that provide:
- Type safety and autocomplete support
- Easy access to nested data
- Consistent API across all event types
- Convenience properties for common operations

## Event Models

### ThreadNewMessageEvent

Represents a new message received through WebSocket.

**Properties:**
- `type` (str): Event type ("THREAD_NEW_MESSAGE")
- `sender` (User): Full User object with sender information
- `data` (MessageEventData): Message details
- `counters` (EventCounters): Real-time counters
- `click_url` (str): Direct URL to the message thread

**Convenience Properties:**
- `message` (str): Quick access to message text
- `message_id` (str): Quick access to message ID
- `thread_id` (str): Quick access to thread ID

**Example:**
```python
@ws.on('on_message')
async def handle_message(event: ThreadNewMessageEvent):
    # Access sender info
    print(f"From: {event.sender.name} (@{event.sender.username})")
    print(f"Online: {event.sender.is_online}")
    
    # Access message
    print(f"Message: {event.data.message}")
    print(f"Thread: {event.data.thread_id}")
    
    # Or use convenience properties
    print(f"Quick access: {event.message}")
    
    # Check counters
    print(f"Unread threads: {event.counters.unread_threads}")
```

### MessageEventData

The actual message data within a ThreadNewMessageEvent.

**Properties:**
- `id` (str): Message ID
- `created` (datetime): Message creation timestamp
- `thread_id` (str): Thread ID
- `sender_id` (str): Sender user ID
- `message` (str): Message text content
- `fake_id` (str): Temporary fake ID (for optimistic updates)
- `tmp_id` (str): Temporary ID (for optimistic updates)

### User (Enhanced)

The User model has been enhanced to support WebSocket event data.

**New Properties:**
- `country_code` (str): ISO country code
- `home_country_code` (str): Home country code
- `birthday` (str): Birthday date
- `avatar_thumb_small` (str): Small avatar thumbnail URL
- `avatar_thumb_medium` (str): Medium avatar thumbnail URL
- `avatar_thumb_large` (str): Large avatar thumbnail URL
- `last_login` (datetime): Last login timestamp
- `mod_status` (str): Moderator status
- `status` (str): Account status

**Example:**
```python
sender = event.sender
print(f"Name: {sender.name}")
print(f"Age: {sender.age}, from {sender.country_code}")
print(f"Avatar: {sender.avatar_url}")
print(f"Thumbnail: {sender.avatar_thumb_small}")
print(f"Online: {sender.is_online}")
print(f"Last login: {sender.last_login}")
```

### EventCounters

Real-time counters for various notification types.

**Properties:**
- `new_friend_requests` (int): Number of new friend requests
- `new_messages` (int): Number of new messages
- `new_notifications` (int): Number of new notifications
- `new_views` (int): Number of new profile views
- `total_threads` (int): Total message threads
- `unread_threads` (int): Number of unread threads

**Example:**
```python
counters = event.counters
print(f"New messages: {counters.new_messages}")
print(f"Unread threads: {counters.unread_threads}")
print(f"New views: {counters.new_views}")
```

### ThreadTypingEvent

Represents a typing indicator event.

**Properties:**
- `type` (str): Event type ("THREAD_TYPING")
- `thread_id` (str): Thread ID
- `user` (User): User who is typing
- `user_id` (str): User ID
- `is_typing` (bool): Whether user is currently typing

**Example:**
```python
@ws.on('on_typing')
async def handle_typing(event: ThreadTypingEvent):
    if event.is_typing:
        print(f"{event.user.name} is typing in thread {event.thread_id}")
    else:
        print(f"{event.user.name} stopped typing")
```

### CounterUpdateEvent

Represents a counter update event.

**Properties:**
- `type` (str): Event type ("COUNTER_UPDATE")
- `counters` (EventCounters): Updated counter values

**Example:**
```python
@ws.on('on_notification')
async def handle_counters(event: CounterUpdateEvent):
    print(f"Notifications: {event.counters.new_notifications}")
    print(f"Friend requests: {event.counters.new_friend_requests}")
```

## Migration from Raw Data

### Before (using raw dictionaries):

```python
@ws.on('on_message')
async def handle_message(data):
    sender_name = data.get('sender', {}).get('name', 'Unknown')
    message_text = data.get('data', {}).get('message', '')
    unread = data.get('counters', {}).get('unread_threads', 0)
    
    print(f"From {sender_name}: {message_text}")
    print(f"Unread: {unread}")
```

### After (using structured models):

```python
@ws.on('on_message')
async def handle_message(event: ThreadNewMessageEvent):
    # Clean, type-safe access with autocomplete
    print(f"From {event.sender.name}: {event.message}")
    print(f"Unread: {event.counters.unread_threads}")
```

## Benefits

1. **Type Safety**: IDEs can provide autocomplete and type checking
2. **Cleaner Code**: No more nested `.get()` calls
3. **Better Defaults**: Missing fields are handled consistently
4. **Documentation**: Clear structure shows what data is available
5. **Convenience**: Quick access properties for common operations
6. **Extensibility**: Easy to add methods and computed properties

## Complete Example

See `examples/websocket_events_example.py` for a complete working example that demonstrates:
- Handling new messages with full event data
- Accessing sender information
- Using counters
- Replying to messages
- Handling typing indicators
- Processing counter updates

## Type Hints

For best IDE support, import and use type hints:

```python
from interpal.models import (
    ThreadNewMessageEvent,
    ThreadTypingEvent,
    CounterUpdateEvent,
    EventCounters,
    User,
)

@ws.on('on_message')
async def handle_message(event: ThreadNewMessageEvent) -> None:
    sender: User = event.sender
    counters: EventCounters = event.counters
    # IDE will provide autocomplete for all properties
```

## Converting Models to Dictionaries

All models support conversion back to dictionaries:

```python
# Convert to dict
event_dict = event.to_dict()

# Convert to JSON string
event_json = event.to_json(indent=2)
```

## Accessing Raw Data

If you need the original raw data, it's still available:

```python
raw_data = event._data
```

However, we recommend using the structured properties for better code quality and maintainability.

