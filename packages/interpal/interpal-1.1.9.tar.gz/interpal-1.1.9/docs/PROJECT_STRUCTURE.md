# Project Structure

Complete directory structure for the Interpals Python Library.

```
interpal-python-lib/
├── interpal/                      # Main package
│   ├── __init__.py               # Package exports
│   ├── client.py                 # Main client classes
│   ├── auth.py                   # Authentication management
│   ├── http.py                   # HTTP client wrapper
│   ├── websocket.py              # WebSocket client
│   ├── exceptions.py             # Custom exceptions
│   ├── utils.py                  # Utility functions
│   │
│   ├── models/                   # Data models
│   │   ├── __init__.py
│   │   ├── base.py              # Base model class
│   │   ├── user.py              # User models
│   │   ├── message.py           # Message models
│   │   ├── media.py             # Media models
│   │   └── social.py            # Social models
│   │
│   └── api/                      # API endpoint modules
│       ├── __init__.py
│       ├── user.py              # User endpoints
│       ├── messages.py          # Message endpoints
│       ├── search.py            # Search endpoints
│       ├── media.py             # Media endpoints
│       ├── social.py            # Social endpoints
│       └── realtime.py          # Realtime endpoints
│
├── examples/                      # Usage examples
│   ├── basic_sync.py            # Synchronous example
│   ├── async_example.py         # Asynchronous example
│   └── realtime_bot.py          # Real-time bot example
│
├── tests/                         # Test suite
│   ├── __init__.py
│   ├── test_client.py           # Client tests
│   ├── test_models.py           # Model tests
│   ├── test_exceptions.py       # Exception tests
│   └── test_utils.py            # Utility tests
│
├── docs/                          # Documentation (optional)
│
├── README.md                      # Main documentation
├── QUICKSTART.md                  # Quick start guide
├── API_REFERENCE.md               # Complete API reference
├── CONTRIBUTING.md                # Contributing guidelines
├── CHANGELOG.md                   # Version history
├── LICENSE                        # MIT License
├── .gitignore                     # Git ignore rules
├── requirements.txt               # Dependencies
├── setup.py                       # Setup script
├── pyproject.toml                 # Modern Python packaging
└── MANIFEST.in                    # Package manifest
```

## File Descriptions

### Core Package Files

#### `interpal/__init__.py`
- Main package entry point
- Exports all public classes and functions
- Version information

#### `interpal/client.py`
- `InterpalClient` - Synchronous client
- `AsyncInterpalClient` - Asynchronous client
- Main user-facing API

#### `interpal/auth.py`
- `AuthManager` - Authentication management
- Login with credentials
- Session import/export

#### `interpal/http.py`
- `HTTPClient` - Synchronous HTTP client
- `AsyncHTTPClient` - Asynchronous HTTP client
- Rate limiting and retry logic

#### `interpal/websocket.py`
- `WebSocketClient` - Async WebSocket client
- `SyncWebSocketClient` - Sync wrapper
- Event system implementation

#### `interpal/exceptions.py`
- Custom exception hierarchy
- All library exceptions

#### `interpal/utils.py`
- Utility functions
- Data parsing helpers
- Validation functions

### Data Models

#### `interpal/models/base.py`
- `BaseModel` - Base class for all models
- Common functionality (to_dict, to_json, etc.)

#### `interpal/models/user.py`
- `User` - Basic user information
- `Profile` - Extended profile
- `UserSettings` - User settings
- `UserCounters` - Statistics

#### `interpal/models/message.py`
- `Message` - Individual message
- `Thread` - Message thread
- `TypingIndicator` - Typing status

#### `interpal/models/media.py`
- `Photo` - Photo metadata
- `Album` - Photo album
- `MediaUpload` - Upload status

#### `interpal/models/social.py`
- `Relationship` - User relationship
- `Bookmark` - Bookmarked user
- `Like` - Content like
- `Notification` - User notification

### API Modules

#### `interpal/api/user.py`
- User management endpoints
- Profile operations
- Settings management

#### `interpal/api/messages.py`
- Messaging endpoints
- Thread operations
- Message sending

