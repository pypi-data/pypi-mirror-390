# API Reference

Complete API reference for the Interpals Python Library.

## Table of Contents

- [Client Classes](#client-classes)
- [User API](#user-api)
- [Messages API](#messages-api)
- [Search API](#search-api)
- [Media API](#media-api)
- [Social API](#social-api)
- [Realtime API](#realtime-api)
- [Data Models](#data-models)
- [Exceptions](#exceptions)

---

## Client Classes

### InterpalClient

Synchronous client for Interpals API.

```python
client = InterpalClient(
    username: Optional[str] = None,
    password: Optional[str] = None,
    session_cookie: Optional[str] = None,
    auth_token: Optional[str] = None,
    auto_login: bool = False,
    user_agent: str = "interpal-python-lib/1.0.0"
)
```

**Methods:**
- `login(username, password)` - Login with credentials
- `import_session(cookie_string, auth_token)` - Import existing session
- `export_session()` - Export current session
- `validate_session()` - Validate current session
- `close()` - Close all connections

### AsyncInterpalClient

Asynchronous client for Interpals API.

```python
client = AsyncInterpalClient(
    username: Optional[str] = None,
    password: Optional[str] = None,
    session_cookie: Optional[str] = None,
    auth_token: Optional[str] = None,
    user_agent: str = "interpal-python-lib/1.0.0"
)
```

**Async Methods:**
- `async close()` - Close all connections
- All API methods are async (use `await`)

---

## User API

Access via `client.user`

### get_self()

Get current user's profile.

```python
profile = client.user.get_self()
```

**Returns:** `Profile` object

### update_self(**kwargs)

Update current user's profile.

```python
profile = client.user.update_self(
    bio="New bio",
    age=25,
    city="New York"
)
```

**Parameters:**
- `**kwargs` - Profile fields to update

**Returns:** Updated `Profile` object

### get_user(user_id)

Get user profile by ID.

```python
profile = client.user.get_user("123456789")
```

**Parameters:**
- `user_id` (str) - User ID

**Returns:** `Profile` object

### get_counters()

Get user statistics.

```python
counters = client.user.get_counters()
print(f"Messages: {counters.messages}")
print(f"Friends: {counters.friends}")
```

**Returns:** `UserCounters` object

### get_settings()

Get user settings.

```python
settings = client.user.get_settings()
```

**Returns:** `UserSettings` object

### update_settings(**kwargs)

Update user settings.

```python
settings = client.user.update_settings(
    email_notifications=True,
    language="en"
)
```

**Returns:** Updated `UserSettings` object

---

## Messages API

Access via `client.messages`

### get_threads(limit=50, offset=0)

Get message threads list.

```python
threads = client.messages.get_threads(limit=20)
```

**Parameters:**
- `limit` (int) - Maximum threads to return
- `offset` (int) - Pagination offset

**Returns:** List of `Thread` objects

### get_thread_messages(thread_id, limit=50, offset=0)

Get messages in a thread.

```python
messages = client.messages.get_thread_messages("123456", limit=50)
```

**Parameters:**
- `thread_id` (str) - Thread ID
- `limit` (int) - Maximum messages
- `offset` (int) - Pagination offset

**Returns:** List of `Message` objects

### send_message(thread_id, content, **kwargs)

Send a message.

```python
message = client.messages.send_message(
    thread_id="123456",
    content="Hello!"
)
```

**Parameters:**
- `thread_id` (str) - Thread ID
- `content` (str) - Message content
- `**kwargs` - Additional parameters

**Returns:** `Message` object

### mark_thread_viewed(thread_id)

Mark thread as read.

```python
client.messages.mark_thread_viewed("123456")
```

### set_typing(thread_id, typing=True)

Send typing indicator.

```python
client.messages.set_typing("123456", typing=True)
```

---

## Search API

Access via `client.search`

### search_users(**filters)

Search for users with filters.

```python
users = client.search.search_users(
    country="Japan",
    age_min=20,
    age_max=30,
    gender="female",
    language="English",
    online_only=True,
    limit=50
)
```

**Parameters:**
- `query` (str) - Search query
- `age_min` (int) - Minimum age
- `age_max` (int) - Maximum age
- `gender` (str) - Gender filter
- `country` (str) - Country filter
- `city` (str) - City filter
- `language` (str) - Language filter
- `looking_for` (str) - Looking for filter
- `online_only` (bool) - Only online users
- `limit` (int) - Maximum results
- `offset` (int) - Pagination offset

**Returns:** List of `Profile` objects

### search_by_location(latitude, longitude, radius=50, limit=50)

Search users by location.

```python
users = client.search.search_by_location(
    latitude=35.6762,
    longitude=139.6503,
    radius=100
)
```

**Returns:** List of `Profile` objects

### get_feed(limit=50, offset=0)

Get main content feed.

```python
feed = client.search.get_feed(limit=20)
```

**Returns:** List of feed items

---

## Media API

Access via `client.media`

### upload_photo(file_path, caption=None, album_id=None)

Upload a photo.

```python
photo = client.media.upload_photo(
    file_path="photo.jpg",
    caption="Beautiful sunset!"
)
```

**Parameters:**
- `file_path` (str) - Path to photo file
- `caption` (str) - Photo caption
- `album_id` (str) - Album ID

**Returns:** `Photo` object

### get_user_photos(user_id, limit=50, offset=0)

Get user's photos.

```python
photos = client.media.get_user_photos("123456")
```

**Returns:** List of `Photo` objects

### get_user_albums(user_id)

Get user's albums.

```python
albums = client.media.get_user_albums("123456")
```

**Returns:** List of `Album` objects

### create_album(name, description=None)

Create new album.

```python
album = client.media.create_album(
    name="Vacation 2024",
    description="Summer vacation photos"
)
```

**Returns:** `Album` object

---

## Social API

Access via `client.social`

### get_friends(user_id=None)

Get friends list.

```python
friends = client.social.get_friends()
```

**Returns:** List of `Relationship` objects

### block_user(user_id)

Block a user.

```python
client.social.block_user("123456")
```

### unblock_user(user_id)

Unblock a user.

```python
client.social.unblock_user("123456")
```

### bookmark_user(user_id, note=None)

Bookmark a user.

```python
bookmark = client.social.bookmark_user(
    user_id="123456",
    note="Interesting person"
)
```

**Returns:** `Bookmark` object

### like_content(content_id, content_type="photo")

Like content.

```python
like = client.social.like_content(
    content_id="789",
    content_type="photo"
)
```

**Returns:** `Like` object

---

## Realtime API

Access via `client.realtime`

### get_notifications(limit=50, offset=0, unread_only=False)

Get notifications.

```python
notifications = client.realtime.get_notifications(
    limit=20,
    unread_only=True
)
```

**Returns:** List of `Notification` objects

### mark_notification_read(notification_id)

Mark notification as read.

```python
client.realtime.mark_notification_read("123456")
```

### get_views(limit=50)

Get profile views.

```python
views = client.realtime.get_views()
```

**Returns:** List of view data

---

## Data Models

### User

Basic user information.

**Attributes:**
- `id` (str) - User ID
- `username` (str) - Username
- `name` (str) - Display name
- `age` (int) - Age
- `gender` (str) - Gender
- `country` (str) - Country
- `city` (str) - City
- `avatar_url` (str) - Avatar URL
- `is_online` (bool) - Online status
- `last_active` (datetime) - Last active time

### Profile

Extended profile (inherits from User).

**Additional Attributes:**
- `bio` (str) - Biography
- `interests` (List[str]) - Interests
- `languages` (List[str]) - Languages
- `looking_for` (str) - Looking for
- `relationship_status` (str) - Relationship status
- `education_level` (str) - Education level
- `occupation` (str) - Occupation

### Message

Individual message.

**Attributes:**
- `id` (str) - Message ID
- `thread_id` (str) - Thread ID
- `sender` (User) - Sender user
- `content` (str) - Message content
- `timestamp` (datetime) - Message timestamp
- `read` (bool) - Read status
- `attachments` (List[str]) - Attachments

### Thread

Message thread.

**Attributes:**
- `id` (str) - Thread ID
- `participants` (List[User]) - Participants
- `last_message` (Message) - Last message
- `unread_count` (int) - Unread count
- `created_at` (datetime) - Creation time
- `updated_at` (datetime) - Last update time

### Photo

Photo with metadata.

**Attributes:**
- `id` (str) - Photo ID
- `url` (str) - Photo URL
- `thumbnail_url` (str) - Thumbnail URL
- `caption` (str) - Caption
- `owner` (User) - Owner user
- `upload_date` (datetime) - Upload date
- `likes` (int) - Like count

### Notification

User notification.

**Attributes:**
- `id` (str) - Notification ID
- `type` (str) - Notification type
- `title` (str) - Title
- `message` (str) - Message
- `actor` (User) - Actor user
- `read` (bool) - Read status
- `action_url` (str) - Action URL
- `created_at` (datetime) - Creation time

---

## Exceptions

### InterpalException

Base exception class.

```python
from interpal.exceptions import InterpalException
```

### AuthenticationError

Authentication failure.

```python
from interpal.exceptions import AuthenticationError

try:
    client.login()
except AuthenticationError as e:
    print(f"Login failed: {e}")
```

**Attributes:**
- `status_code` (int) - HTTP status code

### APIError

API request failure.

```python
from interpal.exceptions import APIError

try:
    profile = client.get_user("invalid")
except APIError as e:
    print(f"Error {e.status_code}: {e}")
```

**Attributes:**
- `status_code` (int) - HTTP status code
- `response` - Response object

### RateLimitError

Rate limit exceeded.

```python
from interpal.exceptions import RateLimitError

try:
    # Make request
    pass
except RateLimitError as e:
    print(f"Rate limited. Retry after {e.retry_after}s")
```

**Attributes:**
- `retry_after` (int) - Seconds to wait

### WebSocketError

WebSocket connection failure.

```python
from interpal.exceptions import WebSocketError
```

### ValidationError

Invalid parameters.

```python
from interpal.exceptions import ValidationError
```

---

## Event System

### Available Events

- `on_ready` - Client ready
- `on_message` - New message
- `on_typing` - Typing indicator
- `on_notification` - New notification
- `on_status_change` - Status change
- `on_user_online` - User online
- `on_user_offline` - User offline
- `on_disconnect` - Disconnected

### Event Registration

```python
@client.event('on_message')
async def handle_message(data):
    """Handle incoming message."""
    print(f"Message: {data}")
```

---

For more examples, see the [examples](examples/) directory.

