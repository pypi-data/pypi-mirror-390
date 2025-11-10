from functools import wraps

from .base import Cache
from .memory_cache import MemoryCache
from .redis_cache import AsyncRedisCache, RedisCache

__all__ = ["Cache", "MemoryCache", "RedisCache", "AsyncRedisCache", "cacheout"]


def cacheout(cache: Cache, ttl=None, key_name=None):
    def _cacheout(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return cache(ttl=ttl, key_name=key_name)(func)(*args, **kwargs)

        return wrapper

    return _cacheout
