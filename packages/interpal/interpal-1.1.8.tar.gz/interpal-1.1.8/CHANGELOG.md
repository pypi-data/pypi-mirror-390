# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-11-04

### Added

#### Core Features
- Initial release of Interpals Python Library
- Synchronous client (`InterpalClient`)
- Asynchronous client (`AsyncInterpalClient`)
- WebSocket support for real-time events

#### Authentication
- Cookie-based session authentication
- Username/password login
- Session import/export functionality
- Session validation

#### API Coverage
- **User Management**: Profile, settings, counters, activity
- **Messaging**: Threads, messages, typing indicators
- **Search**: User search, location search, feed, suggestions
- **Media**: Photo upload, albums, media management
- **Social**: Friends, blocking, bookmarks, likes
- **Real-time**: Notifications, views, push tokens

#### Data Models
- `User` - Basic user information
- `Profile` - Extended profile data
- `UserSettings` - User preferences
- `UserCounters` - User statistics
- `Message` - Individual messages
- `Thread` - Message threads
- `TypingIndicator` - Real-time typing status
- `Photo` - Photo metadata
- `Album` - Photo collections
- `MediaUpload` - Upload status
- `Relationship` - User relationships
- `Bookmark` - Bookmarked users
- `Like` - Content likes
- `Notification` - User notifications

#### Event System
- Decorator-based event handlers (`@client.event`)
- Support for multiple event types:
  - `on_ready` - Client connected
  - `on_message` - New message
  - `on_typing` - Typing indicator
  - `on_notification` - New notification
  - `on_status_change` - Status change
  - `on_user_online` - User online
  - `on_user_offline` - User offline
  - `on_disconnect` - WebSocket disconnect

#### HTTP Client
- Rate limiting (60 requests per minute)
- Automatic retry with exponential backoff
- Comprehensive error handling
- Support for both sync and async operations

#### WebSocket Client
- Automatic reconnection with backoff
- Event dispatching system
- Thread-safe event handlers
- Connection health monitoring (ping/pong)

#### Exception Handling
- `InterpalException` - Base exception
- `AuthenticationError` - Auth failures
- `APIError` - API request failures
- `RateLimitError` - Rate limit exceeded
- `WebSocketError` - WebSocket failures
- `ValidationError` - Invalid parameters

#### Examples
- `basic_sync.py` - Synchronous usage examples
- `async_example.py` - Asynchronous usage examples
- `realtime_bot.py` - Real-time bot implementation

#### Documentation
- Comprehensive README with examples
- API documentation with type hints
- Contributing guidelines
- Code of conduct
- MIT License

### Dependencies
- `requests>=2.28.0` - HTTP client
- `aiohttp>=3.8.0` - Async HTTP client
- `websockets>=10.0` - WebSocket support

### Development Tools
- pytest for testing
- black for code formatting
- flake8 for linting
- mypy for type checking

## [1.1.1] - 2024-11-04

### Fixed
- **Critical API Endpoint Corrections**: Fixed incorrect endpoints to match actual Interpals API
  - ✅ **Messages API**: Changed `/v1/thread` to `/v1/user/self/threads` for getting thread list
  - ✅ **Messages API**: Added `get_user_thread(user_id)` using `/v1/user-thread/{user_id}`
  - ✅ **Messages API**: Changed `delete_thread()` to `delete_message(message_id)`
  - ✅ **Messages API**: Fixed `get_unread_count()` to use `/v1/user-counters`
  - ✅ **Feed API**: Fixed `get_feed()` to support `type` parameter (global/following) and `extra` parameter
  - ✅ **Feed API**: Fixed response parsing to correctly return `data` array from feed response
  - ✅ All endpoints now verified against Postman collection

### Documentation
- Added `docs/API_ENDPOINT_CORRECTIONS.md` with full list of corrections
- Documented all verified API endpoints from Postman collection
- Organized all documentation into `docs/` folder

## [1.1.0] - 2024-11-04

### Added
- **Persistent Session Management**: Automatic session storage with configurable expiration
  - Sessions are saved to `.interpals_session.json` by default
  - Configurable session expiration (default: 24 hours)
  - Automatic session validation and re-login on expiration
  - Custom session file paths for multiple accounts
  - Session info and status checking
- New `SessionManager` class for handling persistent sessions
- `persist_session` parameter in `InterpalClient` and `AsyncInterpalClient`
- `session_file` parameter for custom session storage location
- `session_expiration_hours` parameter for configurable expiration
- `get_session_info()` method to check session status
- `clear_saved_session()` method to manually clear saved sessions
- New example: `examples/persistent_session.py`

### Changed
- Updated `InterpalClient` and `AsyncInterpalClient` to support persistent sessions
- Login methods now save sessions when persistence is enabled
- Updated documentation with persistent session examples
- Updated `basic_sync.py` example to use persistent sessions

