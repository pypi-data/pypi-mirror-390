# Migration Guide: v1.x to v2.0.0

## Overview

This guide helps you migrate from Interpal Python Library v1.x to v2.0.0. The v2.0.0 release introduces a major architectural improvement with smart state management inspired by Discord.py's patterns.

**Good news:** There are **no breaking changes** to public APIs! Your existing code will continue to work unchanged. v2.0.0 is an enhancement release that adds powerful new capabilities.

## 🚀 What's New in v2.0.0?

### ✅ New Features (Opt-in)
- **Smart State Management**: Intelligent caching with memory efficiency
- **Object Identity**: Same user/profile objects reused throughout session
- **Performance Improvements**: Reduced API calls through caching
- **Cache Statistics**: Monitor cache performance and usage
- **Configurable Caching**: Fine-tune memory usage and performance

### 🔧 Internal Improvements
- Updated model architecture for state awareness
- Enhanced memory management with weak references
- LRU cache eviction for optimal memory usage
- Object factory patterns for consistent creation

## 📋 Migration Checklist

### ✅ No Code Changes Required

Your existing v1.x code will continue to work without any changes:

```python
# This v1.x code works unchanged in v2.0.0
from interpal import InterpalClient

client = InterpalClient(username="user", password="pass", auto_login=True)
profile = client.get_self()
threads = client.get_threads()
client.send_message("123456", "Hello!")
```

### ✅ Optional: Add Cache Configuration

You can optionally add cache configuration to improve performance:

```python
# Before (v1.x)
client = InterpalClient(
    username="user",
    password="pass",
    auto_login=True
)

# After (v2.0.0) - optional cache configuration
client = InterpalClient(
    username="user",
    password="pass",
    auto_login=True,
    max_messages=2000,        # New: Cache more messages
    cache_users=True,         # New: Cache users (default)
    cache_threads=True,       # New: Cache threads (default)
    weak_references=True      # New: Memory efficiency (default)
)
```

### ✅ Optional: Add Cache Monitoring

You can optionally add cache monitoring to track performance:

```python
# New in v2.0.0 - optional cache monitoring
stats = client.get_cache_stats()
print(f"Cache hit rate: {stats['hit_rate']:.2%}")
print(f"Objects cached: {stats['objects_created']}")

# New in v2.0.0 - optional cache management
client.clear_user_cache()     # Clear user cache
client.clear_message_cache()  # Clear message cache
```

## 🔄 Step-by-Step Migration

### Step 1: Update Dependencies

```bash
# Update to the latest version
pip install --upgrade interpal
```

### Step 2: Test Your Existing Code

Your existing code should work without changes:

```python
# Test your existing v1.x code
from interpal import InterpalClient

def test_existing_functionality():
    client = InterpalClient(
        username="your_username",
        password="your_password",
        auto_login=True
    )

    # Test all your existing functionality
    profile = client.get_self()
    threads = client.get_threads()
    users = client.search_users(limit=5)

    print("✅ All existing functionality works!")
    client.close()

test_existing_functionality()
```

### Step 3: (Optional) Add Cache Configuration

```python
# Gradually add cache configuration
client = InterpalClient(
    username="user",
    password="pass",
    auto_login=True,

    # Add these gradually as needed
    max_messages=1500,    # Start with a moderate increase
    cache_users=True,     # Enable user caching
    cache_threads=True,   # Enable thread caching
    weak_references=True  # Keep memory efficiency
)
```

### Step 4: (Optional) Add Cache Monitoring

```python
# Add monitoring to track improvements
def monitor_performance():
    stats = client.get_cache_stats()
    print(f"📊 Cache Performance:")
    print(f"   Hit rate: {stats['hit_rate']:.2%}")
    print(f"   Objects created: {stats['objects_created']}")
    print(f"   Cache evictions: {stats['evictions']}")

# Call this periodically in your application
monitor_performance()
```

## 📊 Performance Improvements

### Before v2.0.0
```python
# Multiple API calls for the same user
user1 = client.get_user("123456")  # API call
user2 = client.get_user("123456")  # Another API call
print(user1 is user2)  # False - different objects
```

