#!/usr/bin/env python3
"""
Exercise file for Redis basics
"""
import redis
import uuid
from typing import Union, Callable, Optional
from functools import wraps


def count_calls(method: Callable) -> Callable:
    """
    Decorator to count the number of times a method is called
    """
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        key = method.__qualname__
        self._redis.incr(key)
        return method(self, *args, **kwargs)
    return wrapper


def call_history(method: Callable) -> Callable:
    """
    Decorator to store the history of inputs and outputs for a function
    """
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        input_key = f"{method.__qualname__}:inputs"
        output_key = f"{method.__qualname__}:outputs"
        
        # Store input arguments
        self._redis.rpush(input_key, str(args))
        
        # Execute method and store output
        result = method(self, *args, **kwargs)
        self._redis.rpush(output_key, str(result))
        
        return result
    return wrapper


class Cache:
    """
    Cache class interacting with Redis
    """
    def __init__(self):
        self._redis = redis.Redis()
        self._redis.flushdb()

    @call_history
    @count_calls
    def store(self, data: Union[str, bytes, int, float]) -> str:
        """
        Store data in Redis with a random key and return the key
        """
        key = str(uuid.uuid4())
        self._redis.set(key, data)
        return key

    def get(self, key: str, fn: Optional[Callable] = None) -> Union[str, bytes, int, float, None]:
        """
        Retrieve data from Redis and optionally convert it
        """
        data = self._redis.get(key)
        if fn and data:
            return fn(data)
        return data

    def get_str(self, key: str) -> Optional[str]:
        """
        Get value as string
        """
        return self.get(key, str)

    def get_int(self, key: str) -> Optional[int]:
        """
        Get value as integer
        """
        return self.get(key, int)
