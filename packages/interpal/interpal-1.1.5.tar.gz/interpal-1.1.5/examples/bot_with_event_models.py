"""
Advanced bot example demonstrating the new WebSocket event models.

This example shows how the Bot framework now seamlessly integrates with
structured event models for better type safety and easier data access.
"""

from interpal.ext.commands import Bot, Context
from interpal.models import ThreadNewMessageEvent, ThreadTypingEvent, CounterUpdateEvent


# Create bot
bot = Bot(
    command_prefix='!',
    description='Advanced Event Model Bot',
    username="your_username",
    password="your_password",
    persist_session=True,
    
    # State management for caching
    max_messages=1000,
    cache_users=True,
    cache_threads=True,
)


# ============================================================================
# Event Handlers - Receive structured event models
# ============================================================================

@bot.event
async def on_ready():
    """Bot is ready and connected."""
    print("✅ Bot is ready!")
    profile = await bot.get_self()
    print(f"   Logged in as: {profile.name}")


@bot.event
async def on_message(event: ThreadNewMessageEvent):
    """
    Handle all incoming messages with structured event model.
    
    This runs BEFORE command processing, so you can:
    - Log all messages
    - Filter/moderate content
    - Track statistics
    - Auto-respond to non-commands
    """
    # Skip if it's a command (will be handled by command framework)
    if event.message.startswith(bot.command_prefix[0]):
        return
    
    print(f"\n💬 Message from {event.sender.name}: {event.message}")
    print(f"   Thread: {event.thread_id}")
    print(f"   Unread: {event.counters.unread_threads}")


@bot.event
async def on_typing(event: ThreadTypingEvent):
    """Handle typing indicators."""
    if event.is_typing and event.user:
        print(f"✍️  {event.user.name} is typing...")


@bot.event
async def on_notification(event: CounterUpdateEvent):
    """Handle counter updates."""
    if event.counters.new_notifications > 0:
        print(f"🔔 {event.counters.new_notifications} new notifications")


# ============================================================================
# Commands - Context now includes full event data
# ============================================================================

@bot.command()
async def hello(ctx: Context):
    """Say hello with personalized greeting."""
    # ctx.sender is now a full User object!
    name = ctx.sender.name if ctx.has_event else ctx.sender_name
    age = ctx.sender.age if ctx.has_event else "unknown"
    country = ctx.sender.country_code if ctx.has_event else "unknown"
    
    greeting = f"Hello {name}! 👋\n"
    greeting += f"Age: {age}, Country: {country}\n"
    
    if ctx.has_event:
        greeting += f"You're currently {'🟢 online' if ctx.sender.is_online else '🔴 offline'}"
    
    await ctx.send(greeting)


@bot.command(aliases=['profile', 'me'])
async def whoami(ctx: Context):
    """Show detailed sender information using event models."""
    if not ctx.has_event:
        await ctx.send("⚠️ Event model not available")
        return
    
    sender = ctx.sender
    
    info = f"""
👤 **Profile Information:**

Name: {sender.name}
Username: @{sender.username}
Age: {sender.age}
Country: {sender.country_code}
Birthday: {sender.birthday if sender.birthday else 'Not set'}

Status: {'🟢 Online' if sender.is_online else '🔴 Offline'}
Last Login: {sender.last_login if sender.last_login else 'Unknown'}
Account Status: {sender.status}

📊 **Current Counters:**
Unread Threads: {ctx.counters.unread_threads}
Total Threads: {ctx.counters.total_threads}
New Messages: {ctx.counters.new_messages}
New Notifications: {ctx.counters.new_notifications}
New Views: {ctx.counters.new_views}
    """.strip()
    
    await ctx.send(info)


@bot.command()
async def avatar(ctx: Context):
    """Show your avatar URLs."""
    if not ctx.has_event:
        await ctx.send("⚠️ Event model not available")
        return
    
    # Use the new Context method for getting avatars
    avatar_url = ctx.get_sender_avatar('url')
    avatar_small = ctx.get_sender_avatar('small')
    avatar_medium = ctx.get_sender_avatar('medium')
    avatar_large = ctx.get_sender_avatar('large')
    
    response = f"""
🖼️ **Your Avatars:**

Full Size: {avatar_url or 'Not set'}
Large: {avatar_large or 'Not set'}
Medium: {avatar_medium or 'Not set'}
Small: {avatar_small or 'Not set'}
    """.strip()
    
    await ctx.send(response)


