#!/usr/bin/env python3
"""
This module defines the Cache class for storing and retrieving
data from a Redis database. It also tracks method calls and
stores the history of inputs and outputs.
"""

import redis
import uuid
from functools import wraps
from typing import Union, Callable, Optional


def count_calls(method: Callable) -> Callable:
    """
    Decorator that counts how many times a method is called.

    Stores the count in Redis using INCR on the method's qualified name.
    """
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        """Wrapper that increments call count in Redis."""
        self._redis.incr(method.__qualname__)
        return method(self, *args, **kwargs)
    return wrapper


def call_history(method: Callable) -> Callable:
    """
    Decorator that stores the history of inputs and outputs for a method.

    Uses RPUSH to append serialized inputs and outputs into Redis lists.
    """
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        """Wrapper that records inputs and outputs of a method."""
        input_key = method.__qualname__ + ":inputs"
        output_key = method.__qualname__ + ":outputs"

        self._redis.rpush(input_key, str(args))
        result = method(self, *args, **kwargs)
        self._redis.rpush(output_key, str(result))
        return result
    return wrapper


def replay(method: Callable) -> None:
    """
    Display the history of calls of a particular function.

    It prints the number of times the function was called,
    and its inputs and corresponding outputs.
    """
    redis_instance = method.__self__._redis
    method_name = method.__qualname__

    inputs = redis_instance.lrange(f"{method_name}:inputs", 0, -1)
    outputs = redis_instance.lrange(f"{method_name}:outputs", 0, -1)

    print(f"{method_name} was called {len(inputs)} times:")

    for inp, out in zip(inputs, outputs):
        print(f"{method_name}(*{inp.decode('utf-8')}) -> {out.decode('utf-8')}")


class Cache:
    """
    Cache class to interface with Redis for data storage.
    """

    def __init__(self):
        """
        Initialize the Cache instance and flush any existing Redis data.
        """
        self._redis = redis.Redis()
        self._redis.flushdb()

    @call_history
    @count_calls
    def store(self, data: Union[str, bytes, int, float]) -> str:
        """
        Store the given data in Redis with a generated UUID key.

        Args:
            data: The value to store (str, bytes, int, or float)

        Returns:
            A string representing the generated Redis key
        """
        key = str(uuid.uuid4())
        self._redis.set(key, data)
        return key

    def get(self, key: str, fn: Optional[Callable] = None) -> Union[str, bytes, int, float, None]:
        """
        Retrieve data from Redis and optionally convert it with a function.

        Args:
            key: Redis key to retrieve
            fn: Optional function to apply to the result

        Returns:
            Retrieved and optionally transformed data
        """
        data = self._redis.get(key)
        if data is None:
            return None
        return fn(data) if fn else data

    def get_str(self, key: str) -> Optional[str]:
        """
        Retrieve data as a UTF-8 decoded string.

        Args:
            key: Redis key to retrieve

        Returns:
            String version of the data or None
        """
        return self.get(key, fn=lambda d: d.decode('utf-8'))

    def get_int(self, key: str) -> Optional[int]:
        """
        Retrieve data and convert it to an integer.

        Args:
            key: Redis key to retrieve

        Returns:
            Integer value or None
        """
        return self.get(key, fn=int)
