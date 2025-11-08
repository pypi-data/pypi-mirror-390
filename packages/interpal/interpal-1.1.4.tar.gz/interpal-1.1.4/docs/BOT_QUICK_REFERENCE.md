# Bot Extension Quick Reference

Quick reference for the Interpal Bot Extension (Discord.py-style commands).

## Basic Setup

```python
from interpal.ext.commands import Bot

bot = Bot(
    command_prefix='!',
    username='user',
    password='pass',
    persist_session=True
)

bot.run()
```

## Commands Cheat Sheet

### Basic Command
```python
@bot.command()
async def ping(ctx):
    await ctx.send("Pong!")
```

### Command with Arguments
```python
@bot.command()
async def greet(ctx, name):
    await ctx.send(f"Hello {name}!")
```

### Optional Arguments
```python
@bot.command()
async def hello(ctx, name=None):
    await ctx.send(f"Hi {name or ctx.sender_name}!")
```

### Type Hints
```python
@bot.command()
async def add(ctx, a: int, b: int):
    await ctx.send(f"Result: {a + b}")
```

### Variable Arguments
```python
@bot.command()
async def echo(ctx, *words):
    await ctx.send(' '.join(words))
```

### Aliases
```python
@bot.command(aliases=['h', 'hi'])
async def hello(ctx):
    await ctx.send("Hello!")
```

### Hidden Command
```python
@bot.command(hidden=True)
async def secret(ctx):
    await ctx.send("Secret command!")
```

## Context (ctx) Properties

```python
ctx.sender_name     # Sender's name
ctx.sender_id       # Sender's user ID
ctx.thread_id       # Thread ID
ctx.content         # Full message content
ctx.command.name    # Command name
ctx.prefix          # Prefix used
ctx.bot             # Bot instance
```

## Context Methods

```python
await ctx.send("message")       # Send message
await ctx.reply("reply")        # Reply to message
await ctx.typing()              # Show typing indicator
```

## Events

```python
@bot.event
async def on_ready():
    print("Bot ready!")

@bot.event
async def on_message(data):
    print("Message received")

@bot.event
async def on_notification(data):
    print("Notification!")
```

## Cogs (Command Groups)

```python
from interpal.ext.commands import Cog, command

class MyCog(Cog):
    @command()
    async def test(self, ctx):
        await ctx.send("Test!")

# Add to bot
bot.add_cog(MyCog(bot))
```

## Error Handling

```python
@bot.event
async def on_command_error(ctx, error):
    await ctx.send(f"Error: {error}")
```

## Bot Methods

```python
# Accessing Interpal API
await bot.get_self()
await bot.get_threads()
await bot.get_notifications()
await bot.search_users(country="Japan")
await bot.send_message(thread_id, "message")
```

## Help Command

Built-in help is automatic:
```
!help              # List all commands
!help <command>    # Help for specific command
```

Disable help:
```python
bot = Bot(command_prefix='!', help_command=False)
```

## Running the Bot

```python
# Blocking (runs until stopped)
bot.run()

# Or use asyncio
import asyncio
asyncio.run(bot.start())
```

## Complete Minimal Example

```python
from interpal.ext.commands import Bot

bot = Bot(command_prefix='!', session_cookie='your_cookie')

@bot.command()
async def hello(ctx):
    await ctx.send("Hello!")

@bot.event
async def on_ready():
    print("Ready!")

bot.run()
```

## Discord.py Comparison

| Feature | Discord.py | Interpal Bot |
|---------|-----------|--------------|
| Create bot | `bot = commands.Bot(prefix='!')` | `bot = Bot(command_prefix='!')` |
| Command | `@bot.command()` | `@bot.command()` ✅ |
| Event | `@bot.event` | `@bot.event` ✅ |
| Context | `ctx.send()` | `ctx.send()` ✅ |
| Cogs | `commands.Cog` | `Cog` ✅ |
| Run | `bot.run(token)` | `bot.run()` |
| Author | `ctx.author` | `ctx.sender_name` |
| Channel | `ctx.channel` | `ctx.thread_id` |

## Tips

- ✅ Use `persist_session=True` to avoid re-login
- ✅ Add docstrings to commands for help text
- ✅ Use type hints for automatic conversion
- ✅ Organize large bots with Cogs
- ✅ Handle errors with `on_command_error`
- ✅ Check authentication: `bot.is_authenticated`

## Common Patterns

### Permission Check
```python
ADMINS = ['user_id_1', 'user_id_2']

@bot.command()
async def admin(ctx):
    if ctx.sender_id not in ADMINS:
        await ctx.send("No permission!")
        return
    await ctx.send("Admin command executed")
```

### Long Operation
```python
@bot.command()
async def search(ctx, country):
    await ctx.typing()
    users = await bot.search_users(country=country)
    await ctx.send(f"Found {len(users)} users!")
```

### Error Handling in Command
```python
@bot.command()
async def safe(ctx):
    try:
        result = await bot.get_threads()
        await ctx.send(f"Threads: {len(result)}")
    except Exception as e:
        await ctx.send(f"Error: {e}")
```

---

**Full Documentation:** [Bot Extension Guide](BOT_EXTENSION.md)