@bot.command()
async def counters(ctx: Context):
    """Show current counter values."""
    if not ctx.has_event or not ctx.counters:
        await ctx.send("⚠️ Counters not available")
        return
    
    c = ctx.counters
    response = f"""
📊 **Live Counters:**

📨 New Messages: {c.new_messages}
💬 Unread Threads: {c.unread_threads}
📬 Total Threads: {c.total_threads}
🔔 New Notifications: {c.new_notifications}
👀 New Profile Views: {c.new_views}
👥 New Friend Requests: {c.new_friend_requests}
    """.strip()
    
    await ctx.send(response)


@bot.command()
async def echo(ctx: Context, message: str = None):
    """
    Echo back a message with sender info.
    
    Usage: !echo <message>
    Example: !echo Hello world, this is a test!
    
    Note: The last string parameter automatically captures all remaining words.
    """
    if not message:
        await ctx.send("Please provide a message to echo!")
        return
    
    sender_name = ctx.sender.name if ctx.has_event else ctx.sender_name
    response = f"🔊 {sender_name} says: {message}"
    
    await ctx.send(response)


@bot.command(aliases=['link'])
async def thread_link(ctx: Context):
    """Get a direct link to this conversation."""
    if ctx.has_event and ctx.click_url:
        await ctx.send(f"🔗 Direct link: https://interpals.net{ctx.click_url}")
    else:
        await ctx.send("⚠️ Link not available")


@bot.command()
async def event_debug(ctx: Context):
    """Debug information about the context and event."""
    debug_info = f"""
🔍 **Debug Information:**

Has Event Model: {ctx.has_event}
Thread ID: {ctx.thread_id}
Sender ID: {ctx.sender_id}
Sender Name: {ctx.sender_name}
Content: {ctx.content}
Command: {ctx.command.name}
Prefix: {ctx.prefix}
Args: {ctx.args}
    """.strip()
    
    if ctx.has_event:
        debug_info += f"""

**Event Data:**
Message ID: {ctx.event.message_id}
Thread ID: {ctx.event.thread_id}
Sender Online: {ctx.event.sender.is_online if ctx.event.sender else 'N/A'}
Click URL: {ctx.event.click_url}
        """
    
    await ctx.send(debug_info)


@bot.command()
async def reply_test(ctx: Context):
    """Test various reply methods."""
    # All these work!
    await ctx.send("✅ Using ctx.send()")
    await ctx.reply("✅ Using ctx.reply()")
    
    # Access bot methods directly
    if ctx.thread_id:
        await bot.send_message(ctx.thread_id, "✅ Using bot.send_message()")


# ============================================================================
# Error Handling
# ============================================================================

@bot.event
async def on_command_error(ctx: Context, error: Exception):
    """Custom error handler."""
    error_msg = f"❌ Error in command '{ctx.command.name}': {str(error)}"
    await ctx.send(error_msg)
    print(f"Command error: {error}")


# ============================================================================
# Run Bot
# ============================================================================

if __name__ == "__main__":
    print("🚀 Starting Advanced Event Model Bot")
    print("=" * 70)
    print("\n📦 Features:")
    print("  • Structured event models (ThreadNewMessageEvent)")
    print("  • Type-safe Context with User objects")
    print("  • Automatic event/command integration")
    print("  • Rich sender information in every command")
    print("  • Avatar URLs and counters in Context")
    print("\n💡 Commands:")
    print("  • !hello - Personalized greeting with your info")
    print("  • !whoami - Full profile details")
    print("  • !avatar - Your avatar URLs")
    print("  • !counters - Live counter values")
    print("  • !thread_link - Get direct link to conversation")
    print("  • !event_debug - Debug event data")
    print("  • !help - See all commands")
    print("=" * 70)
    print()
    
    bot.run()

