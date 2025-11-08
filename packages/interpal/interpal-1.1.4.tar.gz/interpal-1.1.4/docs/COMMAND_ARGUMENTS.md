# Command Arguments Guide

## Overview

This guide explains how command arguments work in the Interpal bot framework and best practices for defining command parameters.

## The Issue You Encountered

### Problem
The error occurred because:
```python
@bot.command()
async def echo(ctx: Context, *, message: str = None):  # ❌ Problem: * syntax
    ...
```

The `*` syntax creates **keyword-only arguments**, but the command framework passes arguments positionally through `*args`. This caused a mismatch.

### Solution
Remove the `*` and use a regular parameter:
```python
@bot.command()
async def echo(ctx: Context, message: str = None):  # ✅ Correct
    ...
```

## Multi-Word Arguments

### Automatic Joining (NEW!)

The framework now **automatically joins** all remaining words into the last string parameter!

```python
@bot.command()
async def say(ctx: Context, message: str = None):
    """The 'message' parameter will receive ALL remaining words."""
    await ctx.send(message)

# User types: !say Hello world, how are you?
# message = "Hello world, how are you?"  ✅ Automatic!
```

### How It Works

- If the **last parameter** is a string (or `str`, or `Optional[str]`)
- The framework joins **all remaining arguments** with spaces
- You get the full message as one string

### Examples

#### Single Word Argument
```python
@bot.command()
async def greet(ctx: Context, name: str):
    await ctx.send(f"Hello {name}!")

# !greet Alice
# name = "Alice"
```

#### Multi-Word Last Argument
```python
@bot.command()
async def announce(ctx: Context, message: str):
    await ctx.send(f"📢 Announcement: {message}")

# !announce This is a very long announcement message
# message = "This is a very long announcement message"  ✅
```

#### Mixed Arguments
```python
@bot.command()
async def remind(ctx: Context, time: int, message: str):
    await ctx.send(f"Reminder set for {time} minutes: {message}")

# !remind 30 Remember to check the oven
# time = 30
# message = "Remember to check the oven"  ✅ Auto-joined!
```

#### Optional Multi-Word Argument
```python
@bot.command()
async def echo(ctx: Context, message: str = None):
    if not message:
        await ctx.send("Please provide a message!")
        return
    await ctx.send(f"Echo: {message}")

# !echo
# message = None

# !echo Hello world
# message = "Hello world"
```

## Parameter Types

### String Parameters
```python
@bot.command()
async def cmd(ctx: Context, text: str):
    # text is a string
    pass
```

### Integer Parameters
```python
@bot.command()
async def repeat(ctx: Context, count: int, message: str):
    # count is automatically converted to int
    for _ in range(count):
        await ctx.send(message)

# !repeat 3 Hello
# count = 3 (int)
# message = "Hello"
```

### Float Parameters
```python
@bot.command()
async def calculate(ctx: Context, value: float):
    result = value * 2
    await ctx.send(f"Result: {result}")

# !calculate 3.14
# value = 3.14 (float)
```

### Boolean Parameters
```python
@bot.command()
async def toggle(ctx: Context, enabled: bool):
    await ctx.send(f"Setting: {enabled}")

# !toggle true   -> enabled = True
# !toggle yes    -> enabled = True
# !toggle 1      -> enabled = True
# !toggle false  -> enabled = False
```

### Optional Parameters
```python
@bot.command()
async def search(ctx: Context, query: str, page: int = 1):
    await ctx.send(f"Searching '{query}' on page {page}")

# !search python      -> query="python", page=1
# !search python 2    -> query="python", page=2
```

## Best Practices

### ✅ DO: Use Regular Parameters

```python
@bot.command()
async def good_command(ctx: Context, arg1: str, arg2: int = 0):
    pass
```

### ❌ DON'T: Use Keyword-Only Parameters (`*`)

```python
@bot.command()
async def bad_command(ctx: Context, *, arg: str):  # ❌ Won't work
    pass
```

### ✅ DO: Put String Parameters Last

```python
@bot.command()
async def announce(ctx: Context, priority: int, message: str):
    # ✅ message (string) is last, so it captures all remaining words
    pass
```

### ❌ DON'T: Put String Parameters Before Other Parameters

```python
@bot.command()
async def confusing(ctx: Context, message: str, priority: int):
    # ❌ Won't work as expected - message only gets first word
    pass
```

### ✅ DO: Add Type Hints

```python
@bot.command()
async def typed(ctx: Context, count: int, name: str):
    # ✅ Clear types help with automatic conversion
    pass
```

### ✅ DO: Provide Defaults for Optional Args

```python
@bot.command()
async def flexible(ctx: Context, arg1: str, arg2: str = "default"):
    # ✅ arg2 is optional
    pass
```

## Advanced Examples

### Command with Validation
```python
@bot.command()
async def kick(ctx: Context, user_id: str, reason: str = "No reason provided"):
    """Kick a user with optional reason."""
    if not user_id:
        await ctx.send("❌ Please provide a user ID")
        return
    
    await ctx.send(f"Kicked user {user_id}. Reason: {reason}")

# !kick 12345
# !kick 12345 Spam and abuse
```

### Command with Multiple Optional Args
```python
@bot.command()
async def search(ctx: Context, country: str, min_age: int = None, max_age: int = None):
    """Search users by country and optional age range."""
    filters = f"Country: {country}"
    if min_age:
        filters += f", Min Age: {min_age}"
    if max_age:
        filters += f", Max Age: {max_age}"
    
    await ctx.send(f"Searching with filters: {filters}")

# !search USA
# !search USA 18
# !search USA 18 30
```

### Command with Type Checking
```python
@bot.command()
async def calculate(ctx: Context, operation: str, a: float, b: float):
    """Perform math operations."""
    try:
        if operation == "add":
            result = a + b
        elif operation == "multiply":
            result = a * b
        else:
            await ctx.send("Unknown operation")
            return
        
        await ctx.send(f"Result: {result}")
    except Exception as e:
        await ctx.send(f"Error: {e}")

# !calculate add 5 3
# !calculate multiply 2.5 4
```

## Error Handling

### Missing Required Arguments
```python
@bot.command()
async def require_arg(ctx: Context, required: str):
    await ctx.send(f"Got: {required}")

# !require_arg        -> Error: Missing required argument
# !require_arg test   -> OK
```

### Type Conversion Errors
```python
@bot.command()
async def number_cmd(ctx: Context, value: int):
    await ctx.send(f"Number: {value}")

# !number_cmd 42      -> OK, value = 42
# !number_cmd hello   -> Error (can't convert to int)
```

### Custom Error Handling
```python
@bot.event
async def on_command_error(ctx: Context, error: Exception):
    """Custom error handler."""
    if "Missing required argument" in str(error):
        await ctx.send("❌ Please provide all required arguments!")
    else:
        await ctx.send(f"❌ Error: {error}")
```

## Summary

- ✅ **Last string parameter** automatically captures all remaining words
- ✅ Use **regular parameters** (not `*` keyword-only)
- ✅ Add **type hints** for automatic conversion
- ✅ Provide **defaults** for optional parameters
- ✅ Put **string parameters last** for multi-word support
- ✅ The framework handles **type conversion** automatically

## See Also

- [COMMAND_FRAMEWORK_UPDATES.md](COMMAND_FRAMEWORK_UPDATES.md) - Event model integration
- [examples/bot_with_event_models.py](../examples/bot_with_event_models.py) - Complete examples
- [examples/simple_bot.py](../simple_bot.py) - Simple bot examples

