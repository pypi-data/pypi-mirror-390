# Command Framework Updates - Event Model Integration

## Overview

The command framework (`interpal.ext.commands`) has been updated to seamlessly integrate with the new structured WebSocket event models. This brings type safety, better autocomplete support, and easier access to message data.

## What's New

### 1. Context Now Includes Full Event Data

The `Context` object now automatically extracts data from `ThreadNewMessageEvent` objects:

**Before:**
```python
@bot.command()
async def hello(ctx):
    # Limited access to sender info
    name = ctx.sender_name  # Just a string
    # No access to age, country, online status, etc.
```

**After:**
```python
@bot.command()
async def hello(ctx: Context):
    # Full User object with all information!
    name = ctx.sender.name
    age = ctx.sender.age
    country = ctx.sender.country_code
    is_online = ctx.sender.is_online
    avatar = ctx.sender.avatar_url
```

### 2. New Context Attributes

The `Context` class now includes:

| Attribute | Type | Description |
|-----------|------|-------------|
| `event` | `ThreadNewMessageEvent \| None` | The full event object (if available) |
| `sender` | `User \| Dict` | Full User object or dict |
| `sender_id` | `str` | User ID |
| `sender_name` | `str` | User name |
| `thread_id` | `str` | Thread ID |
| `content` | `str` | Message content |
| `counters` | `EventCounters \| None` | Live counters (messages, notifications, etc.) |
| `click_url` | `str \| None` | Direct URL to conversation |

### 3. New Context Methods

#### `ctx.has_event` (property)
Check if the context has a full event model:
```python
@bot.command()
async def info(ctx):
    if ctx.has_event:
        await ctx.send(f"You're {ctx.sender.age} years old!")
    else:
        await ctx.send("Event model not available")
```

#### `ctx.author` (property)
Discord.py compatibility - alias for `ctx.sender`:
```python
@bot.command()
async def greet(ctx):
    await ctx.send(f"Hello {ctx.author.name}!")
```

#### `ctx.get_sender_avatar(size)`
Get sender's avatar URL by size:
```python
@bot.command()
async def avatar(ctx):
    small = ctx.get_sender_avatar('small')
    medium = ctx.get_sender_avatar('medium')
    large = ctx.get_sender_avatar('large')
    full = ctx.get_sender_avatar('url')
```

### 4. Event Handlers Receive Structured Models

Event handlers registered with `@bot.event` now receive typed event objects:

```python
@bot.event
async def on_message(event: ThreadNewMessageEvent):
    """
    Receives a ThreadNewMessageEvent instead of a dict!
    """
    print(f"From: {event.sender.name}")
    print(f"Message: {event.message}")
    print(f"Counters: {event.counters.unread_threads}")
    print(f"Link: {event.click_url}")
```

### 5. Automatic Command Processing

The bot automatically processes commands from event models:

```python
# When a user sends: "!hello"
# 1. WebSocket receives ThreadNewMessageEvent
# 2. on_message event fires (your handler, if any)
# 3. Bot extracts command from event
# 4. Creates Context with full event data
# 5. Invokes your command handler
```

## Migration Guide

### No Breaking Changes!

The framework is **fully backward compatible**. Old code continues to work:

```python
# This still works!
@bot.command()
async def old_command(ctx):
    await ctx.send(ctx.sender_name)  # Works as before
```

### Recommended Updates

To take advantage of new features:

1. **Add type hints:**
```python
from interpal.ext.commands import Context
from interpal.models import ThreadNewMessageEvent

@bot.command()
async def mycommand(ctx: Context):  # Add type hint
    # Now you get autocomplete!
```

2. **Access User objects:**
```python
@bot.command()
async def info(ctx: Context):
    if ctx.has_event:
        # Access full User object
        await ctx.send(f"You're from {ctx.sender.country_code}!")
```

3. **Use counters:**
```python
@bot.command()
async def stats(ctx: Context):
    if ctx.counters:
        await ctx.send(f"You have {ctx.counters.unread_threads} unread threads!")
```

## Complete Example

