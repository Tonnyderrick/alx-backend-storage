#!/usr/bin/env python3
"""
This module defines a Cache class for storing data in Redis.
It includes a method for storing data using a random key.
"""

import redis
import uuid
from typing import Union


class Cache:
    """
    Cache provides simple methods for interacting with Redis.
    """

    def __init__(self) -> None:
        """
        Initializes the Redis client and flushes the database.
        """
        self._redis = redis.Redis()
        self._redis.flushdb()

    def store(self, data: Union[str, bytes, int, float]) -> str:
        """
        Store data in Redis using a randomly generated key.

        Args:
            data (Union[str, bytes, int, float]): The data to store.

        Returns:
            str: The key under which the data is stored.
        """
        key = str(uuid.uuid4())
        self._redis.set(key, data)
        return key
