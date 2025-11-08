"""
Example of using the Interpal Bot extension with commands and state management.

This demonstrates a Discord.py-style bot with command decorators and v2.0.0
state management features for optimal performance and caching.
"""

import asyncio
from interpal.ext.commands import Bot

# Create bot with command prefix and state management configuration
bot = Bot(
    command_prefix='!',  # Can also be ['!', '?'] for multiple prefixes
    description='My Interpal Bot',
    session_cookie='your_session_cookie_here',  # Or use username/password
    # username='your_username',
    # password='your_password',
    persist_session=True,

    # v2.0.0 state management configuration
    max_messages=5000,        # Large cache for bot performance
    cache_users=True,         # Always cache users for bot state
    cache_threads=True,       # Cache threads for message context
    weak_references=False     # Keep objects for long-running bot
)


# Event handlers
@bot.event
async def on_ready():
    """Called when bot is connected and ready."""
    print("🤖 Bot is ready!")
    profile = await bot.get_self()
    print(f"   Logged in as: {profile.name}")

    # Display cache statistics (v2.0.0 feature)
    stats = bot.get_cache_stats()
    print(f"   Cache initialized: {stats['cache_sizes']['users']} users, {stats['cache_sizes']['threads']} threads")


@bot.event
async def on_message(data):
    """
    This is called for ALL messages (before command processing).
    You can add custom logic here for non-command messages.
    """
    # Note: Command processing happens automatically after this
    pass


# Basic command
@bot.command()
async def hello(ctx, name=None):
    """Say hello to someone"""
    if name:
        await ctx.send(f"Hello {name}! 👋")
    else:
        await ctx.send(f"Hello {ctx.sender_name}! 👋")


# Command with multiple parameters
@bot.command(aliases=['add', 'sum'])
async def calculate(ctx, num1: int, num2: int):
    """Add two numbers together"""
    result = num1 + num2
    await ctx.send(f"The result is: {result}")


# Command with optional parameters
@bot.command()
async def greet(ctx, greeting="Hello", name=None):
    """Greet someone with a custom greeting"""
    target = name or ctx.sender_name
    await ctx.send(f"{greeting} {target}!")


# Info command
@bot.command()
async def info(ctx):
    """Get information about the bot"""
    profile = await bot.get_self()
    info_text = f"""
**Bot Information:**
Name: {profile.name}
Location: {getattr(profile, 'city', 'Unknown')}, {getattr(profile, 'country', 'Unknown')}
Age: {getattr(profile, 'age', 'Unknown')}

Use !help to see all available commands!
    """
    await ctx.send(info_text.strip())


# Time command
@bot.command(aliases=['clock'])
async def time(ctx):
    """Get the current time"""
    from datetime import datetime
    current_time = datetime.now().strftime("%H:%M:%S")
    current_date = datetime.now().strftime("%B %d, %Y")
    await ctx.send(f"⏰ Current time: {current_time}\n📅 Date: {current_date}")


# Echo command
@bot.command()
async def echo(ctx, *args):
    """Repeat what you say"""
    message = ' '.join(args) if args else "You didn't say anything!"
    await ctx.send(message)


# Stats command
@bot.command()
async def stats(ctx):
    """Show bot statistics including cache performance"""
    threads = await bot.get_threads()
    notifications = await bot.get_notifications()

    # Get cache statistics (v2.0.0 feature)
    cache_stats = bot.get_cache_stats()

    stats_text = f"""
**Bot Statistics:**
📬 Message Threads: {len(threads)}
🔔 Notifications: {len(notifications)}
⚡ Commands Available: {len([cmd for name, cmd in bot._commands.items() if cmd.name == name])}

**Cache Performance (v2.0.0):**
🧠 Cache Hit Rate: {cache_stats['hit_rate']:.1%}
👤 Users Cached: {cache_stats['cache_sizes']['users']}
💬 Messages Cached: {cache_stats['cache_sizes']['messages']}
🧵 Threads Cached: {cache_stats['cache_sizes']['threads']}
📊 Objects Created: {cache_stats['objects_created']}
🗑️ Cache Evictions: {cache_stats['evictions']}
    """
    await ctx.send(stats_text.strip())


# Search command
@bot.command()
async def search(ctx, country=None, age_min: int = None, age_max: int = None):
    """Search for users by country and age range (with caching)"""
    if not country:
        await ctx.send("Please specify a country! Usage: !search <country> [age_min] [age_max]")
        return

    await ctx.send(f"🔍 Searching for users in {country}...")

    search_params = {'country': country}
    if age_min:
        search_params['age_min'] = age_min
    if age_max:
        search_params['age_max'] = age_max

    try:
        users = await bot.search_users(**search_params)

        # Show cache performance (v2.0.0 feature)
        cache_stats = bot.get_cache_stats()

        if users:
            result = f"🔍 Found {len(users)} users in {country}:\n\n"

            # Check if users were cached (v2.0.0 feature)
            cached_users = 0
            for user in users[:5]:
                cached_user = bot.get_cached_user(user.id)
                if cached_user and cached_user is user:
                    cached_users += 1
                    result += f"• 🧠 {user.name}, {user.age} - {user.city} (cached)\n"
                else:
                    result += f"• 📡 {user.name}, {user.age} - {user.city} (new)\n"

            if len(users) > 5:
                result += f"\n...and {len(users) - 5} more!"

            # Add cache performance info
            result += f"\n\n📊 Cache Performance: {cache_stats['hit_rate']:.1%} hit rate"

        else:
            result = f"No users found in {country}"

        await ctx.send(result)
    except Exception as e:
        await ctx.send(f"Search failed: {str(e)}")


