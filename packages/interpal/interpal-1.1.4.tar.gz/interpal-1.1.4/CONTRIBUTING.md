# Contributing to Interpals Python Library

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing to the project.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/yourusername/interpal-python-lib.git
   cd interpal-python-lib
   ```
3. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
4. **Install dependencies**:
   ```bash
   pip install -e ".[dev]"
   ```

## Development Workflow

### 1. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
```

### 2. Make Your Changes

- Write clean, readable code
- Follow PEP 8 style guidelines
- Add docstrings to all functions and classes
- Update type hints where applicable

### 3. Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=interpal tests/

# Run specific test file
pytest tests/test_client.py
```

### 4. Format Your Code

```bash
# Format with black
black interpal/

# Check with flake8
flake8 interpal/

# Type check with mypy
mypy interpal/
```

### 5. Commit Your Changes

```bash
git add .
git commit -m "Add feature: description of your changes"
```

Use clear, descriptive commit messages:
- `Add feature: user profile caching`
- `Fix bug: WebSocket reconnection issue`
- `Update docs: add async examples`
- `Refactor: improve error handling in HTTP client`

### 6. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub.

## Code Style Guidelines

### Python Style

- Follow PEP 8
- Use 4 spaces for indentation
- Maximum line length: 100 characters
- Use meaningful variable names
- Add type hints to function signatures

### Docstring Format

```python
def function_name(param1: str, param2: int) -> bool:
    """
    Brief description of the function.
    
    Args:
        param1: Description of param1
        param2: Description of param2
        
    Returns:
        Description of return value
        
    Raises:
        ExceptionType: When this exception is raised
    """
    pass
```

### Import Organization

```python
# Standard library imports
import os
import sys

# Third-party imports
import requests
import aiohttp

# Local imports
from .models import User
from .exceptions import APIError
```

## Testing Guidelines

### Writing Tests

Create test files in the `tests/` directory:

```python
import pytest
from interpal import InterpalClient
from interpal.exceptions import AuthenticationError


def test_login_success():
    """Test successful login."""
    client = InterpalClient(username="test", password="test")
    # Test implementation
    

def test_login_failure():
    """Test login with invalid credentials."""
    client = InterpalClient(username="invalid", password="wrong")
    with pytest.raises(AuthenticationError):
        client.login()


@pytest.mark.asyncio
async def test_async_get_profile():
    """Test async profile fetching."""
    from interpal import AsyncInterpalClient
    client = AsyncInterpalClient(session_cookie="test_cookie")
    # Test implementation
```

### Test Coverage

- Aim for at least 80% code coverage
- Test both success and failure cases
- Test edge cases and error conditions
- Mock external API calls

## Documentation

### Updating Documentation

- Update README.md for user-facing changes
- Add docstrings to new functions/classes
- Update examples if API changes
- Document breaking changes in CHANGELOG.md

### Example Code

When adding examples:

```python
# Bad: No context
client.send_message("123", "Hello")

# Good: Clear and complete
from interpal import InterpalClient

client = InterpalClient(session_cookie="your_cookie")
thread_id = "1234567890"
message = "Hello from Python!"
client.send_message(thread_id, message)
```

## Pull Request Guidelines

### Before Submitting

- [ ] All tests pass
- [ ] Code is formatted with black
- [ ] No linting errors
- [ ] Documentation is updated
- [ ] Commit messages are clear
- [ ] Branch is up to date with main

### PR Description Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Changes Made
- Change 1
- Change 2
- Change 3

## Testing
How has this been tested?

## Checklist
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] Code formatted
- [ ] No linting errors
```

## Adding New Features

### API Endpoints

When adding new API endpoints:

1. **Add to appropriate API module** (`interpal/api/`)
2. **Create/update data models** if needed (`interpal/models/`)
3. **Add type hints** for all parameters and returns
4. **Write docstrings** with examples
5. **Add tests** for the new endpoint
6. **Update README** with usage examples

Example:

```python
# In interpal/api/user.py
def get_user_badges(self, user_id: str) -> List[Badge]:
    """
    Get badges for a user.
    
    Args:
        user_id: User ID
        
    Returns:
        List of Badge objects
        
    Example:
        >>> badges = client.user.get_user_badges("123456")
        >>> for badge in badges:
        ...     print(badge.name)
    """
    data = self.http.get(f"/v1/user/{user_id}/badges")
    return [Badge(b) for b in data]
```

### Data Models

When adding new models:

1. **Inherit from BaseModel** (`interpal/models/base.py`)
2. **Override `_from_dict`** for custom parsing
3. **Add type hints** for all attributes
4. **Write docstrings**

```python
from .base import BaseModel
from typing import Optional

class Badge(BaseModel):
    """
    User badge model.
    """
    
    def __init__(self, data: Optional[Dict[str, Any]] = None):
        self.id: Optional[str] = None
        self.name: Optional[str] = None
        self.icon_url: Optional[str] = None
        super().__init__(data)
    
    def _from_dict(self, data: Dict[str, Any]):
        """Parse badge data from API response."""
        self.id = str(data.get('id', ''))
        self.name = data.get('name')
        self.icon_url = data.get('icon_url')
```

## Issue Reporting

### Bug Reports

Include:
- Python version
- Library version
- Minimal code to reproduce
- Expected behavior
- Actual behavior
- Error messages/stack traces

### Feature Requests

Include:
- Clear description of the feature
- Use case / motivation
- Example usage code
- Any relevant API documentation

## Code Review Process

1. Maintainers will review your PR
2. Address any feedback or requested changes
3. Once approved, your PR will be merged
4. Your contribution will be credited

## Community Guidelines

- Be respectful and inclusive
- Provide constructive feedback
- Help others learn and grow
- Follow the Code of Conduct

## Questions?

- Open an issue for questions
- Join discussions on GitHub Discussions
- Check existing issues and PRs

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to the Interpals Python Library! 🎉

