#!/usr/bin/env python3
"""
Module that defines the Cache class for storing data in Redis.
"""

import redis
import uuid
from typing import Union


class Cache:
    """
    Cache class that provides simple Redis-based data storage.
    """

    def __init__(self):
        """
        Initialize a Redis client and flush the database.
        """
        self._redis = redis.Redis()
        self._redis.flushdb()

    def store(self, data: Union[str, bytes, int, float]) -> str:
        """
        Store the given data in Redis using a random key.

        Args:
            data: The data to store. Can be str, bytes, int, or float.

        Returns:
            The key under which the data was stored (as a string).
        """
        key = str(uuid.uuid4())
        self._redis.set(key, data)
        return key
