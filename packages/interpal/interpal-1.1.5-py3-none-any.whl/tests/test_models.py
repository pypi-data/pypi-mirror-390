"""
Tests for data models.
"""

import pytest
from datetime import datetime
from interpal.models import User, Profile, Message, Thread, Photo, Album
from interpal.models import Relationship, Bookmark, Like, Notification


class TestUser:
    """Tests for User model."""
    
    def test_user_from_dict(self):
        """Test User creation from dictionary."""
        data = {
            'id': '123456',
            'username': 'testuser',
            'name': 'Test User',
            'age': 25,
            'country': 'USA',
        }
        user = User(data)
        assert user.id == '123456'
        assert user.username == 'testuser'
        assert user.name == 'Test User'
        assert user.age == 25
        assert user.country == 'USA'
    
    def test_user_to_dict(self):
        """Test User conversion to dictionary."""
        user = User({'id': '123', 'name': 'Test'})
        data = user.to_dict()
        assert 'id' in data
        assert 'name' in data


class TestProfile:
    """Tests for Profile model."""
    
    def test_profile_extends_user(self):
        """Test Profile extends User."""
        data = {
            'id': '123',
            'name': 'Test',
            'bio': 'Test bio',
            'languages': ['English', 'Spanish'],
        }
        profile = Profile(data)
        assert profile.id == '123'
        assert profile.name == 'Test'
        assert profile.bio == 'Test bio'
        assert len(profile.languages) == 2


class TestMessage:
    """Tests for Message model."""
    
    def test_message_from_dict(self):
        """Test Message creation from dictionary."""
        data = {
            'id': '789',
            'thread_id': '456',
            'content': 'Hello World',
            'sender': {'id': '123', 'name': 'Sender'},
        }
        message = Message(data)
        assert message.id == '789'
        assert message.thread_id == '456'
        assert message.content == 'Hello World'
        assert message.sender.name == 'Sender'


class TestThread:
    """Tests for Thread model."""
    
    def test_thread_from_dict(self):
        """Test Thread creation from dictionary."""
        data = {
            'id': '456',
            'participants': [
                {'id': '123', 'name': 'User1'},
                {'id': '456', 'name': 'User2'},
            ],
            'unread_count': 5,
        }
        thread = Thread(data)
        assert thread.id == '456'
        assert len(thread.participants) == 2
        assert thread.unread_count == 5


class TestPhoto:
    """Tests for Photo model."""
    
    def test_photo_from_dict(self):
        """Test Photo creation from dictionary."""
        data = {
            'id': '999',
            'url': 'https://example.com/photo.jpg',
            'caption': 'Test photo',
            'likes': 10,
        }
        photo = Photo(data)
        assert photo.id == '999'
        assert photo.url == 'https://example.com/photo.jpg'
        assert photo.caption == 'Test photo'
        assert photo.likes == 10


class TestNotification:
    """Tests for Notification model."""
    
    def test_notification_from_dict(self):
        """Test Notification creation from dictionary."""
        data = {
            'id': '111',
            'type': 'message',
            'message': 'New message',
            'read': False,
        }
        notif = Notification(data)
        assert notif.id == '111'
        assert notif.type == 'message'
        assert notif.message == 'New message'
        assert not notif.read


class TestBaseModel:
    """Tests for BaseModel functionality."""
    
    def test_to_json(self):
        """Test JSON conversion."""
        user = User({'id': '123', 'name': 'Test'})
        json_str = user.to_json()
        assert '"id"' in json_str
        assert '"name"' in json_str
    
    def test_equality(self):
        """Test model equality."""
        user1 = User({'id': '123', 'name': 'Test'})
        user2 = User({'id': '123', 'name': 'Test'})
        user3 = User({'id': '456', 'name': 'Other'})
        assert user1 == user2
        assert user1 != user3

