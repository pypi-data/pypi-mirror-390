"""
Tests for utility functions.
"""

import pytest
from datetime import datetime
from interpal.utils import (
    parse_user_id,
    parse_timestamp,
    validate_email,
    build_query_params,
    extract_cookie,
    safe_get,
)
from interpal.exceptions import ValidationError


class TestParseUserId:
    """Tests for parse_user_id."""
    
    def test_parse_string_id(self):
        """Test parsing string ID."""
        assert parse_user_id("123456") == "123456"
    
    def test_parse_int_id(self):
        """Test parsing integer ID."""
        assert parse_user_id(123456) == "123456"
    
    def test_parse_none_raises_error(self):
        """Test parsing None raises error."""
        with pytest.raises(ValidationError):
            parse_user_id(None)
    
    def test_parse_invalid_raises_error(self):
        """Test parsing invalid ID raises error."""
        with pytest.raises(ValidationError):
            parse_user_id("abc123")


class TestParseTimestamp:
    """Tests for parse_timestamp."""
    
    def test_parse_none(self):
        """Test parsing None."""
        assert parse_timestamp(None) is None
    
    def test_parse_datetime(self):
        """Test parsing datetime object."""
        dt = datetime.now()
        assert parse_timestamp(dt) == dt
    
    def test_parse_unix_timestamp(self):
        """Test parsing unix timestamp."""
        timestamp = 1609459200  # 2021-01-01 00:00:00
        result = parse_timestamp(timestamp)
        assert isinstance(result, datetime)
    
    def test_parse_iso_string(self):
        """Test parsing ISO format string."""
        result = parse_timestamp("2021-01-01T00:00:00Z")
        assert isinstance(result, datetime)


class TestValidateEmail:
    """Tests for validate_email."""
    
    def test_valid_email(self):
        """Test valid email addresses."""
        assert validate_email("test@example.com")
        assert validate_email("user.name@domain.co.uk")
    
    def test_invalid_email(self):
        """Test invalid email addresses."""
        assert not validate_email("invalid")
        assert not validate_email("@example.com")
        assert not validate_email("test@")


class TestBuildQueryParams:
    """Tests for build_query_params."""
    
    def test_build_params(self):
        """Test building query parameters."""
        params = {'key1': 'value1', 'key2': 123, 'key3': None}
        result = build_query_params(params)
        assert result == {'key1': 'value1', 'key2': '123'}
        assert 'key3' not in result


class TestExtractCookie:
    """Tests for extract_cookie."""
    
    def test_extract_single_cookie(self):
        """Test extracting a single cookie."""
        cookie_string = "interpals_sessid=abc123; path=/"
        result = extract_cookie(cookie_string, "interpals_sessid")
        assert result == "abc123"
    
    def test_extract_from_multiple_cookies(self):
        """Test extracting from multiple cookies."""
        cookie_string = "cookie1=value1; interpals_sessid=abc123; cookie2=value2"
        result = extract_cookie(cookie_string, "interpals_sessid")
        assert result == "abc123"
    
    def test_extract_missing_cookie(self):
        """Test extracting non-existent cookie."""
        cookie_string = "cookie1=value1; cookie2=value2"
        result = extract_cookie(cookie_string, "missing")
        assert result is None


class TestSafeGet:
    """Tests for safe_get."""
    
    def test_safe_get_nested(self):
        """Test safely getting nested values."""
        data = {'level1': {'level2': {'level3': 'value'}}}
        result = safe_get(data, 'level1', 'level2', 'level3')
        assert result == 'value'
    
    def test_safe_get_missing_key(self):
        """Test safely getting missing key."""
        data = {'level1': {'level2': 'value'}}
        result = safe_get(data, 'level1', 'missing', default='default')
        assert result == 'default'
    
    def test_safe_get_empty_dict(self):
        """Test safely getting from empty dict."""
        result = safe_get({}, 'key', default=None)
        assert result is None

