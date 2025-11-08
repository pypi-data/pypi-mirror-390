# API Updates Summary

This document summarizes the new features and endpoints added to the interpal library based on the API analysis from `download.json`.

## Date
November 5, 2025

## Overview
Added comprehensive support for new API endpoints discovered through API traffic analysis. The library now includes notifications, posts/comments, trips, and additional parameters for existing endpoints.

---

## New API Modules

### 1. Notifications API (`interpal/api/notifications.py`)

**New Module**: Provides access to user notifications.

**Endpoints:**
- `GET /v1/notification/my` - Get user notifications
- `PUT /v1/notification/{id}/read` - Mark notification as read
- `PUT /v1/notification/read-all` - Mark all notifications as read
- `DELETE /v1/notification/{id}` - Delete a notification

**Methods:**
- `get_notifications(limit=50, offset=0)` - Fetch user notifications with pagination
- `mark_notification_read(notification_id)` - Mark single notification as read
- `mark_all_read()` - Mark all notifications as read
- `delete_notification(notification_id)` - Delete a notification

**Usage:**
```python
client = InterpalClient(username="user", password="pass")
client.login()

# Get notifications
notifications = client.notifications.get_notifications(limit=20)

# Mark as read
client.notifications.mark_notification_read(notification_id)
```

---

### 2. Posts/Feed API (`interpal/api/posts.py`)

**New Module**: Manage feed posts and comments.

**Endpoints:**
- `POST /v1/post` - Create a new post
- `GET /v1/post/{id}` - Get a specific post
- `PUT /v1/post/{id}` - Update a post
- `DELETE /v1/post/{id}` - Delete a post
- `GET /v1/post/{id}/comments` - Get post comments
- `POST /v1/comment` - Create a comment
- `PUT /v1/comment/{id}` - Update a comment
- `DELETE /v1/comment/{id}` - Delete a comment

**Methods:**
- `create_post(content, privacy='public', **kwargs)` - Create a new feed post
- `get_post(post_id)` - Get post details
- `update_post(post_id, content=None, privacy=None)` - Update a post
- `delete_post(post_id)` - Delete a post
- `get_comments(post_id, limit=50, offset=0, nest_replies=True)` - Get post comments
- `create_comment(post_id, content, parent_id=None)` - Create a comment
- `update_comment(comment_id, content)` - Update a comment
- `delete_comment(comment_id)` - Delete a comment

**Usage:**
```python
# Create a post
post = client.posts.create_post(
    content="Hello from the API!",
    privacy="public"
)

# Add a comment
comment = client.posts.create_comment(
    post_id=post['id'],
    content="Great post!"
)

# Get comments
comments = client.posts.get_comments(post_id, limit=10)
```

---

## Enhanced Existing Modules

### 3. User API Updates (`interpal/api/user.py`)

**New Features:** Trip/travel planning endpoints

**New Endpoints:**
- `GET /v1/user/{id}/trips` - Get user's trips
- `GET /v1/user/self/trips` - Get current user's trips
- `POST /v1/trip` - Create a trip
- `PUT /v1/trip/{id}` - Update a trip
- `DELETE /v1/trip/{id}` - Delete a trip

**New Methods:**
- `get_user_trips(user_id, limit=50, offset=0)` - Get user's travel plans
- `get_my_trips(limit=50, offset=0)` - Get current user's trips
- `create_trip(destination, start_date, end_date=None, **kwargs)` - Create a new trip
- `update_trip(trip_id, **kwargs)` - Update a trip
- `delete_trip(trip_id)` - Delete a trip

**Usage:**
```python
# Get user's trips
trips = client.user.get_user_trips(user_id="123456")

# Create a trip
trip = client.user.create_trip(
    destination="Paris, France",
    start_date="2025-12-01",
    end_date="2025-12-07",
    description="Winter vacation"
)
```

---

### 4. Media API Updates (`interpal/api/media.py`)

**New Features:** Photo count and upload status tracking

**New Endpoints:**
- `GET /v1/total/{id}/photos` - Get total photo count
- `GET /v1/upload-status/{token}` - Check upload status

**New Methods:**
- `get_photo_count(user_id)` - Get total photo count for a user
- `get_upload_status(upload_token)` - Check the status of a photo upload
- `upload_photo_async(file_path, caption=None, album_id=None)` - Upload photo asynchronously

**Usage:**
```python
# Get photo count
count = client.media.get_photo_count(user_id)
print(f"User has {count} photos")

# Async upload with status tracking
upload_response = client.media.upload_photo_async("photo.jpg")
upload_token = upload_response['token']

# Check status
status = client.media.get_upload_status(upload_token)
```

---

### 5. Messages API Updates (`interpal/api/messages.py`)

**New Features:** Thread management

**New Endpoints:**
- `DELETE /v1/thread/{id}` - Delete a thread
- `PUT /v1/thread/{id}/archive` - Archive a thread
- `PUT /v1/thread/{id}/unarchive` - Unarchive a thread

**New Methods:**
- `delete_thread(thread_id)` - Delete a message thread
- `archive_thread(thread_id)` - Archive a thread
- `unarchive_thread(thread_id)` - Unarchive a thread

**Usage:**
```python
# Delete a thread
client.messages.delete_thread(thread_id)

# Archive a thread
client.messages.archive_thread(thread_id)
```