# Cache management command
@bot.command(aliases=['cache', 'clear'])
async def manage_cache(ctx, action=None):
    """Manage bot cache (usage: !cache [clear|stats|users|messages|all])"""
    if not action:
        await ctx.send("Usage: !cache [clear|stats|users|messages|all]")
        return

    action = action.lower()

    if action == "stats":
        cache_stats = bot.get_cache_stats()
        cache_text = f"""
**Cache Statistics:**
🧠 Hit Rate: {cache_stats['hit_rate']:.1%}
📊 Objects Created: {cache_stats['objects_created']}
🔄 Objects Updated: {cache_stats['objects_updated']}
🗑️ Evictions: {cache_stats['evictions']}

**Cache Sizes:**
👤 Users: {cache_stats['cache_sizes']['users']}
💬 Messages: {cache_stats['cache_sizes']['messages']}
🧵 Threads: {cache_stats['cache_sizes']['threads']}
        """
        await ctx.send(cache_text.strip())

    elif action == "clear":
        bot.clear_caches()
        await ctx.send("🧹 All caches cleared!")

    elif action == "users":
        bot.clear_user_cache()
        await ctx.send("🧹 User cache cleared!")

    elif action == "messages":
        bot.clear_message_cache()
        await ctx.send("🧹 Message cache cleared!")

    elif action == "all":
        bot.clear_caches()
        bot.state.reset_stats()  # Reset statistics too
        await ctx.send("🧹 All caches cleared and statistics reset!")

    else:
        await ctx.send("Unknown action. Use: clear, stats, users, messages, or all")


# Performance monitoring command
@bot.command(aliases=['monitor', 'perf'])
async def monitor_performance(ctx):
    """Monitor bot performance and cache efficiency"""
    cache_stats = bot.get_cache_stats()

    # Performance analysis
    hit_rate = cache_stats['hit_rate']
    evictions = cache_stats['evictions']
    objects_created = cache_stats['objects_created']

    # Determine performance level
    if hit_rate >= 0.8:
        performance_emoji = "🚀"
        performance_level = "Excellent"
    elif hit_rate >= 0.6:
        performance_emoji = "✅"
        performance_level = "Good"
    elif hit_rate >= 0.4:
        performance_emoji = "⚠️"
        performance_level = "Fair"
    else:
        performance_emoji = "❌"
        performance_level = "Poor"

    perf_text = f"""
{performance_emoji} **Bot Performance Report**

**Cache Performance:**
🧠 Hit Rate: {hit_rate:.1%} ({performance_level})
📊 Objects Created: {objects_created}
🗑️ Cache Evictions: {evictions}
🔄 Objects Updated: {cache_stats['objects_updated']}

**Cache Sizes:**
👤 Users: {cache_stats['cache_sizes']['users']}
💬 Messages: {cache_stats['cache_sizes']['messages']}
🧵 Threads: {cache_stats['cache_sizes']['threads']}

**Recommendations:**
"""

    # Add recommendations based on performance
    recommendations = []

    if hit_rate < 0.5:
        recommendations.append("• Consider increasing cache size (low hit rate)")

    if evictions > 100:
        recommendations.append("• Cache is too small (many evictions)")

    if cache_stats['cache_sizes']['messages'] > 4000:
        recommendations.append("• Consider clearing message cache periodically")

    if hit_rate >= 0.8:
        recommendations.append("• Performance is optimal!")

    if not recommendations:
        recommendations.append("• Performance looks good!")

    perf_text += "\n".join(recommendations[:3])  # Limit to 3 recommendations

    await ctx.send(perf_text.strip())


# Admin command (example of checking permissions)
@bot.command(hidden=True)  # Hidden from help
async def shutdown(ctx):
    """Shutdown the bot (admin only)"""
    # You could check if sender is admin here
    admin_ids = ['your_user_id_here']  # Add your user ID

    if ctx.sender_id in admin_ids:
        await ctx.send("Shutting down bot... 👋")
        await bot.close()
        exit(0)
    else:
        await ctx.send("You don't have permission to use this command!")


# Error handler (override default)
@bot.event
async def on_command_error(ctx, error):
    """Custom error handler for commands"""
    error_msg = str(error)
    
    if "Missing required argument" in error_msg:
        await ctx.send(f"❌ Missing argument! Use `!help {ctx.command.name}` for usage info.")
    elif "invalid literal" in error_msg:
        await ctx.send(f"❌ Invalid argument type! Use `!help {ctx.command.name}` for usage info.")
    else:
        await ctx.send(f"❌ Error: {error_msg}")
    
    # Print to console for debugging
    print(f"Command error in {ctx.command.name}: {error}")


def main():
    """Run the bot with state management features."""
    print("=" * 70)
    print("Starting Interpal Bot with Commands Extension & State Management (v2.0.0)")
    print("=" * 70)

    print("🚀 New v2.0.0 Features:")
    print("   • Smart caching with memory efficiency")
    print("   • Object identity - same objects reused throughout session")
    print("   • Performance monitoring and cache statistics")
    print("   • Configurable cache sizes and management")
    print()
    print("📋 Available Commands:")
    print("   • !stats - Show bot statistics with cache performance")
    print("   • !cache [action] - Manage cache (clear, stats, users, messages, all)")
    print("   • !monitor - Performance monitoring and recommendations")
    print("   • !search <country> - Search users with caching info")
    print()
    print("💡 Try these commands to see state management in action!")
    print()

    # If using username/password instead of session cookie
    if not bot.is_authenticated:
        print("\n⚠️  Please set your session_cookie or username/password in the code!")
        print("   Edit this file and add your credentials.\n")
        return

    # Start the bot (this will run indefinitely)
    bot.run()


if __name__ == "__main__":
    main()

