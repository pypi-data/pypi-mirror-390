# State Management & Caching Guide

## Overview

The Interpal Python Library v2.0+ features a sophisticated state management system inspired by Discord.py's ConnectionState pattern. This system provides intelligent caching, memory-efficient object management, and significant performance improvements.

## 🧠 What is State Management?

State management automatically caches API responses and reuses the same objects throughout your client session. This means:

- **Object Identity**: The same `User` object is returned when you fetch the same user multiple times
- **Memory Efficiency**: Weak references prevent memory leaks from long-lived caches
- **Performance**: Reduced API calls through intelligent caching
- **Automatic Updates**: Cached objects update when new data arrives

## ⚙️ Configuration

### Basic Configuration

```python
from interpal import InterpalClient

# Default configuration (recommended for most users)
client = InterpalClient(
    username="user",
    password="pass",
    auto_login=True
)
```

### Advanced Configuration

```python
# Configure caching for high-usage applications
client = InterpalClient(
    username="user",
    password="pass",
    auto_login=True,
    max_messages=5000,        # Cache up to 5000 messages (default: 1000)
    cache_users=True,         # Enable user caching (default: True)
    cache_threads=True,       # Enable thread caching (default: True)
    weak_references=True      # Use weak references for memory efficiency (default: True)
)
```

### Configuration Options

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `max_messages` | `int` | `1000` | Maximum number of messages to cache |
| `cache_users` | `bool` | `True` | Enable user and profile caching |
| `cache_threads` | `bool` | `True` | Enable message thread caching |
| `weak_references` | `bool` | `True` | Use weak references for memory efficiency |

## 📊 Monitoring Cache Performance

### Get Cache Statistics

```python
# Get comprehensive cache statistics
stats = client.get_cache_stats()

print(f"Cache hit rate: {stats['hit_rate']:.2%}")
print(f"Cache hits: {stats['cache_hits']}")
print(f"Cache misses: {stats['cache_misses']}")
print(f"Objects created: {stats['objects_created']}")
print(f"Objects updated: {stats['objects_updated']}")
print(f"Cache evictions: {stats['evictions']}")

# Cache sizes by type
sizes = stats['cache_sizes']
print(f"Users cached: {sizes['users']}")
print(f"Messages cached: {sizes['messages']}")
print(f"Threads cached: {sizes['threads']}")
```

### Performance Monitoring

```python
import time

def monitor_cache_performance():
    """Monitor cache performance and provide recommendations."""
    stats = client.get_cache_stats()

    # Hit rate analysis
    hit_rate = stats['hit_rate']
    if hit_rate < 0.3:
        print("⚠️  Low cache hit rate (<30%). Consider:")
        print("   - Increasing cache size")
        print("   - Checking if your access patterns are cache-friendly")
    elif hit_rate > 0.8:
        print("✅ Excellent cache hit rate (>80%)")

    # Eviction analysis
    evictions = stats['evictions']
    if evictions > 100:
        print("⚠️  High number of cache evictions. Consider:")
        print("   - Increasing max_messages")
        print("   - Implementing periodic cache cleanup")

    # Memory usage analysis
    total_objects = (stats['cache_sizes']['users'] +
                   stats['cache_sizes']['messages'] +
                   stats['cache_sizes']['threads'])

    if total_objects > 10000:
        print("⚠️  Large number of cached objects. Monitor memory usage.")

    return stats

# Run periodic monitoring
def periodic_monitoring():
    while True:
        stats = monitor_cache_performance()
        time.sleep(300)  # Check every 5 minutes
```

## 🔧 Cache Management

### Accessing Cached Objects

```python
# Check if a user is cached
user = client.get_cached_user("123456")
if user:
    print(f"User from cache: {user.name}")
else:
    print("User not cached, fetching from API...")
    user = client.user.get_user("123456")

# Check if a message is cached
message = client.get_cached_message("msg789")
if message:
    print(f"Message from cache: {message.content}")
```

### Manual Cache Management

```python
# Clear specific caches
client.clear_user_cache()      # Clear only user cache
client.clear_message_cache()   # Clear only message cache
client.clear_caches()          # Clear all caches

# Reset cache statistics
client.state.reset_stats()

# Update cache configuration at runtime
client.state.update_config(
    max_messages=2000,
    cache_users=False  # Disable user caching
)
```