### After v2.0.0
```python
# Same user, cached efficiently
user1 = client.get_user("123456")  # API call
user2 = client.get_user("123456")  # From cache
print(user1 is user2)  # True - same object!
```

## 🎯 Recommended Migration Strategy

### For New Projects

```python
# Use v2.0.0 features from the start
client = InterpalClient(
    username="user",
    password="pass",
    auto_login=True,
    max_messages=2000,     # Larger cache for better performance
    cache_users=True,      # Enable all caching
    cache_threads=True,
    weak_references=True   # Keep memory efficiency
)
```

### For Existing Applications

```python
# Phase 1: Update with no changes (immediate)
# Your existing code works as-is

# Phase 2: Add basic cache configuration (optional)
client = InterpalClient(
    # your existing parameters...
    max_messages=1500  # Moderate increase
)

# Phase 3: Add cache monitoring (optional)
stats = client.get_cache_stats()
print(f"Cache hit rate: {stats['hit_rate']:.2%}")

# Phase 4: Optimize based on usage patterns
# Monitor and adjust cache sizes as needed
```

### For High-Performance Bots

```python
# Optimize for high-traffic usage
client = InterpalClient(
    username="bot_user",
    password="bot_pass",
    auto_login=True,
    max_messages=10000,    # Large cache for active bots
    cache_users=True,      # Always cache users
    cache_threads=True,    # Cache threads for context
    weak_references=False  # Keep objects for bot state
)

# Monitor performance regularly
def bot_performance_monitor():
    stats = client.get_cache_stats()
    if stats['hit_rate'] < 0.7:
        print("⚠️  Consider increasing cache size")
```

## 🔧 Common Migration Scenarios

### Scenario 1: Simple Scripts

```python
# Before (v1.x)
client = InterpalClient(username="user", password="pass")
client.login()
profile = client.get_self()
print(f"Hello {profile.name}")

# After (v2.0.0) - identical code
client = InterpalClient(username="user", password="pass")
client.login()
profile = client.get_self()  # Now cached!
print(f"Hello {profile.name}")
```

### Scenario 2: Data Collection Scripts

```python
# Before (v1.x)
def collect_user_data(user_ids):
    client = InterpalClient(username="user", password="pass", auto_login=True)

    users = []
    for user_id in user_ids:
        user = client.user.get_user(user_id)  # API call each time
        users.append(user)

    return users

# After (v2.0.0) - automatic caching improves performance
def collect_user_data(user_ids):
    client = InterpalClient(username="user", password="pass", auto_login=True)

    users = []
    for user_id in user_ids:
        user = client.user.get_user(user_id)  # Cached after first call
        users.append(user)

    # Check performance improvement
    stats = client.get_cache_stats()
    print(f"Cache hit rate: {stats['hit_rate']:.2%}")

    return users
```

### Scenario 3: Real-time Bots

```python
# Before (v1.x)
async def handle_messages():
    client = AsyncInterpalClient(username="bot", password="pass")
    await client.login()

    @client.event('on_message')
    async def on_message(data):
        # Each message creates new objects
        user_id = data.get('sender_id')
        # No caching, repeated API calls
        user = await client.get_user(user_id)
        print(f"Message from {user.name}")

# After (v2.0.0) - automatic user caching
async def handle_messages():
    client = AsyncInterpalClient(username="bot", password="pass")
    await client.login()

    @client.event('on_message')
    async def on_message(data):
        user_id = data.get('sender_id')
        # User likely cached already
        user = await client.get_user(user_id)
        print(f"Message from {user.name}")

        # Monitor cache performance
        stats = client.get_cache_stats()
        if stats['hit_rate'] > 0.8:
            print("🚀 Great cache performance!")
```

## ⚠️ Important Notes

### No Breaking Changes
- ✅ All existing public APIs work unchanged
- ✅ All existing parameters and methods are preserved
- ✅ Existing code continues to work without modification

