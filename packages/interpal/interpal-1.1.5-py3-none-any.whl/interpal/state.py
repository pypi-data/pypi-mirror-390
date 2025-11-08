"""
State management implementation following Discord.py's ConnectionState pattern.
Provides centralized state management, memory-efficient caching, and object lifecycle management.
"""

import weakref
import time
import asyncio
from collections import OrderedDict
from typing import Dict, Any, Optional, List, Callable, Union
from .models.user import User, Profile, UserSettings, UserCounters
from .models.message import Message, Thread, TypingIndicator
from .models.media import Photo, Album, MediaUpload


class InterpalState:
    """
    Centralized state management following Discord.py's ConnectionState pattern.

    Provides memory-efficient caching with weak references, object factory patterns,
    and cache eviction policies for optimal performance.
    """

    def __init__(self, dispatch: Optional[Callable] = None, http: Optional[Any] = None, **options):
        """
        Initialize the InterpalState.

        Args:
            dispatch: Event dispatch function
            http: HTTP client instance
            max_messages: Maximum number of messages to cache (default: 1000)
            cache_users: Enable user caching (default: True)
            cache_threads: Enable thread caching (default: True)
            weak_references: Use weak references for memory efficiency (default: True)
        """
        self.dispatch = dispatch
        self.http = http

        # Configuration options
        self.max_messages = options.get('max_messages', 1000)
        self.cache_users = options.get('cache_users', True)
        self.cache_threads = options.get('cache_threads', True)
        self.weak_references = options.get('weak_references', True)

        # Weak reference caches for memory efficiency
        if self.weak_references:
            self._users = weakref.WeakValueDictionary()
            self._profiles = weakref.WeakValueDictionary()
            self._threads = weakref.WeakValueDictionary()
        else:
            self._users = {}
            self._profiles = {}
            self._threads = {}

        # Strong reference caches with LRU eviction
        self._messages = OrderedDict()
        self._photos = OrderedDict()
        self._albums = OrderedDict()

        # Cache management
        self._cache_handlers = {}
        self._creation_handlers = {}

        # Statistics
        self._stats = {
            'cache_hits': 0,
            'cache_misses': 0,
            'objects_created': 0,
            'objects_updated': 0,
            'evictions': 0
        }

    # User and Profile Factory Methods

    def create_user(self, data: Dict[str, Any]) -> User:
        """
        Create or update a User object.

        Args:
            data: User data from API

        Returns:
            User instance
        """
        if not self.cache_users:
            return User(state=self, data=data)

        user_id = data.get('id', data.get('user_id'))
        if user_id is None:
            return User(state=self, data=data)

        # Check cache first
        if user_id in self._users:
            user = self._users[user_id]
            user._update(data)
            self._stats['objects_updated'] += 1
            self._stats['cache_hits'] += 1
            return user

        # Create new user
        user = User(state=self, data=data)
        self._users[user_id] = user
        self._stats['objects_created'] += 1
        self._stats['cache_misses'] += 1

        # Call creation handlers
        self._call_creation_handlers('user', user)

        return user

    def create_profile(self, data: Dict[str, Any]) -> Profile:
        """
        Create or update a Profile object.

        Args:
            data: Profile data from API

        Returns:
            Profile instance
        """
        if not self.cache_users:
            return Profile(state=self, data=data)

        user_id = data.get('id', data.get('user_id'))
        if user_id is None:
            return Profile(state=self, data=data)

        # Check cache first
        if user_id in self._profiles:
            profile = self._profiles[user_id]
            profile._update(data)
            self._stats['objects_updated'] += 1
            self._stats['cache_hits'] += 1
            return profile

        # Create new profile
        profile = Profile(state=self, data=data)
        self._profiles[user_id] = profile
        self._stats['objects_created'] += 1
        self._stats['cache_misses'] += 1

        # Call creation handlers
        self._call_creation_handlers('profile', profile)

        return profile

    # Message and Thread Factory Methods

    def create_message(self, data: Dict[str, Any]) -> Message:
        """
        Create or update a Message object with LRU caching.

        Args:
            data: Message data from API

        Returns:
            Message instance
        """
        message_id = data.get('id')
        if message_id is None:
            return Message(state=self, data=data)

        # Check cache first
        if message_id in self._messages:
            message = self._messages[message_id]
            message._update(data)
            # Move to end (most recently used)
            self._messages.move_to_end(message_id)
            self._stats['objects_updated'] += 1
            self._stats['cache_hits'] += 1
            return message

        # Create new message
        message = Message(state=self, data=data)
        self._add_to_cache(self._messages, message_id, message, self.max_messages)
        self._stats['objects_created'] += 1
        self._stats['cache_misses'] += 1

        # Call creation handlers
        self._call_creation_handlers('message', message)

        return message

    def create_thread(self, data: Dict[str, Any]) -> Thread:
        """
        Create or update a Thread object.

        Args:
            data: Thread data from API

        Returns:
            Thread instance
        """
        if not self.cache_threads:
            return Thread(state=self, data=data)

        thread_id = data.get('id', data.get('thread_id'))
        if thread_id is None:
            return Thread(state=self, data=data)

        # Check cache first
        if thread_id in self._threads:
            thread = self._threads[thread_id]
            thread._update(data)
            self._stats['objects_updated'] += 1
            self._stats['cache_hits'] += 1
            return thread

        # Create new thread
        thread = Thread(state=self, data=data)
        self._threads[thread_id] = thread
        self._stats['objects_created'] += 1
        self._stats['cache_misses'] += 1

        # Call creation handlers
        self._call_creation_handlers('thread', thread)

        return thread

    # Media Factory Methods

    def create_photo(self, data: Dict[str, Any]) -> Photo:
        """
        Create or update a Photo object with LRU caching.

        Args:
            data: Photo data from API

        Returns:
            Photo instance
        """
        photo_id = data.get('id')
        if photo_id is None:
            return Photo(state=self, data=data)

        # Check cache first
        if photo_id in self._photos:
            photo = self._photos[photo_id]
            photo._update(data)
            self._photos.move_to_end(photo_id)
            self._stats['objects_updated'] += 1
            self._stats['cache_hits'] += 1
            return photo

        # Create new photo
        photo = Photo(state=self, data=data)
        self._add_to_cache(self._photos, photo_id, photo, self.max_messages)
        self._stats['objects_created'] += 1
        self._stats['cache_misses'] += 1

        # Call creation handlers
        self._call_creation_handlers('photo', photo)

        return photo

    def create_album(self, data: Dict[str, Any]) -> Album:
        """
        Create or update an Album object with LRU caching.

        Args:
            data: Album data from API

        Returns:
            Album instance
        """
        album_id = data.get('id')
        if album_id is None:
            return Album(state=self, data=data)

        # Check cache first
        if album_id in self._albums:
            album = self._albums[album_id]
            album._update(data)
            self._albums.move_to_end(album_id)
            self._stats['objects_updated'] += 1
            self._stats['cache_hits'] += 1
            return album

        # Create new album
        album = Album(state=self, data=data)
        self._add_to_cache(self._albums, album_id, album, self.max_messages // 2)
        self._stats['objects_created'] += 1
        self._stats['cache_misses'] += 1

        # Call creation handlers
        self._call_creation_handlers('album', album)

        return album

    # Cache Management Methods

    def _add_to_cache(self, cache: OrderedDict, key: str, obj: Any, max_size: int):
        """
        Add object to cache with LRU eviction.

        Args:
            cache: OrderedDict cache
            key: Cache key
            obj: Object to cache
            max_size: Maximum cache size
        """
        cache[key] = obj

        # Evict oldest entries if cache is full
        while len(cache) > max_size:
            oldest_key = next(iter(cache))
            del cache[oldest_key]
            self._stats['evictions'] += 1

    def get_cached_user(self, user_id: str) -> Optional[User]:
        """
        Get cached user by ID.

        Args:
            user_id: User ID

        Returns:
            Cached User or None
        """
        user = self._users.get(user_id)
        if user:
            self._stats['cache_hits'] += 1
        else:
            self._stats['cache_misses'] += 1
        return user

    def get_cached_profile(self, user_id: str) -> Optional[Profile]:
        """
        Get cached profile by ID.

        Args:
            user_id: User ID

        Returns:
            Cached Profile or None
        """
        profile = self._profiles.get(user_id)
        if profile:
            self._stats['cache_hits'] += 1
        else:
            self._stats['cache_misses'] += 1
        return profile

    def get_cached_message(self, message_id: str) -> Optional[Message]:
        """
        Get cached message by ID.

        Args:
            message_id: Message ID

        Returns:
            Cached Message or None
        """
        message = self._messages.get(message_id)
        if message:
            # Move to end (most recently used)
            self._messages.move_to_end(message_id)
            self._stats['cache_hits'] += 1
        else:
            self._stats['cache_misses'] += 1
        return message

    def get_cached_thread(self, thread_id: str) -> Optional[Thread]:
        """
        Get cached thread by ID.

        Args:
            thread_id: Thread ID

        Returns:
            Cached Thread or None
        """
        thread = self._threads.get(thread_id)
        if thread:
            self._stats['cache_hits'] += 1
        else:
            self._stats['cache_misses'] += 1
        return thread

    # Cache Clearing Methods

    def clear_user_cache(self):
        """Clear all user caches."""
        self._users.clear()
        self._profiles.clear()

    def clear_message_cache(self):
        """Clear all message caches."""
        self._messages.clear()
        self._threads.clear()

    def clear_media_cache(self):
        """Clear all media caches."""
        self._photos.clear()
        self._albums.clear()

    def clear_all_caches(self):
        """Clear all caches."""
        self.clear_user_cache()
        self.clear_message_cache()
        self.clear_media_cache()

    # Event Handler Management

    def add_cache_handler(self, event_type: str, callback: Callable):
        """
        Add a cache event handler.

        Args:
            event_type: Type of event ('eviction', 'hit', 'miss')
            callback: Callback function
        """
        if event_type not in self._cache_handlers:
            self._cache_handlers[event_type] = []
        self._cache_handlers[event_type].append(callback)

    def add_creation_handler(self, object_type: str, callback: Callable):
        """
        Add an object creation handler.

        Args:
            object_type: Type of object ('user', 'message', etc.)
            callback: Callback function
        """
        if object_type not in self._creation_handlers:
            self._creation_handlers[object_type] = []
        self._creation_handlers[object_type].append(callback)

    def _call_creation_handlers(self, object_type: str, obj: Any):
        """Call creation handlers for an object type."""
        handlers = self._creation_handlers.get(object_type, [])
        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    # Handle async handlers in sync context by creating a task
                    if self.dispatch:
                        self.dispatch(f'raw_{object_type}_created', obj)
                else:
                    handler(obj)
            except Exception as e:
                # Log but don't let handler failures break object creation
                if self.dispatch:
                    self.dispatch('error', e)

    # Statistics and Monitoring

    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            Dictionary with cache statistics
        """
        total_requests = self._stats['cache_hits'] + self._stats['cache_misses']
        hit_rate = self._stats['cache_hits'] / max(1, total_requests)

        return {
            'cache_hits': self._stats['cache_hits'],
            'cache_misses': self._stats['cache_misses'],
            'hit_rate': hit_rate,
            'objects_created': self._stats['objects_created'],
            'objects_updated': self._stats['objects_updated'],
            'evictions': self._stats['evictions'],
            'cache_sizes': {
                'users': len(self._users),
                'profiles': len(self._profiles),
                'messages': len(self._messages),
                'threads': len(self._threads),
                'photos': len(self._photos),
                'albums': len(self._albums)
            }
        }

    def reset_stats(self):
        """Reset cache statistics."""
        self._stats = {
            'cache_hits': 0,
            'cache_misses': 0,
            'objects_created': 0,
            'objects_updated': 0,
            'evictions': 0
        }

    # Configuration Methods

    def update_config(self, **options):
        """
        Update state configuration.

        Args:
            **options: Configuration options to update
        """
        if 'max_messages' in options:
            self.max_messages = options['max_messages']
            # Resize caches if needed
            while len(self._messages) > self.max_messages:
                oldest_key = next(iter(self._messages))
                del self._messages[oldest_key]
                self._stats['evictions'] += 1

        if 'cache_users' in options:
            self.cache_users = options['cache_users']
            if not self.cache_users:
                self.clear_user_cache()

        if 'cache_threads' in options:
            self.cache_threads = options['cache_threads']
            if not self.cache_threads:
                self._threads.clear()