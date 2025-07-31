#!/usr/bin/env python3
"""Redis-based cache system"""

import redis
import uuid
from typing import Union, Callable, Optional
from functools import wraps


def count_calls(method: Callable) -> Callable:
    """Decorator that counts the number of times a method is called."""
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        # Use the qualified name as key
        key = method.__qualname__
        self._redis.incr(key)  # Increment the call count
        return method(self, *args, **kwargs)

    return wrapper


class Cache:
    """Cache class for storing and retrieving values in Redis."""

    def __init__(self):
        self._redis = redis.Redis()
        self._redis.flushdb()

    @count_calls
    def store(self, data: Union[str, bytes, int, float]) -> str:
        """Generate a random key and store the data with that key."""
        key = str(uuid.uuid4())
        self._redis.set(key, data)
        return key

    def get(self, key: str, fn: Optional[Callable] = None) -> Union[str, bytes, int, None]:
        """Retrieve data from Redis, optionally applying a conversion function."""
        value = self._redis.get(key)
        if value is None:
            return None
        if fn is not None:
            return fn(value)
        return value

    def get_str(self, key: str) -> str:
        """Retrieve a UTF-8 string from Redis."""
        return self.get(key, lambda d: d.decode("utf-8"))

    def get_int(self, key: str) -> int:
        """Retrieve an int from Redis."""
        return self.get(key, int)
