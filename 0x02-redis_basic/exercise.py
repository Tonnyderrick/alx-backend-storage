#!/usr/bin/env python3
"""
This module defines the Cache class that provides simple
methods for storing data in a Redis database.
"""

import redis
import uuid
from typing import Union


class Cache:
    """
    Cache class for storing arbitrary data in Redis using random keys.
    """

    def __init__(self) -> None:
        """
        Initialize a Redis client instance and flush existing data.
        """
        self._redis = redis.Redis()
        self._redis.flushdb()

    def store(self, data: Union[str, bytes, int, float]) -> str:
        """
        Store the given data in Redis and return the generated key.

        Args:
            data: The data to be stored (str, bytes, int, or float)

        Returns:
            A string representing the key under which the data was stored.
        """
        key = str(uuid.uuid4())
        self._redis.set(key, data)
        return key
