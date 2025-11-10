# Getting Started with Interpals Python Library

## 🚀 Installation

### Method 1: Install from PyPI (after publishing)
```bash
pip install interpal-python-lib
```

### Method 2: Install from Source (Local Development)
```bash
# Navigate to the project directory
cd interpal-python-lib

# Install in development mode
pip install -e .
```

### Method 3: Install Dependencies Only
```bash
pip install -r requirements.txt
```

---

## 📝 First Steps

### 1. Import the Library

```python
from interpal import InterpalClient
```

### 2. Create a Client

```python
# Option A: Login with credentials
client = InterpalClient(
    username="your_username",
    password="your_password",
    auto_login=True
)

# Option B: Use existing session cookie
client = InterpalClient(
    session_cookie="interpals_sessid=your_session_cookie"
)
```

### 3. Make Your First Request

```python
# Get your profile
profile = client.get_self()
print(f"Welcome, {profile.name}!")
```

---

## 🎯 Common Use Cases

### Check Messages
```python
threads = client.get_threads()
print(f"You have {len(threads)} conversations")

# Get messages from first thread
if threads:
    messages = client.messages.get_thread_messages(threads[0].id)
    for msg in messages:
        print(f"{msg.sender.name}: {msg.content}")
```

### Send a Message
```python
client.send_message(
    thread_id="1234567890",
    content="Hello from Python!"
)
```

### Search for Users
```python
users = client.search_users(
    country="Japan",
    age_min=20,
    age_max=30,
    language="English"
)

for user in users:
    print(f"{user.name}, {user.age} - {user.city}")
```

### Upload a Photo
```python
photo = client.upload_photo(
    file_path="my_photo.jpg",
    caption="Having a great day!"
)
print(f"Photo uploaded: {photo.url}")
```

---

## 🔄 Asynchronous Usage

### Setup
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
    profile, threads = await asyncio.gather(
        client.get_self(),
        client.get_threads()
    )
    
    print(f"Welcome {profile.name}!")
    print(f"You have {len(threads)} threads")
    
    await client.close()

# Run
asyncio.run(main())
```

---

## 🤖 Real-time Bot

### Basic Bot
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
    
    if 'hello' in content:
        thread_id = data.get('thread_id')
        await client.send_message(thread_id, "Hi there! 👋")

# Start listening
asyncio.run(client.start())
```

---

## 🔐 Session Management

### Export Session
```python
# Login and export session for later use
client = InterpalClient(username="user", password="pass")
client.login()

session = client.export_session()
print(f"Session cookie: {session['session_cookie']}")

# Save to file
with open('session.txt', 'w') as f:
    f.write(session['session_cookie'])
```

### Import Session
```python
# Load session from file
with open('session.txt', 'r') as f:
    session_cookie = f.read().strip()

# Use saved session (no login needed)
client = InterpalClient(session_cookie=session_cookie)

# Verify it works
if client.validate_session():
    print("Session is valid!")
```

---

## 🛠️ Configuration

### Custom User Agent
```python
client = InterpalClient(
    username="user",
    password="pass",
    user_agent="my-app/1.0.0"
)
```

### Rate Limiting
```python
# Adjust request interval (default: 1 second)
client.http._min_request_interval = 2.0  # 2 seconds
```

### Retry Configuration
```python
# Change retry attempts (default: 3)
client.http.max_retries = 5
```

---

## ⚠️ Error Handling

### Basic Error Handling
```python
from interpal.exceptions import (
    AuthenticationError,
    APIError,
    RateLimitError
)

try:
    client = InterpalClient(username="user", password="pass")
    client.login()
except AuthenticationError:
    print("Invalid credentials!")
except APIError as e:
    print(f"API error ({e.status_code}): {e}")
```

### Handle Rate Limiting
```python
try:
    # Make API call
    profile = client.get_self()
except RateLimitError as e:
    print(f"Rate limited. Retry after {e.retry_after} seconds")
    time.sleep(e.retry_after)
    profile = client.get_self()  # Retry
```

---

## 📚 Next Steps

1. **Read the Documentation**
   - [README.md](README.md) - Complete overview
   - [QUICKSTART.md](QUICKSTART.md) - 5-minute tutorial
   - [API_REFERENCE.md](API_REFERENCE.md) - Full API docs

2. **Try the Examples**
   - [examples/basic_sync.py](examples/basic_sync.py)
   - [examples/async_example.py](examples/async_example.py)
   - [examples/realtime_bot.py](examples/realtime_bot.py)

3. **Explore the API**
   - User Management: `client.user.*`
   - Messaging: `client.messages.*`
   - Search: `client.search.*`
   - Media: `client.media.*`
   - Social: `client.social.*`
   - Real-time: `client.realtime.*`

---

## 🔍 Troubleshooting

### "Authentication failed"
- Check username and password
- Verify account is not locked
- Try using session cookie instead

### "Module not found"
- Install dependencies: `pip install -r requirements.txt`
- Make sure you're in the right directory

### "Rate limit exceeded"
- Wait a few seconds between requests
- Library handles this automatically with retries
- Consider using async client for better performance

### "WebSocket won't connect"
- Verify you're authenticated first
- Check internet connection
- Ensure session cookie is valid

---

## 💡 Tips & Best Practices

1. **Save Your Session**: Export session cookie to avoid repeated logins
2. **Use Async**: Async client is much faster for multiple operations
3. **Handle Errors**: Always wrap API calls in try-except blocks
4. **Close Connections**: Call `client.close()` when done
5. **Rate Limiting**: Library handles it automatically, don't worry

---

## 🆘 Getting Help

- 📖 [Full Documentation](README.md)
- 💬 [GitHub Discussions](https://github.com/yourusername/interpal-python-lib/discussions)
- 🐛 [Report Issues](https://github.com/yourusername/interpal-python-lib/issues)
- 📧 Email: support@example.com

---

## ✅ Quick Reference

```python
# Import
from interpal import InterpalClient

# Initialize
client = InterpalClient(username="user", password="pass", auto_login=True)

# Profile
profile = client.get_self()

# Messages
threads = client.get_threads()
messages = client.messages.get_thread_messages(thread_id)
client.send_message(thread_id, "Hello!")

# Search
users = client.search_users(country="Japan")
feed = client.get_feed()

# Media
photo = client.upload_photo("photo.jpg", caption="Hello!")

# Social
friends = client.social.get_friends()
client.social.bookmark_user(user_id, note="Interesting")

# Notifications
notifications = client.get_notifications()

# Close
client.close()
```

---

Happy coding! 🎉