### Cache Cleanup Strategies

```python
def cleanup_strategy_for_bots():
    """Cache cleanup strategy for long-running bots."""
    stats = client.get_cache_stats()

    # Clear message cache if it gets too large
    if stats['cache_sizes']['messages'] > 2000:
        client.clear_message_cache()
        print("✅ Cleared message cache (too large)")

    # Clear user cache if hit rate is very low
    if stats['hit_rate'] < 0.1:
        client.clear_user_cache()
        print("✅ Cleared user cache (low hit rate)")

def cleanup_strategy_for_memory_constrained():
    """Cache cleanup strategy for memory-constrained environments."""
    # Keep only user profiles, clear everything else
    client.clear_message_cache()
    client.state.clear_media_cache()

    # Reduce cache size
    client.state.update_config(max_messages=500)
    print("✅ Optimized for memory usage")
```

## 🚀 Performance Optimization

### For High-Traffic Bots

```python
# Configuration for high-traffic bots
client = InterpalClient(
    username="bot_user",
    password="bot_pass",
    max_messages=10000,       # Large cache for active bots
    cache_users=True,         # Always cache users
    cache_threads=True,       # Cache threads for context
    weak_references=False     # Keep objects for bot state
)

# Preload frequently accessed data
async def preload_data():
    """Preload frequently accessed data."""
    # Preload recent threads
    threads = await client.get_threads()
    print(f"Preloaded {len(threads)} threads")

    # Preload user data for thread participants
    users = set()
    for thread in threads:
        users.update(thread.participants)

    print(f"Preloaded {len(users)} unique users")
```

### For Memory-Constrained Applications

```python
# Configuration for memory-constrained applications
client = InterpalClient(
    username="user",
    password="pass",
    max_messages=200,         # Small cache
    cache_users=True,         # Keep users for identity
    cache_threads=False,      # Don't cache threads
    weak_references=True      # Use weak references
)

def memory_monitoring_loop():
    """Monitor memory usage and clean up if needed."""
    import psutil
    import gc

    process = psutil.Process()
    memory_percent = process.memory_percent()

    if memory_percent > 80:  # If using >80% of available memory
        print("⚠️  High memory usage detected, clearing caches...")
        client.clear_caches()
        gc.collect()  # Force garbage collection

        # Reduce cache size further
        client.state.update_config(max_messages=100)
```

## 🔍 Debugging State Management

### Enable Debug Mode

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Enable state debugging
def log_state_activity():
    """Log state activity for debugging."""

    # Add creation handlers to log object creation
    def log_user_creation(user):
        print(f"👤 Created user: {user.id} ({user.name})")

    def log_message_creation(message):
        print(f"💬 Created message: {message.id}")

    client.state.add_creation_handler('user', log_user_creation)
    client.state.add_creation_handler('message', log_message_creation)

log_state_activity()
```

### Inspect Internal State

```python
def inspect_state():
    """Inspect internal state for debugging."""
    print("=== State Inspection ===")

    # Direct access to internal caches
    print(f"Users in weak cache: {len(client.state._users)}")
    print(f"Messages in LRU cache: {len(client.state._messages)}")
    print(f"Threads in weak cache: {len(client.state._threads)}")

    # Check LRU order for messages
    if client.state._messages:
        print("Message cache (LRU order):")
        for msg_id, message in list(client.state._messages.items())[:5]:
            print(f"  {msg_id}: {message.content[:50]}...")

    # Statistics
    stats = client.state.get_cache_stats()
    print(f"Cache hit rate: {stats['hit_rate']:.2%}")
    print(f"Total objects created: {stats['objects_created']}")

inspect_state()
```

## 🎯 Best Practices

### 1. Choose the Right Cache Size

```python
# Small applications
client = InterpalClient(max_messages=500)

# Regular usage
client = InterpalClient(max_messages=1000)  # Default

# High-traffic bots
client = InterpalClient(max_messages=5000)