#### `interpal/api/search.py`
- User search
- Location search
- Feed retrieval

#### `interpal/api/media.py`
- Photo upload
- Album management
- Media operations

#### `interpal/api/social.py`
- Friend management
- Blocking/bookmarking
- Like operations

#### `interpal/api/realtime.py`
- Notifications
- Profile views
- Push tokens

### Examples

#### `examples/basic_sync.py`
- Basic synchronous usage
- Common operations
- Error handling

#### `examples/async_example.py`
- Asynchronous operations
- Concurrent requests
- Performance optimization

#### `examples/realtime_bot.py`
- WebSocket events
- Bot implementation
- Event handlers

### Tests

#### `tests/test_client.py`
- Client initialization tests
- Authentication tests
- API module tests

#### `tests/test_models.py`
- Data model tests
- Parsing tests
- Serialization tests

#### `tests/test_exceptions.py`
- Exception tests
- Error handling tests

#### `tests/test_utils.py`
- Utility function tests
- Helper function tests

### Documentation

#### `README.md`
- Main documentation
- Installation guide
- Usage examples
- Feature overview

#### `QUICKSTART.md`
- Quick start guide
- 5-minute tutorial
- Common patterns

#### `API_REFERENCE.md`
- Complete API documentation
- Method signatures
- Parameter descriptions
- Return types

#### `CONTRIBUTING.md`
- Contribution guidelines
- Development setup
- Code style
- Pull request process

#### `CHANGELOG.md`
- Version history
- Release notes
- Breaking changes

### Configuration Files

#### `requirements.txt`
- Runtime dependencies
- Version constraints

#### `setup.py`
- Traditional setup script
- Package metadata
- Dependencies

#### `pyproject.toml`
- Modern Python packaging
- Tool configurations
- Build system

#### `MANIFEST.in`
- Package manifest
- Files to include/exclude

#### `.gitignore`
- Git ignore rules
- Excluded files/directories

#### `LICENSE`
- MIT License
- Copyright information

## Package Size

Estimated package size: ~150KB (without dependencies)

## Dependencies

### Runtime
- `requests>=2.28.0` - HTTP client (~150KB)
- `aiohttp>=3.8.0` - Async HTTP (~500KB)
- `websockets>=10.0` - WebSocket support (~100KB)

### Development
- `pytest>=7.0.0` - Testing
- `pytest-asyncio>=0.20.0` - Async testing
- `black>=22.0.0` - Code formatting
- `flake8>=5.0.0` - Linting
- `mypy>=0.990` - Type checking

## Lines of Code

Approximate lines of code:

```
interpal/
  client.py:        ~400 lines
  auth.py:          ~200 lines
  http.py:          ~350 lines
  websocket.py:     ~250 lines
  exceptions.py:    ~50 lines
  utils.py:         ~150 lines
  
  models/
    base.py:        ~80 lines
    user.py:        ~150 lines
    message.py:     ~100 lines
    media.py:       ~120 lines
    social.py:      ~130 lines
  
  api/
    user.py:        ~100 lines
    messages.py:    ~150 lines
    search.py:      ~120 lines
    media.py:       ~150 lines
    social.py:      ~130 lines
    realtime.py:    ~100 lines

examples/:          ~500 lines
tests/:            ~400 lines

Total:            ~3,500 lines
```

## API Coverage

- 70+ API endpoints
- 15+ data models
- 6 API modules
- 8 event types
- 6 exception types

## Features

✅ Synchronous client  
✅ Asynchronous client  
✅ WebSocket support  
✅ Event system  
✅ Rate limiting  
✅ Auto-retry  
✅ Session management  
✅ Type hints  
✅ Comprehensive docs  
✅ Unit tests  
✅ Examples  

## Next Steps

1. Install dependencies: `pip install -r requirements.txt`
2. Run tests: `pytest`
3. Try examples: `python examples/basic_sync.py`
4. Build package: `python setup.py sdist bdist_wheel`
5. Install locally: `pip install -e .`

---

For more information, see [README.md](README.md)

