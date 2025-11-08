# Interpals Python Library

A comprehensive Python library for the Interpals API, providing both synchronous and asynchronous interfaces with WebSocket support for real-time events. Designed similar to discord.py for ease of use and powerful functionality.

## Features

✨ **Dual Interface**: Both sync and async client support
🔐 **Flexible Authentication**: Auto-login or manual cookie import
🌐 **WebSocket Support**: Real-time events and notifications
📝 **Comprehensive Models**: Fully typed data models for all API responses
🎯 **Event System**: Decorator-based event handlers (@client.event)
🔄 **Auto-retry**: Built-in retry logic with exponential backoff
⚡ **Rate Limiting**: Automatic rate limit handling
📦 **Complete API Coverage**: 70+ endpoints across all categories
🧠 **Smart State Management**: Memory-efficient caching with Discord.py patterns
⚡ **Object Identity**: Same user/profile objects reused throughout session
🔄 **Automatic Updates**: Cached objects update when new data arrives
💾 **Configurable Caching**: Fine-tune memory usage and performance

## Installation

```bash
pip install interpal
```

Or install from source:

```bash
git clone https://github.com/yourusername/interpal.git
cd interpal
pip install -e .
```

### Requirements

- Python 3.7+
- requests >= 2.28.0
- aiohttp >= 3.8.0
- websockets >= 10.0

## Quick Start

### Synchronous Usage

```python
from interpal import InterpalClient

# Auto-login with credentials
client = InterpalClient(
    username="your_username",
    password="your_password",
    auto_login=True
)

# Get your profile
profile = client.get_self()
print(f"Logged in as: {profile.name}")

# Get message threads
threads = client.get_threads()
print(f"You have {len(threads)} message threads")

# Send a message
client.send_message(thread_id="123456", content="Hello from Python!")

# Search for users
users = client.search_users(country="Japan", age_min=20, age_max=30)
for user in users:
    print(f"{user.name}, {user.age}, {user.city}")

# State management features
print(f"Cache stats: {client.get_cache_stats()}")
print(f"Messages cached: {client.state._stats['objects_created']}")

# Close connections
client.close()
```

### Asynchronous Usage

```python
import asyncio
from interpal import AsyncInterpalClient

async def main():
    client = AsyncInterpalClient(
        username="your_username",
        password="your_password"
    )
    client.login()
    
    # Fetch multiple things concurrently
    profile, threads, notifications = await asyncio.gather(
        client.get_self(),
        client.get_threads(),
        client.get_notifications()
    )
    
    print(f"Welcome {profile.name}!")
    print(f"Threads: {len(threads)}, Notifications: {len(notifications)}")
    
    await client.close()

asyncio.run(main())
```

### State Management & Caching

The library automatically manages state and caching to improve performance and memory efficiency:

```python
from interpal import InterpalClient

# Configure caching behavior
client = InterpalClient(
    username="user",
    password="pass",
    auto_login=True,
    max_messages=2000,        # Cache up to 2000 messages (default: 1000)
    cache_users=True,         # Enable user caching (default: True)
    cache_threads=True,       # Enable thread caching (default: True)
    weak_references=True      # Use weak references for memory efficiency (default: True)
)

# Get cache statistics
stats = client.get_cache_stats()
print(f"Cache hit rate: {stats['hit_rate']:.2%}")
print(f"Objects created: {stats['objects_created']}")
print(f"Cache evictions: {stats['evictions']}")

# Access cached objects directly
cached_user = client.get_cached_user("123456")
if cached_user:
    print(f"User from cache: {cached_user.name}")

# Clear caches if needed
client.clear_user_cache()     # Clear only user cache
client.clear_message_cache()  # Clear only message cache
client.clear_caches()         # Clear all caches
```

**State Management Benefits:**
- 🧠 **Memory Efficiency**: Weak references prevent memory leaks
- ⚡ **Performance**: Reduced API calls through intelligent caching
- 🔄 **Object Identity**: Same user object returned from different API calls
- 📊 **Statistics**: Monitor cache performance and usage
- ⚙️ **Configurable**: Fine-tune caching for your use case

### Real-time Events (WebSocket)

```python
import asyncio
from interpal import AsyncInterpalClient

client = AsyncInterpalClient(session_cookie="your_session_cookie")

@client.event('on_ready')
async def on_ready(data=None):
    print("Bot is ready!")
    profile = await client.get_self()
    print(f"Logged in as: {profile.name}")

@client.event('on_message')
async def on_message(data):
    sender = data.get('sender', {}).get('name', 'Unknown')
    content = data.get('content', '')
    print(f"New message from {sender}: {content}")
    
    # Auto-reply
    if 'hello' in content.lower():
        thread_id = data.get('thread_id')
        await client.send_message(thread_id, "Hi there!")

@client.event('on_notification')
async def on_notification(data):
    print(f"New notification: {data.get('message')}")

# Start listening (runs indefinitely)
asyncio.run(client.start())
```

### Bot Extension (Discord.py-style Commands)

Build command-based bots with a familiar Discord.py-style interface:

```python
from interpal.ext.commands import Bot

bot = Bot(
    command_prefix='!',
    username='your_username',
    password='your_password',
    persist_session=True
)

@bot.command()
async def hello(ctx, name=None):
    """Say hello to someone"""
    if name:
        await ctx.send(f"Hello {name}! 👋")
    else:
        await ctx.send(f"Hello {ctx.sender_name}! 👋")

@bot.command(aliases=['add'])
async def calculate(ctx, num1: int, num2: int):
    """Add two numbers"""
    await ctx.send(f"Result: {num1 + num2}")

@bot.event
async def on_ready():
    print("🤖 Bot is ready!")
    profile = await bot.get_self()
    print(f"Logged in as: {profile.name}")

bot.run()
```

**Features:**
- 🎯 Command decorators (`@bot.command()`)
- 🔧 Automatic argument parsing with type conversion
- 📚 Built-in help command
- 🎨 Command aliases
- 📦 Cogs for organizing commands
- ⚠️ Error handling

See the [Bot Extension Guide](docs/BOT_EXTENSION.md) for complete documentation.

## Authentication

### Method 1: Persistent Sessions (Recommended)

Automatically save and reuse sessions for 24 hours - no need to login every time!

```python
client = InterpalClient(
    username="user",
    password="pass",
    auto_login=True,
    persist_session=True  # Session saved and reused for 24 hours
)

# First run: Logs in and saves session
# Next runs: Automatically uses saved session until it expires
# After 24 hours: Automatically re-logins and saves new session
```

Check session status:

```python
session_info = client.get_session_info()
print(f"Time remaining: {session_info['time_remaining']}")
print(f"Expires at: {session_info['expires_at']}")
```

Custom session configuration:

```python
client = InterpalClient(
    username="user",
    password="pass",
    auto_login=True,
    persist_session=True,
    session_file="my_session.json",  # Custom file location
    session_expiration_hours=48  # Expire after 48 hours
)
```

### Method 2: Login with Credentials

```python
client = InterpalClient(username="user", password="pass", auto_login=True)
```

### Method 3: Import Session Cookie

```python
client = InterpalClient(session_cookie="interpals_sessid=abc123...")
client.validate_session()
```

### Method 4: Export/Import Session

```python
# Export session for later use
session = client.export_session()
print(session['session_cookie'])

# Import it later
client = InterpalClient(
    session_cookie=session['session_cookie'],
    auth_token=session['auth_token']
)
```

## API Coverage

### User Management
- `get_self()` - Get current user profile
- `update_self(**kwargs)` - Update profile
- `get_user(user_id)` - Get user by ID
- `get_counters()` - Get user statistics
- `get_settings()` - Get user settings
- `update_settings(**kwargs)` - Update settings

### Messaging
- `get_threads()` - Get message threads
- `get_thread_messages(thread_id)` - Get messages in thread
- `send_message(thread_id, content)` - Send message
- `mark_thread_viewed(thread_id)` - Mark as read
- `set_typing(thread_id)` - Send typing indicator

### Search & Discovery
- `search_users(**filters)` - Search users with filters
- `search_by_location(lat, lon, radius)` - Location-based search
- `get_feed()` - Get main content feed
- `get_nearby_users()` - Get nearby users
- `get_suggestions()` - Get suggested users

### Media & Photos
- `upload_photo(file_path, caption)` - Upload photo
- `get_photo(photo_id)` - Get photo details
- `get_user_photos(user_id)` - Get user's photos
- `get_album(album_id)` - Get album
- `create_album(name, description)` - Create album

### Social Features
- `get_friends()` - Get friends list
- `block_user(user_id)` - Block user
- `unblock_user(user_id)` - Unblock user
- `bookmark_user(user_id, note)` - Bookmark user
- `like_content(content_id, type)` - Like content

### Real-time & Notifications
- `get_notifications()` - Get notifications
- `mark_notification_read(id)` - Mark as read
- `register_push_token(token)` - Register for push
- `get_views()` - Get profile views

## Data Models

All API responses are automatically parsed into comprehensive data models:

```python
# User Profile
profile = client.get_self()
print(profile.name)        # str
print(profile.age)         # int
print(profile.country)     # str
print(profile.bio)         # str
print(profile.languages)   # List[str]

# Message Thread
thread = client.get_threads()[0]
print(thread.id)                    # str
print(thread.participants)          # List[User]
print(thread.last_message.content)  # str
print(thread.unread_count)          # int

# Notification
notif = client.get_notifications()[0]
print(notif.type)         # str
print(notif.message)      # str
print(notif.actor.name)   # str
print(notif.read)         # bool
```

## Event System

### Available Events

- `on_ready` - Client connected and ready
- `on_message` - New message received
- `on_typing` - User typing indicator
- `on_notification` - New notification
- `on_status_change` - User status change
- `on_user_online` - User comes online
- `on_user_offline` - User goes offline
- `on_disconnect` - WebSocket disconnected

### Registering Events

```python
# Method 1: Using decorator
@client.event('on_message')
async def handle_message(data):
    print(f"Message: {data}")

# Method 2: Programmatically
async def my_handler(data):
    print(f"Notification: {data}")

client._ws_client.register_event('on_notification', my_handler)
```

