#!/usr/bin/env python3
"""Redis exercise module"""
import redis
import uuid
from typing import Union, Callable, Optional
from functools import wraps


def count_calls(method: Callable) -> Callable:
    """Decorator to count number of calls to a method."""
    key = method.__qualname__

    @wraps(method)
    def wrapper(self, *args, **kwargs):
        self._redis.incr(key)
        return method(self, *args, **kwargs)
    return wrapper


def call_history(method: Callable) -> Callable:
    """Decorator to store the history of inputs and outputs for a function."""
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        input_key = method.__qualname__ + ":inputs"
        output_key = method.__qualname__ + ":outputs"

        self._redis.rpush(input_key, str(args))
        result = method(self, *args, **kwargs)
        self._redis.rpush(output_key, str(result))

        return result
    return wrapper


def replay(method: Callable) -> None:
    """Display the history of calls of a function."""
    redis = method.__self__._redis
    method_name = method.__qualname__
    inputs = redis.lrange(f"{method_name}:inputs", 0, -1)
    outputs = redis.lrange(f"{method_name}:outputs", 0, -1)

    print(f"{method_name} was called {len(inputs)} times:")
    for input_data, output_data in zip(inputs, outputs):
        input_str = input_data.decode("utf-8")
        output_str = output_data.decode("utf-8")
        print(f"{method_name}(*({input_str},)) -> {output_str}")


class Cache:
    """Cache class that stores data in Redis."""

    def __init__(self):
        """Initialize Redis connection and flush data."""
        self._redis = redis.Redis()
        self._redis.flushdb()

    @call_history
    @count_calls
    def store(self, data: Union[str, bytes, int, float]) -> str:
        """Store data and return the generated key."""
        key = str(uuid.uuid4())
        self._redis.set(key, data)
        return key

    def get(self, key: str, fn: Optional[Callable] = None) -> Union[
            str, bytes, int, float, None]:
        """Retrieve data and optionally convert it."""
        value = self._redis.get(key)
        if value is not None and fn is not None:
            return fn(value)
        return value

    def get_str(self, key: str) -> str:
        """Retrieve a string from Redis."""
        return self.get(key, str)

    def get_int(self, key: str) -> int:
        """Retrieve an integer from Redis."""
        return self.get(key, int)