## [1.2.0] - 2024-11-05

### Added
- **Bot Extension (Discord.py-style Commands)**: Complete command framework for building bots
  - `Bot` class extending `AsyncInterpalClient` with command handling
  - `@bot.command()` decorator for easy command creation
  - Automatic command parsing with argument extraction
  - Type conversion support (int, float, bool, str)
  - Command aliases for multiple trigger words
  - `Context` object providing command context and utilities
  - Built-in help command with automatic generation
  - `Cog` system for organizing commands into groups
  - `@listener()` decorator for event handlers in cogs
  - Custom error handling with `on_command_error`
  - Case-insensitive command matching (configurable)
  - Hidden commands for admin/debug features
  - Variable arguments support (*args)
  - Optional parameters with defaults
  - Command enabling/disabling
  - Full type hints and documentation

#### New Examples
- `examples/simple_bot.py` - Minimal bot setup
- `examples/bot_example.py` - Full-featured command bot
- `examples/bot_with_cogs.py` - Advanced bot with Cogs

#### New Documentation
- `docs/BOT_EXTENSION.md` - Complete guide to building bots
- `docs/BOT_QUICK_REFERENCE.md` - Quick reference cheat sheet

### Changed
- Updated README with Bot Extension section and examples
- Added bot extension to package exports
- Enhanced documentation structure

## [2.0.0] - 2025-11-05

### 🚨 **Breaking Changes**

#### Major Architecture Update
- **State Management System**: Complete rewrite following Discord.py's ConnectionState pattern
- **Object Identity**: Same user/profile objects now reused throughout client session
- **Model Updates**: All models now accept `state` parameter and have `_update()` methods
- **API Module Updates**: API modules now receive `state` parameter for object caching
- **Version Bump**: Bumped to v2.0.0 due to architectural changes

### ✅ **New Features**

#### Smart State Management
- **Centralized State**: New `InterpalState` class manages all object caching
- **Weak Reference Caching**: Memory-efficient caching using `weakref.WeakValueDictionary`
- **LRU Cache Eviction**: Automatic eviction of oldest messages when cache is full
- **Object Factory Patterns**: Consistent object creation with caching
- **Cache Statistics**: Detailed monitoring of cache performance and usage
- **Configurable Caching**: Fine-tune cache behavior for different use cases

#### Performance Improvements
- **Reduced API Calls**: Intelligent caching eliminates redundant requests
- **Memory Management**: Weak references prevent memory leaks from long-lived caches
- **Object Identity**: Same user object returned from multiple API calls
- **Automatic Updates**: Cached objects update when new data arrives

#### New Configuration Options
- `max_messages`: Maximum number of messages to cache (default: 1000)
- `cache_users`: Enable user caching (default: True)
- `cache_threads`: Enable thread caching (default: True)
- `weak_references`: Use weak references for memory efficiency (default: True)

#### New Client Methods
- `get_cache_stats()`: Get detailed cache statistics
- `clear_caches()`: Clear all caches
- `clear_user_cache()`: Clear user cache only
- `clear_message_cache()`: Clear message cache only
- `get_cached_user(user_id)`: Get cached user by ID
- `get_cached_message(message_id)`: Get cached message by ID

### 🔧 **Internal Changes**
- Updated `BaseModel` class to work with state management
- All model classes (`User`, `Profile`, `Message`, `Thread`, etc.) updated for state-awareness
- API modules (`UserAPI`, `MessagesAPI`, etc.) updated to use state factories
- Enhanced error handling and logging in state management
- Improved memory management and garbage collection

### 📚 **Documentation**
- Updated README with state management examples
- Added cache configuration documentation
- Enhanced API documentation with state-aware patterns
- Performance optimization guides added

### 🔄 **Migration Notes**
- Existing code continues to work without changes (backward compatible)
- No breaking changes to public APIs
- New cache features are opt-in with sensible defaults
- Version bump to v2.0.0 reflects architectural improvements, not breaking changes

## [Unreleased]

### Planned Features
- Advanced rate limiting with exponential backoff
- Enhanced event system with predicate filtering
- Batch operations support
- Advanced search filters
- File download utilities
- Image processing helpers
- CLI tool for quick operations
- More comprehensive tests
- Performance optimizations
- Command cooldowns system
- Permission system for commands
- Command groups/categories

### Known Issues
- None currently reported

## Version History

- **2.0.0** (2025-11-05) - **🚀 Major Architecture Update**: Smart State Management with Discord.py patterns
- **1.2.0** (2024-11-05) - Added Bot Extension (Discord.py-style commands)
- **1.1.1** (2024-11-04) - Fixed API endpoint corrections
- **1.1.0** (2024-11-04) - Added persistent session management
- **1.0.0** (2024-11-04) - Initial release

---

For more details, see the [commit history](https://github.com/yourusername/interpal-python-lib/commits/main).

