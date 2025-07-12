#!/usr/bin/env python3
"""
Module that defines the Cache class for storing and retrieving data in Redis.
"""

import redis
import uuid
from typing import Union, Callable, Optional


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

    def get(self, key: str, fn: Optional[Callable] = None) -> Union[str, bytes, int, float, None]:
        """
        Retrieve data from Redis and optionally convert it using fn.

        Args:
            key: The Redis key to retrieve.
            fn: Optional callable to convert the data.

        Returns:
            The retrieved and converted data, or None if key does not exist.
        """
        data = self._redis.get(key)
        if data is None:
            return None
        return fn(data) if fn else data

    def get_str(self, key: str) -> Optional[str]:
        """
        Retrieve data from Redis and decode it as a UTF-8 string.

        Args:
            key: The Redis key to retrieve.

        Returns:
            The data as a UTF-8 string, or None if key does not exist.
        """
        return self.get(key, fn=lambda d: d.decode('utf-8'))

    def get_int(self, key: str) -> Optional[int]:
        """
        Retrieve data from Redis and convert it to an integer.

        Args:
            key: The Redis key to retrieve.

        Returns:
            The data as an integer, or None if key does not exist.
        """
        return self.get(key, fn=int)