# Enterprise applications
client = InterpalClient(max_messages=10000)
```

### 2. Monitor Performance

```python
# Regular performance monitoring
def setup_monitoring():
    """Set up periodic performance monitoring."""
    import threading
    import time

    def monitor():
        while True:
            stats = client.get_cache_stats()
            if stats['hit_rate'] < 0.5:
                print("⚠️  Low cache hit rate detected")
            time.sleep(300)  # Every 5 minutes

    thread = threading.Thread(target=monitor, daemon=True)
    thread.start()

setup_monitoring()
```

### 3. Graceful Cache Management

```python
# Implement graceful cache management
class CacheManager:
    def __init__(self, client):
        self.client = client
        self.last_cleanup = time.time()

    def periodic_cleanup(self):
        """Perform periodic cache cleanup."""
        if time.time() - self.last_cleanup > 3600:  # Every hour
            stats = self.client.get_cache_stats()

            # Clear old messages if cache is getting full
            if stats['cache_sizes']['messages'] > 800:
                self.client.clear_message_cache()
                print("🧹 Cleaned up old messages")

            self.last_cleanup = time.time()

cache_manager = CacheManager(client)
```

### 4. Error Handling

```python
# Handle cache-related errors gracefully
try:
    # Normal operations
    user = client.get_cached_user("123456")
    if user:
        print(f"User: {user.name}")
    else:
        user = client.user.get_user("123456")
        print(f"Fetched user: {user.name}")

except Exception as e:
    print(f"Cache operation failed: {e}")
    # Fallback to API call
    user = client.user.get_user("123456")
```

## 🔜 Advanced Features

### Cache Hooks and Events

```python
# Add custom cache event handlers
def on_user_created(user):
    """Called when a new user is created."""
    print(f"👤 New user cached: {user.name}")

def on_cache_eviction(cache_type, object_id):
    """Called when an object is evicted from cache."""
    print(f"🗑️  Evicted {cache_type}: {object_id}")

# Register handlers (future feature)
client.state.add_creation_handler('user', on_user_created)
client.state.add_cache_handler('eviction', on_cache_eviction)
```

### Custom Cache Strategies

```python
# Implement custom cache strategies
class SmartCacheStrategy:
    def __init__(self, client):
        self.client = client
        self.user_activity = {}  # Track user activity

    def mark_user_active(self, user_id):
        """Mark a user as recently active."""
        self.user_activity[user_id] = time.time()

    def cleanup_inactive_users(self, inactive_hours=24):
        """Remove users inactive for specified hours."""
        cutoff_time = time.time() - (inactive_hours * 3600)

        inactive_users = [
            user_id for user_id, last_seen in self.user_activity.items()
            if last_seen < cutoff_time
        ]

        for user_id in inactive_users:
            # Remove from weak cache (they'll be garbage collected)
            if user_id in self.client.state._users:
                del self.client.state._users[user_id]
                del self.user_activity[user_id]

        print(f"🧹 Cleaned up {len(inactive_users)} inactive users")

smart_cache = SmartCacheStrategy(client)
```

---

## 📚 Additional Resources

- [API Reference](API_REFERENCE.md) - Complete API documentation
- [Quick Start Guide](QUICKSTART.md) - Get up and running quickly
- [Migration Guide](MIGRATION_GUIDE.md) - Upgrade from v1.x to v2.0.0
- [Performance Tuning](PERFORMANCE.md) - Advanced performance optimization
- [Examples](../examples/) - Complete code examples

## ❓ Troubleshooting

### Common Issues

**Q: My cache hit rate is very low (<20%)**
A: Your access pattern might not be cache-friendly. Consider increasing cache size or checking if you're accessing unique objects each time.

**Q: Memory usage is too high**
A: Reduce `max_messages`, enable `weak_references=True`, or implement periodic cache cleanup.

**Q: Objects aren't being cached**
A: Check that `cache_users` and `cache_threads` are enabled. Some objects might not be cached if they're temporary or have no ID.

**Q: Same user appears as different objects**
A: This shouldn't happen with v2.0+. If it does, check if you're creating multiple client instances.

### Getting Help

- 📖 [Documentation](../README.md)
- 🐛 [Issue Tracker](https://github.com/yourusername/interpal-python-lib/issues)
- 💬 [Discussions](https://github.com/yourusername/interpal-python-lib/discussions)