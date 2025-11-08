# Quick Start Guide

Get up and running with the Interpals Python Library in 5 minutes!

## Installation

```bash
pip install interpal-python-lib
```

## 1. Simple Login and Profile

```python
from interpal import InterpalClient

# Login with persistent session (Recommended!)
# Sessions are saved and reused for 24 hours
client = InterpalClient(
    username="your_username",
    password="your_password",
    auto_login=True,
    persist_session=True  # No need to login every time!
)

# Get your profile
profile = client.get_self()
print(f"Hello, {profile.name}!")
print(f"You're {profile.age} from {profile.city}, {profile.country}")
```

## 2. Check Messages

```python
# Get your message threads
threads = client.get_threads()
print(f"You have {len(threads)} conversations")

# Read messages from first thread
if threads:
    thread = threads[0]
    messages = client.messages.get_thread_messages(thread.id, limit=10)
    
    for msg in messages:
        print(f"{msg.sender.name}: {msg.content}")
```

## 3. Send a Message

```python
# Send to existing thread
client.send_message(
    thread_id="1234567890",
    content="Hello from Python!"
)

# Start new conversation
client.messages.start_conversation(
    user_id="9876543210",
    content="Hey! Nice to meet you!"
)
```

## 4. Search for Users

```python
# Search by location and age
users = client.search_users(
    country="Japan",
    age_min=20,
    age_max=30,
    language="English"
)

for user in users:
    print(f"{user.name}, {user.age} - {user.city}")
```

## 5. Upload a Photo

```python
# Upload photo with caption
photo = client.upload_photo(
    file_path="my_photo.jpg",
    caption="Having a great day!"
)
print(f"Photo uploaded: {photo.url}")
```

## 6. Get Notifications

```python
# Check notifications
notifications = client.get_notifications()
print(f"You have {len(notifications)} notifications")

for notif in notifications[:5]:
    print(f"{notif.type}: {notif.message}")
```

## 7. Session Management

### Automatic Persistent Sessions (Recommended)

```python
# Enable persistent sessions - saves and reuses for 24 hours
client = InterpalClient(
    username="your_username",
    password="your_password",
    auto_login=True,
    persist_session=True  # Session saved to .interpals_session.json
)

# Check session status
session_info = client.get_session_info()
print(f"Time remaining: {session_info['time_remaining']}")
print(f"Expires at: {session_info['expires_at']}")

# Custom session file and expiration
client = InterpalClient(
    username="your_username",
    password="your_password",
    auto_login=True,
    persist_session=True,
    session_file="my_session.json",  # Custom location
    session_expiration_hours=48  # 48 hours instead of 24
)
```

### Manual Session Export/Import

```python
# Export session for later use
session = client.export_session()
print(f"Cookie: {session['session_cookie']}")

# Use saved session (no login needed)
client = InterpalClient(
    session_cookie=session['session_cookie']
)
```

## 8. Async Operations (Advanced)

```python
import asyncio
from interpal import AsyncInterpalClient

async def main():
    client = AsyncInterpalClient(
        username="your_username",
        password="your_password"
    )
    client.login()
    
    # Fetch multiple things at once
    profile, threads, feed = await asyncio.gather(
        client.get_self(),
        client.get_threads(),
        client.get_feed()
    )
    
    print(f"Welcome {profile.name}!")
    print(f"Threads: {len(threads)}, Feed items: {len(feed)}")
    
    await client.close()

asyncio.run(main())
```

## 9. Real-time Bot (WebSocket)

```python
import asyncio
from interpal import AsyncInterpalClient

client = AsyncInterpalClient(session_cookie="your_session_cookie")

@client.event('on_ready')
async def on_ready(data=None):
    print("Bot is online!")

@client.event('on_message')
async def on_message(data):
    content = data.get('content', '').lower()
    thread_id = data.get('thread_id')
    
    if 'hello' in content:
        await client.send_message(thread_id, "Hi there! 👋")

# Start listening
asyncio.run(client.start())
```

## Common Patterns

### Error Handling

```python
from interpal import InterpalClient
from interpal.exceptions import AuthenticationError, APIError

try:
    client = InterpalClient(username="user", password="pass")
    client.login()
except AuthenticationError:
    print("Invalid credentials!")
except APIError as e:
    print(f"API error: {e}")
```

### Pagination

```python
# Get older messages
messages = client.messages.get_thread_messages(
    thread_id="123",
    limit=50,
    offset=0  # Start from beginning
)

# Get next page
more_messages = client.messages.get_thread_messages(
    thread_id="123",
    limit=50,
    offset=50  # Skip first 50
)
```

### Typing Indicator

```python
# Show typing in a thread
client.messages.set_typing(thread_id="123", typing=True)

# Stop typing
client.messages.set_typing(thread_id="123", typing=False)
```

### Mark as Read

```python
# Mark thread as viewed
client.messages.mark_thread_viewed(thread_id="123")
```

## Next Steps

- 📖 Read the [full documentation](README.md)
- 💡 Check out [examples](examples/)
- 🐛 Report issues on [GitHub](https://github.com/yourusername/interpal-python-lib/issues)
- 💬 Join the discussions

## Tips

1. **Use persistent sessions**: Enable `persist_session=True` to avoid re-authenticating every run
2. **Use async for speed**: Async client is much faster for multiple operations
3. **Handle errors gracefully**: Always wrap API calls in try-except blocks
4. **Rate limiting**: The library handles rate limiting automatically
5. **Close connections**: Always call `client.close()` when done
6. **Multiple accounts**: Use different `session_file` paths for different accounts

## Troubleshooting

### "Authentication failed"
- Check your username and password
- Make sure your account isn't locked
- Try using a session cookie instead

### "Rate limit exceeded"
- The library will automatically retry
- Wait a few seconds between requests
- Use async client for better performance

### "WebSocket won't connect"
- Make sure you're authenticated
- Check your internet connection
- Verify the session cookie is valid

## Need Help?

- 📚 [Full Documentation](README.md)
- 💬 [GitHub Discussions](https://github.com/yourusername/interpal-python-lib/discussions)
- 🐛 [Report a Bug](https://github.com/yourusername/interpal-python-lib/issues)

---

Happy coding! 🚀

