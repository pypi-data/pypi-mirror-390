

import asyncio
from functools import wraps


def cache(namespace=None, ttl=None, key=None):
    def _wrapper_factory(func):
        if asyncio.iscoroutinefunction(func):
            @wraps(func)
            async def async_wrapper_func(*args, **kwargs):
                return await func(*args, **kwargs)
            return async_wrapper_func
        else:
            @wraps(func)
            def sync_wrapper_func(*args, **kwargs):
                return func(*args, **kwargs)
            return sync_wrapper_func
    return _wrapper_factory
