# Session Persistence Guide

## Overview

The Interpals Python Library now supports **automatic session persistence**, which means you don't need to login every time you run your script. Sessions are saved to a file and automatically reused until they expire.

## Key Features

✅ **Automatic Session Storage** - Sessions are saved to `.interpals_session.json` by default  
✅ **Configurable Expiration** - Default 24 hours, customizable to any duration  
✅ **Automatic Validation** - Validates saved sessions and re-logins if expired  
✅ **Multiple Accounts** - Support for separate session files per account  
✅ **Session Info** - Check session status, expiration time, and more  
✅ **Manual Control** - Clear sessions manually when needed  

## Quick Start

### Basic Usage

```python
from interpal import InterpalClient

# Enable persistent sessions
client = InterpalClient(
    username="your_username",
    password="your_password",
    auto_login=True,
    persist_session=True  # This is the magic! ✨
)

# First run: Logs in and saves session to .interpals_session.json
# Next runs: Automatically loads and uses saved session
# After 24 hours: Automatically re-logins and saves new session
```

### How It Works

1. **First Run**:
   - Logs in with your credentials
   - Saves session cookie and auth token to file
   - Records expiration time (24 hours by default)

2. **Subsequent Runs** (within 24 hours):
   - Loads saved session from file
   - Validates the session is still valid
   - Uses saved session instead of logging in

3. **After Expiration** (>24 hours):
   - Detects expired session
   - Automatically logs in again with stored credentials
   - Saves new session to file

## Configuration Options

### Custom Session File Location

```python
client = InterpalClient(
    username="your_username",
    password="your_password",
    auto_login=True,
    persist_session=True,
    session_file="my_custom_session.json"  # Custom file path
)
```

### Custom Expiration Time

```python
client = InterpalClient(
    username="your_username",
    password="your_password",
    auto_login=True,
    persist_session=True,
    session_expiration_hours=48  # Expire after 48 hours instead of 24
)
```

### Multiple Accounts

```python
# Account 1
client1 = InterpalClient(
    username="account1@example.com",
    password="password1",
    auto_login=True,
    persist_session=True,
    session_file="account1_session.json"
)

# Account 2
client2 = InterpalClient(
    username="account2@example.com",
    password="password2",
    auto_login=True,
    persist_session=True,
    session_file="account2_session.json"
)
```

## Session Management Methods

### Check Session Info

```python
session_info = client.get_session_info()

if session_info:
    print(f"Username: {session_info['username']}")
    print(f"Created at: {session_info['created_at']}")
    print(f"Expires at: {session_info['expires_at']}")
    print(f"Time remaining: {session_info['time_remaining']}")
    print(f"Is expired: {session_info['is_expired']}")
```

### Clear Saved Session

```python
# Manually clear the saved session file
client.clear_saved_session()
```

## Async Client Support

The async client also supports persistent sessions:

```python
from interpal import AsyncInterpalClient

client = AsyncInterpalClient(
    username="your_username",
    password="your_password",
    persist_session=True
)

client.login()  # Saves session automatically

# Use async client as normal
profile = await client.get_self()
```

## Session File Format

The session file is stored as JSON:

```json
{
  "session_cookie": "abc123...",
  "auth_token": "xyz789...",
  "username": "your_username",
  "created_at": "2024-11-04T12:00:00",
  "expires_at": "2024-11-05T12:00:00"
}
```

**Security Note**: Session files contain sensitive authentication data. The library automatically sets file permissions to user-only on Unix systems. Make sure to add `*_session.json` to your `.gitignore` file.

## Examples

See the complete examples in:
- `examples/persistent_session.py` - Comprehensive examples of all features
- `examples/basic_sync.py` - Updated to use persistent sessions

## Benefits

### Without Persistent Sessions
```python
# Every time you run your script:
client = InterpalClient(username="user", password="pass")
client.login()  # ⏰ Logs in every time (slow!)
# ... do work ...
```

### With Persistent Sessions
```python
# First run:
client = InterpalClient(
    username="user",
    password="pass",
    auto_login=True,
    persist_session=True
)
# ✅ Logs in and saves session

# Next 100 runs (within 24 hours):
client = InterpalClient(
    username="user",
    password="pass",
    auto_login=True,
    persist_session=True
)
# ⚡ Instantly uses saved session (fast!)
```

## Troubleshooting

### Session validation fails
If you see "Saved session is invalid", the library will automatically re-login. This can happen if:
- The session was manually invalidated on Interpals
- The session file was corrupted
- Too much time passed between uses

### Session file not found
On first run, there won't be a session file. The library will login and create one automatically.

### Multiple scripts using same session
If you have multiple scripts running simultaneously, they can share the same session file. However, if one script's login invalidates the session, others may need to re-login.

## Security Best Practices

1. **Add to .gitignore**: Never commit session files to version control
   ```gitignore
   .interpals_session.json
   *_session.json
   ```

2. **File Permissions**: On Unix systems, the library automatically sets files to user-only (600)

3. **Secure Storage**: Store session files in secure locations, not publicly accessible directories

4. **Clear Old Sessions**: Periodically clear old session files you no longer need

5. **Environment Variables**: Consider storing credentials in environment variables:
   ```python
   import os
   
   client = InterpalClient(
       username=os.getenv("INTERPALS_USERNAME"),
       password=os.getenv("INTERPALS_PASSWORD"),
       persist_session=True
   )
   ```

## Migration Guide

### From Manual Session Export/Import

**Old Way:**
```python
# First script run
client = InterpalClient(username="user", password="pass")
client.login()
session = client.export_session()
# Save session somewhere manually...

# Later runs
# Load session manually...
client = InterpalClient(session_cookie=saved_cookie)
```

**New Way:**
```python
# All runs (automatic!)
client = InterpalClient(
    username="user",
    password="pass",
    auto_login=True,
    persist_session=True  # That's it!
)
```

## FAQ

**Q: Is my session secure?**  
A: Session files are stored with restricted permissions on Unix systems. Always add them to `.gitignore` and don't share them.

**Q: What happens if I change my password?**  
A: The saved session will become invalid. The library will detect this and re-login with your new credentials.

**Q: Can I disable persistent sessions temporarily?**  
A: Yes, just set `persist_session=False` or omit it (defaults to False).

**Q: Where is the session file stored?**  
A: By default in the current working directory as `.interpals_session.json`. You can customize this with the `session_file` parameter.

**Q: Can I use this in production?**  
A: Yes! The session persistence is production-ready. Consider using longer expiration times (48+ hours) for production bots.

## Implementation Details

The session persistence is implemented through:
- `SessionManager` class in `interpal/session_manager.py`
- Integrated into `InterpalClient` and `AsyncInterpalClient`
- Automatic validation on initialization
- Transparent re-login on expiration

---

**Version**: 1.1.0  
**Last Updated**: November 4, 2024