## Error Handling

The library provides comprehensive exception handling:

```python
from interpal import (
    InterpalException,
    AuthenticationError,
    APIError,
    RateLimitError,
    WebSocketError,
    ValidationError
)

try:
    client.login()
except AuthenticationError as e:
    print(f"Login failed: {e}")
except APIError as e:
    print(f"API error ({e.status_code}): {e}")
except RateLimitError as e:
    print(f"Rate limited. Retry after {e.retry_after} seconds")
```

## Advanced Usage

### State Management & Caching

```python
# Configure cache for high-usage applications
client = InterpalClient(
    username="user",
    password="pass",
    max_messages=5000,        # Increase cache size for bots
    cache_users=True,         # Always cache users
    cache_threads=True,       # Cache message threads
    weak_references=False     # Disable weak refs for long-running bots
)

# Monitor cache performance
def monitor_cache():
    stats = client.get_cache_stats()
    if stats['hit_rate'] < 0.5:  # Low hit rate
        print("Consider increasing cache size")
    if stats['evictions'] > 100:  # Many evictions
        print("Cache is too small, increase max_messages")

# Periodic cache cleanup (useful for long-running bots)
import time

def cache_maintenance_loop():
    while True:
        time.sleep(3600)  # Every hour
        stats = client.get_cache_stats()
        print(f"Cache stats: {stats}")

        # Clear old caches if memory is high
        if stats['cache_sizes']['messages'] > 4000:
            client.clear_message_cache()
```

### Custom User Agent

```python
client = InterpalClient(
    username="user",
    password="pass",
    user_agent="my-app/2.0.0"
)
```

### Rate Limiting Configuration

```python
from interpal.http import HTTPClient

# Adjust minimum request interval (default: 1 second)
client.http._min_request_interval = 2.0  # 2 seconds between requests
```

### Retry Configuration

```python
from interpal import InterpalClient
from interpal.http import HTTPClient

client = InterpalClient(...)
client.http.max_retries = 5  # Default: 3
```

### WebSocket Reconnection

```python
# Configure reconnection behavior
client._ws_client._max_reconnect_attempts = 10  # Default: 5
client._ws_client._reconnect_delay = 3  # Default: 2 seconds
```

## Examples

Check the `examples/` directory for complete examples:

- `basic_sync.py` - Basic synchronous usage
- `async_example.py` - Asynchronous operations (updated with state management)
- `realtime_bot.py` - Real-time bot with event handlers
- `bot_example.py` - **UPDATED: Full-featured bot with state management (v2.0.0)**
- `bot_with_cogs.py` - Advanced bot with Cogs (command groups)
- `state_management_demo.py` - **NEW: State management and caching features**

## Testing

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run tests with coverage
pytest --cov=interpal tests/
```

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This is an unofficial library and is not affiliated with or endorsed by Interpals. Use at your own risk and in accordance with Interpals' Terms of Service.

## Documentation

For detailed documentation, please refer to the `docs/` folder:

- 📚 [Getting Started Guide](docs/GETTING_STARTED.md) - Detailed setup and first steps
- ⚡ [Quick Start Guide](docs/QUICKSTART.md) - Get up and running quickly
- 📖 [API Reference](docs/API_REFERENCE.md) - Complete API documentation
- 🤖 [Bot Extension Guide](docs/BOT_EXTENSION.md) - Build command-based bots (Discord.py-style)
- 🧠 **NEW: [State Management Guide](docs/STATE_MANAGEMENT.md)** - Smart caching and performance optimization
- 🔄 **NEW: [Migration Guide](docs/MIGRATION_GUIDE.md)** - Upgrade from v1.x to v2.0.0
- 🔐 [Session Persistence Guide](docs/SESSION_PERSISTENCE_GUIDE.md) - Automatic session management
- 🔧 [API Endpoint Corrections](docs/API_ENDPOINT_CORRECTIONS.md) - Verified API endpoints
- 🏗️ [Project Structure](docs/PROJECT_STRUCTURE.md) - Understanding the codebase
- 📝 [Implementation Summary](docs/IMPLEMENTATION_SUMMARY.md) - Technical implementation details
- ✅ [Verification Checklist](docs/VERIFICATION_CHECKLIST.md) - Testing and verification guide

## Support

- 📖 [Documentation](https://github.com/yourusername/interpal-python-lib/wiki)
- 🐛 [Issue Tracker](https://github.com/yourusername/interpal-python-lib/issues)
- 💬 [Discussions](https://github.com/yourusername/interpal-python-lib/discussions)

## Changelog

### Version 1.0.0 (Initial Release)

- ✅ Complete API coverage for 70+ endpoints
- ✅ Synchronous and asynchronous client support
- ✅ WebSocket support for real-time events
- ✅ Comprehensive data models
- ✅ Event system with decorators
- ✅ Authentication management
- ✅ Rate limiting and auto-retry
- ✅ Full documentation and examples

## Acknowledgments

- Inspired by [discord.py](https://github.com/Rapptz/discord.py)
- Built with love for the Interpals community

---

Made with ❤️ by the Interpals Python Library Contributors

