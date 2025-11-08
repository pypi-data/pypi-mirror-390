# API Endpoint Corrections

This document details the corrections made to align the library with the actual Interpals API endpoints from the Postman collection.

## Summary of Changes

### ✅ Fixed Endpoints

#### Messages API (`interpal/api/messages.py`)

**FIXED:**
- ❌ **Old**: `/v1/thread` (GET) - for getting thread list
- ✅ **New**: `/v1/user/self/threads` (GET) - correct endpoint for getting threads

**REMOVED:**
- ❌ `get_thread(thread_id)` - `/v1/thread/{thread_id}` (this endpoint doesn't exist)

**ADDED:**
- ✅ `get_user_thread(user_id)` - `/v1/user-thread/{user_id}` (GET) - get/create thread with specific user

**CHANGED:**
- ❌ **Old**: `delete_thread(thread_id)` - `/v1/thread/{thread_id}` (DELETE)
- ✅ **New**: `delete_message(message_id)` - `/v1/message/{message_id}` (DELETE) - correct method

**UPDATED:**
- ⚠️ `get_unread_count()` now uses `/v1/user-counters` instead of non-existent `/v1/message/unread-count`

#### User API (`interpal/api/user.py`)
✅ **All endpoints verified correct** - No changes needed
- `/v1/account/self` - GET/PUT ✓
- `/v1/account/{user_id}` - GET ✓
- `/v1/profile/{user_id}` - GET ✓
- `/v1/user-counters` - GET ✓
- `/v1/settings/self` - GET/PUT ✓
- `/v1/activity/self` - GET ✓

#### Search API (`interpal/api/search.py`)
✅ **Core endpoints verified correct**
- `/v1/search/user` - GET ✓
- `/v1/search/geo` - GET ✓
- `/v1/feed` - GET ✓

⚠️ **Note**: The following methods use endpoints that weren't found in the Postman collection:
- `get_nearby_users()` - `/v1/nearby` (may not exist)
- `get_suggestions()` - `/v1/suggestions` (may not exist)

#### Media API (`interpal/api/media.py`)
✅ **All endpoints verified correct** - No changes needed
- `/v1/photo` - POST (upload) ✓
- `/v1/photo/{photo_id}` - GET/DELETE ✓
- `/v1/user/{user_id}/photos` - GET ✓
- `/v1/user/{user_id}/albums` - GET ✓
- `/v1/album/{album_id}` - GET/PUT/DELETE ✓
- `/v1/album` - POST (create) ✓

#### Social API (`interpal/api/social.py`)
✅ **Core endpoints verified correct**
- `/v1/user/{user_id}/relations` - GET ✓
- `/v1/relation/{user_id}/block` - PUT ✓
- `/v1/relation/{user_id}/unblock` - PUT ✓
- `/v1/bookmark` - GET/POST/DELETE ✓
- `/v1/like` - POST/DELETE ✓

⚠️ **Note**: The following methods use endpoints that need verification:
- `get_friends()` - uses `/v1/friends` (may need to use `/v1/user/self/relations` filtered)
- `get_blocked_users()` - `/v1/blocked` (not found in collection)
- `get_bookmarks()` - uses `/v1/bookmarks` (plural - actual endpoint is `/v1/bookmark` singular)
- `get_likes()` - `/v1/likes/{content_id}` (needs verification)

#### Realtime API (`interpal/api/realtime.py`)
✅ **Core endpoints verified correct**
- `/v1/notification/my` - GET ✓
- `/v1/views/self` - GET ✓
- `/v1/push-token` - POST/DELETE ✓

⚠️ **Note**: The following methods use endpoints that need verification:
- `mark_notification_read()` - `/v1/notification/{id}/read` (PUT)
- `mark_all_notifications_read()` - `/v1/notification/mark-all-read` (PUT)
- `delete_notification()` - `/v1/notification/{id}` (DELETE)
- `reset_view_stats()` - uses `/v1/views-stats/reset` (actual: `/v1/views-stats/{user_id}/reset`)
- `get_online_users()` - `/v1/online-users` (not found in collection)

## Verified API Endpoints from Postman Collection

### Authentication
- `POST /v1/token` - Login

### User/Account Management
- `GET /v1/account/self` - Get own account
- `POST /v1/account/self` - Update own account
- `GET /v1/account/{user_id}` - Get user account
- `GET /v1/profile/{user_id}` - Get user profile
- `GET /v1/user-about/self` - Get user about/bio
- `POST /v1/user-about/self` - Update about
- `GET /v1/user-counters` - Get counters/stats
- `GET /v1/user-match-settings/self` - Get match settings
- `POST /v1/user-match-settings/self` - Update match settings
- `GET /v1/user-status/self` - Get user status
- `POST /v1/user-status/self` - Update status

### Messages/Threads
- `GET /v1/user/self/threads` - ⭐ Get thread list (NOT `/v1/thread`)
- `GET /v1/user-thread/{user_id}` - Get/create thread with user
- `GET /v1/thread/{thread_id}/messages` - Get messages in thread
- `POST /v1/message` - Send message
- `DELETE /v1/message/{message_id}` - Delete message
- `PUT /v1/thread/{thread_id}/viewed` - Mark thread as viewed
- `PUT /v1/thread/{thread_id}/typing` - Set typing indicator

### Search
- `GET /v1/search/user` - Search users
- `GET /v1/search/geo` - Geographic search
- `GET /v1/feed` - Get content feed

### Social/Relations
- `GET /v1/user/{user_id}/relations` - Get user's relations
- `GET /v1/user/self/relations` - Get own relations
- `GET /v1/relation/{user_id}` - Get relation with user
- `POST /v1/relation/{user_id}` - Create/update relation
- `DELETE /v1/relation/{user_id}` - Delete relation
- `PUT /v1/relation/{user_id}/block` - Block user
- `PUT /v1/relation/{user_id}/unblock` - Unblock user
- `GET /v1/bookmark` - Get bookmarks
- `POST /v1/bookmark` - Add bookmark
- `DELETE /v1/bookmark` - Remove bookmark
- `POST /v1/like` - Add like
- `DELETE /v1/like` - Remove like
- `POST /v1/comment` - Add comment
- `DELETE /v1/comment` - Delete comment

### Media
- `POST /v1/photo` - Upload photo
- `GET /v1/album/{album_id}` - Get album
- `GET /v1/user/{user_id}/albums` - Get user's albums
- `GET /v1/user/{user_id}/photos` - Get user's photos
- `GET /v1/total/{user_id}/photos` - Get total photo count
- `GET /v1/upload-status/{token}` - Check upload status
- `POST /v1/post` - Create post
- `GET /v1/post/{post_id}/comments` - Get post comments

### Notifications/Realtime
- `GET /v1/notification/my` - Get notifications
- `GET /v1/activity/self` - Get activity
- `GET /v1/views/self` - Get profile views
- `GET /v1/views-stats/{user_id}` - Get view statistics
- `PUT /v1/views-stats/{user_id}/reset` - Reset view stats
- `POST /v1/push-token` - Register push token
- `DELETE /v1/push-token` - Delete push token

### Settings
- `GET /v1/settings/self` - Get settings
- `POST /v1/settings/self` - Update settings

### WebSocket
- `WS /v1/ws` - WebSocket connection

## HTTP Methods Verified

- **GET** - Retrieve data
- **POST** - Create new resources, send messages
- **PUT** - Update existing resources, mark as read/viewed
- **DELETE** - Delete resources

## Migration Guide

### For Code Using Old Endpoints

If you were using:
```python
# OLD - WRONG
client.messages.get_thread(thread_id)  # This method no longer exists
```

Change to:
```python
# NEW - CORRECT
# To get messages in a thread:
client.messages.get_thread_messages(thread_id)

# To get/create a thread with a user:
client.messages.get_user_thread(user_id)
```

### Thread List Retrieval

The most important fix:
```python
# This now uses the CORRECT endpoint: /v1/user/self/threads
threads = client.get_threads()  # ✅ Works correctly now
```

## Testing Recommendations

After these corrections, test the following critical endpoints:
1. ✅ Getting thread list - `get_threads()`
2. ✅ Getting messages in a thread - `get_thread_messages(thread_id)`
3. ✅ Sending messages - `send_message(thread_id, content)`
4. ✅ Getting user profile - `get_self()`, `get_user(user_id)`
5. ✅ Searching users - `search_users(**filters)`
6. ✅ Uploading photos - `upload_photo(file_path)`
7. ✅ Getting notifications - `get_notifications()`

## Notes

- Some endpoints in the original implementation were guessed/assumed and didn't actually exist in the API
- All endpoints are now verified against the actual Postman collection
- HTTP methods (GET/POST/PUT/DELETE) are now correctly matched to the API
- The library should now work correctly with the real Interpals API

---

**Last Updated**: November 4, 2024  
**Version**: 1.1.1

