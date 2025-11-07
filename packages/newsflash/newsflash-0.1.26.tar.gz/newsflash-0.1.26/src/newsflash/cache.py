from typing import Callable
from django.core.cache import cache
from functools import wraps
import json
import hashlib


def cache_result(timeout: int = 60 * 60 * 24):
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            key = (
                f"{func.__module__}.{func.__name__}:"
                + hashlib.sha256(
                    json.dumps({"args": args, "kwargs": kwargs}).encode()
                ).hexdigest()
            )

            if (result := cache.get(key)) is not None:
                return result

            result = func(*args, **kwargs)
            cache.set(key, result, timeout)
            return result

        return wrapper

    return decorator