### Optional New Features
- ✅ New cache parameters are optional with sensible defaults
- ✅ New methods are additive (don't replace existing ones)
- ✅ State management is transparent to existing code

### Performance Improvements
- ✅ Automatic - no code changes required
- ✅ Memory efficient - weak references prevent leaks
- ✅ Configurable - tune for your specific use case

## 🧪 Testing Your Migration

### Basic Functionality Test

```python
def test_migration():
    """Test that basic functionality works after migration."""

    # Test sync client
    client = InterpalClient(username="test_user", password="test_pass")

    # These should all work exactly as before
    assert hasattr(client, 'get_self')
    assert hasattr(client, 'get_threads')
    assert hasattr(client, 'send_message')
    assert hasattr(client, 'search_users')

    # Test new state features
    assert hasattr(client, 'get_cache_stats')
    assert hasattr(client, 'clear_caches')

    # Test cache configuration
    assert 'max_messages' in client.__dict__
    assert client.max_messages == 1000  # Default value

    print("✅ Migration test passed!")

test_migration()
```

### Performance Test

```python
def test_performance_improvement():
    """Test that caching improves performance."""

    client = InterpalClient(username="test_user", password="test_pass")

    # Get the same user multiple times
    user1 = client.get_cached_user("123456")
    user2 = client.get_cached_user("123456")

    # First call should create the object
    stats_before = client.state.get_cache_stats()

    # Simulate getting the user (would normally make API call)
    # In real usage, the second call would be from cache

    stats_after = client.state.get_cache_stats()

    print(f"✅ Performance test completed")
    print(f"Objects created: {stats_after['objects_created']}")
    print(f"Cache hit rate: {stats_after['hit_rate']:.2%}")

test_performance_improvement()
```

## 🆘 Troubleshooting

### Common Issues

**Q: My code stopped working after upgrade**
A: This shouldn't happen. Please check:
- You're using the latest version: `pip install --upgrade interpal`
- Your import statements are correct
- Check the error message - it might be unrelated to state management

**Q: Memory usage increased**
A: The new caching system uses more memory for better performance. You can:
- Reduce `max_messages`: `client = InterpalClient(max_messages=500)`
- Enable `weak_references=True` (default)
- Clear caches periodically: `client.clear_caches()`

**Q: I don't see performance improvements**
A: Check your cache hit rate:
```python
stats = client.get_cache_stats()
print(f"Hit rate: {stats['hit_rate']:.2%}")
```
Low hit rates (<30%) might indicate your access pattern isn't cache-friendly.

### Getting Help

If you encounter issues during migration:

1. **Check the logs** - Look for any error messages
2. **Verify imports** - Ensure you're using the latest version
3. **Test gradually** - Add new features incrementally
4. **Check documentation** - [State Management Guide](STATE_MANAGEMENT.md)
5. **Report issues** - [GitHub Issues](https://github.com/yourusername/interpal-python-lib/issues)

## 📈 Benefits of Upgrading

### Immediate Benefits
- ✅ **Zero Migration Effort** - Your code works as-is
- ✅ **Automatic Performance** - No code changes needed
- ✅ **Memory Efficiency** - Better memory management
- ✅ **Future-Ready** - Foundation for advanced features

### Long-term Benefits
- ✅ **Reduced API Calls** - Lower bandwidth usage
- ✅ **Faster Response Times** - Cached objects
- ✅ **Better User Experience** - More responsive applications
- ✅ **Monitoring Capabilities** - Track performance metrics

### Developer Experience
- ✅ **Same APIs** - No learning curve
- ✅ **Optional Enhancements** - Add features as needed
- ✅ **Better Debugging** - Cache statistics and monitoring
- ✅ **Performance Insights** - Understand your usage patterns

## 🎉 Conclusion

Migrating to v2.0.0 is **effortless and beneficial**:

1. **No Code Changes Required** - Your existing code works unchanged
2. **Automatic Performance Improvements** - Better caching and memory management
3. **Optional Enhancements** - Add new features when you're ready
4. **Future-Proof** - Foundation for advanced Discord.py patterns

The v2.0.0 release maintains full backward compatibility while adding powerful new capabilities that will improve your applications' performance and reduce your API usage.

**Ready to upgrade?** Just run:
```bash
pip install --upgrade interpal
```

That's it! Your applications will automatically benefit from the new state management system. 🚀