```python
from interpal.ext.commands import Bot, Context
from interpal.models import ThreadNewMessageEvent

bot = Bot(
    command_prefix='!',
    username='your_username',
    password='your_password'
)

@bot.event
async def on_message(event: ThreadNewMessageEvent):
    """Handle all messages with full event data."""
    if not event.message.startswith('!'):
        print(f"Non-command from {event.sender.name}: {event.message}")

@bot.command()
async def profile(ctx: Context):
    """Show user profile using event data."""
    if not ctx.has_event:
        await ctx.send("Event data not available")
        return
    
    info = f"""
    👤 **Your Profile**
    
    Name: {ctx.sender.name}
    Username: @{ctx.sender.username}
    Age: {ctx.sender.age}
    Country: {ctx.sender.country_code}
    Status: {'🟢 Online' if ctx.sender.is_online else '🔴 Offline'}
    
    📊 **Stats**
    Unread: {ctx.counters.unread_threads}
    Messages: {ctx.counters.new_messages}
    """
    
    await ctx.send(info.strip())

bot.run()
```

## Type Safety Benefits

### With Type Hints

Your IDE will provide:
- ✅ Autocomplete for all attributes
- ✅ Type checking
- ✅ Inline documentation
- ✅ Error detection before runtime

```python
@bot.command()
async def typed_command(ctx: Context):
    # IDE knows ctx.sender is a User object
    name = ctx.sender.name  # Autocomplete suggests 'name', 'age', etc.
    age = ctx.sender.age    # IDE knows this is Optional[int]
```

### Without Type Hints

Still works, but no IDE support:
```python
@bot.command()
async def untyped_command(ctx):
    # Works, but no autocomplete
    name = ctx.sender.name
```

## Advanced Features

### Access Raw Event

If you need the raw event data:
```python
@bot.command()
async def debug(ctx: Context):
    if ctx.event:
        raw_data = ctx.event._data
        # Access original dict if needed
```

### Convert to Dict

```python
@bot.command()
async def export(ctx: Context):
    if ctx.event:
        event_dict = ctx.event.to_dict()
        event_json = ctx.event.to_json(indent=2)
```

### Check Event Type

```python
@bot.event
async def on_message(event):
    from interpal.models import ThreadNewMessageEvent
    
    if isinstance(event, ThreadNewMessageEvent):
        # It's a message event
        print(f"Message: {event.message}")
```

## Best Practices

1. **Always add type hints** for better IDE support
2. **Check `ctx.has_event`** before accessing event-specific data
3. **Use `ctx.sender` as User** object when possible
4. **Handle both modes** if supporting older code
5. **Use convenience properties** like `ctx.author`, `ctx.get_sender_avatar()`

## Troubleshooting

### Issue: `ctx.sender.name` AttributeError

**Solution:** Check if event model is available:
```python
@bot.command()
async def safe_command(ctx: Context):
    if ctx.has_event:
        name = ctx.sender.name
    else:
        name = ctx.sender_name  # Fallback
```

### Issue: Counters is None

**Solution:** Counters only available with event model:
```python
@bot.command()
async def counters(ctx: Context):
    if ctx.counters:
        await ctx.send(f"Unread: {ctx.counters.unread_threads}")
    else:
        await ctx.send("Counters not available")
```

### Issue: No autocomplete in IDE

**Solution:** Add type hints:
```python
from interpal.ext.commands import Context

@bot.command()
async def mycommand(ctx: Context):  # Add this type hint!
    # Now you get autocomplete
```

## See Also

- [WEBSOCKET_EVENTS.md](WEBSOCKET_EVENTS.md) - Full WebSocket event model documentation
- [examples/bot_with_event_models.py](../examples/bot_with_event_models.py) - Complete working example
- [examples/simple_bot.py](../simple_bot.py) - Simple bot with new features

## Summary

The command framework now seamlessly integrates with structured event models, providing:
- 🎯 **Type safety** - Full type hints and IDE support
- 📦 **Rich data** - Access to User objects, counters, avatars
- 🔄 **Backward compatible** - Old code still works
- 🚀 **Easy to use** - Automatic extraction of event data
- 💡 **Better DX** - Autocomplete and inline documentation

Update your bots to take advantage of these features for cleaner, safer, and more maintainable code!

