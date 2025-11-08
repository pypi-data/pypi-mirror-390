# Bot Extension Guide

The Interpal library includes a powerful command framework extension inspired by discord.py's `commands` module. This makes it easy to create command-based bots with decorators and automatic command parsing.

## Table of Contents

- [Quick Start](#quick-start)
- [Basic Concepts](#basic-concepts)
- [Creating Commands](#creating-commands)
- [Command Context](#command-context)
- [Event Handlers](#event-handlers)
- [Cogs (Command Groups)](#cogs-command-groups)
- [Error Handling](#error-handling)
- [Advanced Features](#advanced-features)

## Quick Start

Here's the simplest possible bot:

```python
from interpal.ext.commands import Bot

bot = Bot(
    command_prefix='!',
    username='your_username',
    password='your_password',
    persist_session=True
)

@bot.command()
async def hello(ctx):
    """Say hello"""
    await ctx.send(f"Hello {ctx.sender_name}!")

@bot.event
async def on_ready():
    print("Bot is ready!")

bot.run()
```

## Basic Concepts

### The Bot Class

The `Bot` class extends `AsyncInterpalClient` with command handling capabilities:

```python
from interpal.ext.commands import Bot

bot = Bot(
    command_prefix='!',           # Can be string or list: ['!', '?']
    description='My Bot',         # Bot description for help
    help_command=True,            # Include default help command
    case_insensitive=True,        # Commands are case insensitive
    username='user',              # Authentication
    password='pass',
    persist_session=True          # Save session for 24 hours
)
```

### Command Prefix

You can use single or multiple prefixes:

```python
# Single prefix
bot = Bot(command_prefix='!')

# Multiple prefixes
bot = Bot(command_prefix=['!', '?', '/'])

# Commands work with any prefix:
# !hello
# ?hello
# /hello
```

## Creating Commands

### Basic Command

```python
@bot.command()
async def ping(ctx):
    """Check if bot is alive"""
    await ctx.send("Pong! 🏓")
```

**Usage:** `!ping`

### Command with Parameters

```python
@bot.command()
async def greet(ctx, name):
    """Greet someone by name"""
    await ctx.send(f"Hello {name}!")
```

**Usage:** `!greet Alice`

### Optional Parameters

```python
@bot.command()
async def hello(ctx, name=None):
    """Say hello"""
    if name:
        await ctx.send(f"Hello {name}!")
    else:
        await ctx.send(f"Hello {ctx.sender_name}!")
```

**Usage:** `!hello` or `!hello Alice`

### Multiple Parameters

```python
@bot.command()
async def calculate(ctx, num1: int, num2: int):
    """Add two numbers"""
    result = num1 + num2
    await ctx.send(f"Result: {result}")
```

**Usage:** `!calculate 5 10`

### Variable Arguments

```python
@bot.command()
async def echo(ctx, *words):
    """Repeat what you say"""
    message = ' '.join(words)
    await ctx.send(message)
```

**Usage:** `!echo Hello world from bot`

### Command Aliases

```python
@bot.command(aliases=['add', 'sum'])
async def calculate(ctx, num1: int, num2: int):
    """Add two numbers"""
    await ctx.send(f"Result: {num1 + num2}")
```

**Usage:** `!calculate 5 10` or `!add 5 10` or `!sum 5 10`

### Custom Command Name

```python
@bot.command(name='info')
async def bot_info(ctx):
    """Get bot information"""
    await ctx.send("I am a helpful bot!")
```

**Usage:** `!info` (not `!bot_info`)

### Hidden Commands

```python
@bot.command(hidden=True)
async def secret(ctx):
    """This won't show in help"""
    await ctx.send("You found the secret command!")
```

## Command Context

Every command receives a `Context` object (`ctx`) with useful information:

```python
@bot.command()
async def info(ctx):
    # Message information
    print(ctx.content)         # Full message content
    print(ctx.thread_id)       # Thread ID
    
    # Sender information
    print(ctx.sender_name)     # Sender's name
    print(ctx.sender_id)       # Sender's user ID
    print(ctx.sender)          # Full sender dict
    
    # Command information
    print(ctx.command.name)    # Command name
    print(ctx.prefix)          # Prefix used
    print(ctx.invoked_with)    # Alias used
    
    # Bot reference
    profile = await ctx.bot.get_self()
    
    # Send messages
    await ctx.send("Message here")
    await ctx.reply("Same as send")
    
    # Typing indicator
    await ctx.typing()
```

## Event Handlers

Listen to real-time events:

```python
@bot.event
async def on_ready():
    """Bot connected and ready"""
    print("Bot is online!")

@bot.event
async def on_message(data):
    """Called for ALL messages (before command processing)"""
    sender = data.get('sender', {}).get('name')
    print(f"Message from {sender}")

@bot.event
async def on_notification(data):
    """New notification received"""
    print(f"Notification: {data}")

@bot.event
async def on_typing(data):
    """Someone is typing"""
    user = data.get('user', {}).get('name')
    print(f"{user} is typing...")

@bot.event
async def on_user_online(data):
    """User came online"""
    user = data.get('user', {}).get('name')
    print(f"{user} is now online")
```

## Cogs (Command Groups)

Cogs organize related commands together. This is useful for large bots:

### Creating a Cog

```python
from interpal.ext.commands import Cog, command, listener

class FunCog(Cog):
    """Fun commands"""
    
    def __init__(self, bot):
        super().__init__(bot)
        self.joke_count = 0
    
    @command()
    async def joke(self, ctx):
        """Tell a joke"""
        self.joke_count += 1
        await ctx.send("Why did the chicken cross the road? 🐔")
    
    @command()
    async def roll(self, ctx, sides: int = 6):
        """Roll a die"""
        import random
        result = random.randint(1, sides)
        await ctx.send(f"🎲 You rolled: {result}")
    
    @listener('on_ready')
    async def on_ready(self):
        """Called when bot is ready"""
        print("FunCog loaded!")
```

### Adding Cogs to Bot

```python
bot = Bot(command_prefix='!')

# Add cog
bot.add_cog(FunCog(bot))

# Remove cog
bot.remove_cog('FunCog')

# Get cog
cog = bot.get_cog('FunCog')
```

### Multiple Cogs Example

```python
class AdminCog(Cog):
    """Admin commands"""
    
    @command(hidden=True)
    async def restart(self, ctx):
        """Restart the bot"""
        await ctx.send("Restarting...")
        # restart logic

class SocialCog(Cog):
    """Social commands"""
    
    @command()
    async def search(self, ctx, country):
        """Search users by country"""
        users = await self.bot.search_users(country=country)
        await ctx.send(f"Found {len(users)} users!")

# Add all cogs
bot.add_cog(AdminCog(bot))
bot.add_cog(SocialCog(bot))
```

## Error Handling

### Default Error Handler

By default, errors are sent to the user and printed to console.

### Custom Error Handler

Override the error handler for custom behavior:

```python
@bot.event
async def on_command_error(ctx, error):
    """Custom error handling"""
    error_str = str(error)
    
    if "Missing required argument" in error_str:
        await ctx.send(f"❌ Missing argument! Use `!help {ctx.command.name}`")
    elif "invalid literal" in error_str:
        await ctx.send("❌ Invalid number format!")
    else:
        await ctx.send(f"❌ Error: {error_str}")
    
    # Log error
    print(f"Error in {ctx.command.name}: {error}")
```

### Try-Catch in Commands

```python
@bot.command()
async def search(ctx, country):
    """Search for users"""
    try:
        users = await bot.search_users(country=country)
        await ctx.send(f"Found {len(users)} users!")
    except Exception as e:
        await ctx.send(f"Search failed: {str(e)}")
```

## Advanced Features

### Help Command

The bot includes a built-in help command:

```
!help              # Show all commands
!help <command>    # Show help for specific command
```

**Disable default help:**

```python
bot = Bot(command_prefix='!', help_command=False)
```

**Custom help command:**

```python
@bot.command(name='help')
async def custom_help(ctx, command_name=None):
    """Custom help"""
    if command_name:
        cmd = bot.get_command(command_name)
        await ctx.send(f"Help for {cmd.name}: {cmd.help}")
    else:
        await ctx.send("Available commands: ping, hello, info")
```

### Type Annotations

Commands automatically convert arguments based on type hints:

```python
@bot.command()
async def repeat(ctx, times: int, message: str):
    """Repeat a message"""
    for i in range(times):
        await ctx.send(f"{i+1}. {message}")
```

**Usage:** `!repeat 3 Hello`

Supported types:
- `int` - Converts to integer
- `float` - Converts to float
- `bool` - Converts to boolean ('true', 'yes', '1' → True)
- `str` - Default, no conversion

### Permission Checks

Implement custom permission checks:

```python
ADMIN_IDS = ['user_id_1', 'user_id_2']

@bot.command()
async def ban(ctx, user_id):
    """Ban a user (admin only)"""
    if ctx.sender_id not in ADMIN_IDS:
        await ctx.send("❌ You don't have permission!")
        return
    
    # Ban logic here
    await ctx.send(f"Banned user {user_id}")
```

### Accessing Bot Methods

All bot methods are available in commands:

```python
@bot.command()
async def stats(ctx):
    """Show bot statistics"""
    profile = await bot.get_self()
    threads = await bot.get_threads()
    notifs = await bot.get_notifications()
    
    stats_text = f"""
**Bot Stats:**
Name: {profile.name}
Threads: {len(threads)}
Notifications: {len(notifs)}
Commands: {len(bot._commands)}
    """
    await ctx.send(stats_text.strip())
```

### Long Running Operations

Show typing indicator for long operations:

```python
@bot.command()
async def search(ctx, country):
    """Search users (may take a while)"""
    await ctx.typing()  # Show typing indicator
    
    users = await bot.search_users(country=country)
    
    # Format results...
    result = f"Found {len(users)} users in {country}!"
    await ctx.send(result)
```

### Command Cooldowns

Implement custom cooldowns:

```python
import time

cooldowns = {}

@bot.command()
async def expensive(ctx):
    """Command with cooldown"""
    user_id = ctx.sender_id
    
    # Check cooldown
    if user_id in cooldowns:
        time_left = 60 - (time.time() - cooldowns[user_id])
        if time_left > 0:
            await ctx.send(f"⏳ Cooldown! Try again in {int(time_left)}s")
            return
    
    # Execute command
    await ctx.send("Executing expensive operation...")
    
    # Set cooldown
    cooldowns[user_id] = time.time()
```

## Complete Example

Here's a complete bot with multiple features:

```python
from interpal.ext.commands import Bot, Cog, command

class MyBot(Bot):
    def __init__(self):
        super().__init__(
            command_prefix='!',
            description='My Awesome Bot',
            username='bot_username',
            password='bot_password',
            persist_session=True
        )
        
        # Add cogs
        self.add_cog(GeneralCog(self))
        self.add_cog(FunCog(self))

class GeneralCog(Cog):
    @command()
    async def hello(self, ctx, name=None):
        """Say hello"""
        target = name or ctx.sender_name
        await ctx.send(f"Hello {target}! 👋")
    
    @command(aliases=['info'])
    async def about(self, ctx):
        """Bot information"""
        profile = await self.bot.get_self()
        await ctx.send(f"I am {profile.name}, a helpful bot!")

class FunCog(Cog):
    @command()
    async def roll(self, ctx, sides: int = 6):
        """Roll a die"""
        import random
        result = random.randint(1, sides)
        await ctx.send(f"🎲 You rolled: {result}")
    
    @command()
    async def joke(self, ctx):
        """Tell a joke"""
        await ctx.send("Why did the bot cross the road? To get to the server! 😄")

# Create and run bot
bot = MyBot()

@bot.event
async def on_ready():
    print("🤖 Bot is ready!")
    profile = await bot.get_self()
    print(f"   Logged in as: {profile.name}")

bot.run()
```

## Comparison with Discord.py

If you're familiar with discord.py, here's how they compare:

| Discord.py | Interpal Bot |
|------------|--------------|
| `@bot.command()` | `@bot.command()` ✅ Same |
| `@bot.event` | `@bot.event` ✅ Same |
| `ctx.send()` | `ctx.send()` ✅ Same |
| `ctx.author` | `ctx.sender_name` |
| `ctx.message` | `ctx.message` ✅ Same |
| `ctx.guild` | N/A (no guilds in Interpal) |
| `bot.add_cog()` | `bot.add_cog()` ✅ Same |
| `commands.Cog` | `Cog` ✅ Same |
| `bot.run(token)` | `bot.run()` (auth in constructor) |

## Tips & Best Practices

1. **Use Cogs** for organizing commands in larger bots
2. **Type hints** make commands more robust (`num: int`)
3. **Error handling** improves user experience
4. **Help text** should be clear and concise
5. **Persistent sessions** avoid re-logging in every time
6. **Hidden commands** for admin/debug features
7. **Aliases** make commands easier to use

## Troubleshooting

### Bot doesn't respond to commands
- Check the prefix is correct
- Ensure you're authenticated
- Check for errors in console

### Commands not found
- Make sure decorator is `@bot.command()` not `@bot.event()`
- Check command name and aliases
- Verify bot is ready (wait for `on_ready`)

### Type conversion errors
- Use try-catch for robust error handling
- Provide clear error messages
- Check user input format

## Next Steps

- Check out the examples: `examples/bot_example.py`, `examples/bot_with_cogs.py`
- Read the main documentation: `docs/GETTING_STARTED.md`
- Explore the API: `docs/API_REFERENCE.md`

---

Happy botting! 🤖✨