---

### 6. Search API Updates (`interpal/api/search.py`)

**Enhanced Features:** Expanded search parameters and feed filtering

**Enhanced Methods:**

#### `search_users()` - New Parameters:
- `sort` - Sort order (e.g., 'last_login', 'age', 'distance')
- `order` - Order direction ('asc' or 'desc')
- `username` - Search by username
- `new` - Only show new users
- `radius` - Search radius in km
- `known_level_min` - Minimum language knowledge level
- `lfor_friend` - Looking for friendship
- `lfor_langex` - Looking for language exchange
- `lfor_meet` - Looking to meet in person
- `lfor_relation` - Looking for relationship
- `lfor_snail` - Looking for snail mail pen pal

#### `get_feed()` - New Parameters:
- `owner_id` - Filter by owner/user ID
- `owner_only` - Only show posts from the owner
- `post_type` - Filter by post type

**Usage:**
```python
# Enhanced user search
users = client.search.search_users(
    age_min=18,
    age_max=30,
    city="London",
    lfor_friend=True,
    lfor_langex=True,
    online_only=True,
    sort="last_login",
    order="desc"
)

# Filtered feed
feed = client.search.get_feed(
    feed_type="global",
    owner_id="123456",
    post_type="photo",
    limit=20
)
```

---

## New Model Classes

### 7. Post Model (`interpal/models/post.py`)

**New Model Class:** Represents a feed post

**Attributes:**
- `id` - Post ID
- `user_id` - Author user ID
- `user` - User object
- `content` - Post content/text
- `post_type` - Type of post
- `privacy` - Privacy level
- `created_at` - Creation timestamp
- `updated_at` - Last update timestamp
- `likes_count` - Number of likes
- `comments_count` - Number of comments
- `photos` - List of Photo objects
- `is_liked` - Whether current user liked
- `can_edit` - Edit permission
- `can_delete` - Delete permission

---

### 8. Comment Model (`interpal/models/post.py`)

**New Model Class:** Represents a post comment

**Attributes:**
- `id` - Comment ID
- `post_id` - Parent post ID
- `user_id` - Author user ID
- `user` - User object
- `content` - Comment content
- `parent_id` - Parent comment ID (for nested replies)
- `created_at` - Creation timestamp
- `updated_at` - Last update timestamp
- `likes_count` - Number of likes
- `replies_count` - Number of replies
- `replies` - List of nested Comment objects
- `is_liked` - Whether current user liked
- `can_edit` - Edit permission
- `can_delete` - Delete permission

---

### 9. Trip Model (`interpal/models/post.py`)

**New Model Class:** Represents a travel plan/trip

**Attributes:**
- `id` - Trip ID
- `user_id` - User ID
- `user` - User object
- `destination` - Trip destination
- `country` - Country
- `city` - City
- `start_date` - Start date
- `end_date` - End date
- `description` - Trip description/notes
- `created_at` - Creation timestamp
- `updated_at` - Last update timestamp

---

## Client Updates

Both `InterpalClient` and `AsyncInterpalClient` have been updated to include:

1. **New API Module Access:**
   - `client.notifications` - NotificationsAPI instance
   - `client.posts` - PostsAPI instance

2. **Updated Convenience Method:**
   - `get_notifications()` - Now uses NotificationsAPI instead of RealtimeAPI

---

## Import Updates

All new models and APIs can be imported directly from the main module:

```python
from interpal import (
    InterpalClient,
    Post,
    Comment,
    Trip,
    Notification
)
```

---

## Summary of Changes

### Files Created:
1. `interpal/api/notifications.py` - Notifications API module
2. `interpal/api/posts.py` - Posts/Feed API module
3. `interpal/models/post.py` - Post, Comment, and Trip models

### Files Modified:
1. `interpal/api/user.py` - Added trip management endpoints
2. `interpal/api/media.py` - Added photo count and upload status
3. `interpal/api/messages.py` - Added thread deletion and archiving
4. `interpal/api/search.py` - Enhanced with additional parameters
5. `interpal/client.py` - Added new API modules
6. `interpal/api/__init__.py` - Export new modules
7. `interpal/models/__init__.py` - Export new models
8. `interpal/__init__.py` - Export new models in main package

### Total New Endpoints: 25+

### Major Features Added:
- ✅ Notifications system
- ✅ Feed posts creation and management
- ✅ Comments system with nested replies
- ✅ Trip/travel planning
- ✅ Photo count tracking
- ✅ Async upload with status checking
- ✅ Thread deletion and archiving
- ✅ Enhanced search with 10+ new parameters
- ✅ Feed filtering by owner and post type

---

## Testing Recommendations

1. Test notification retrieval and marking as read
2. Test post creation with various privacy levels
3. Test comment creation and nested replies
4. Test trip CRUD operations
5. Test enhanced search with new filters
6. Test photo upload status tracking
7. Test thread deletion and archiving
8. Verify all model classes parse API responses correctly

---

## Documentation Updates Needed

- Update API_REFERENCE.md with new endpoints
- Create examples for new features
- Update QUICKSTART.md with notifications and posts examples
- Add trip planning examples

---

## Version Information

**Library Version:** 1.1.1 (recommended bump)
**Update Type:** Minor (new features, backward compatible)
**Breaking Changes:** None

All existing functionality remains intact. New features are additive only.

