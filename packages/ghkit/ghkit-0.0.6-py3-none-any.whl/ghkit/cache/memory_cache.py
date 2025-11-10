import time
from collections import OrderedDict

from .base import Cache


class MemoryCache(Cache):
    def __init__(self, cache_size=1000):
        self._cache = OrderedDict()
        self._cache_size = cache_size

    def get(self, key):
        if self.is_expired(key):
            self.delete(key)
            return None
        return self._cache.get(key, {}).get("value", None)

    def set(self, key, value, ttl=None):
        if len(self._cache) >= self._cache_size:
            self._cache.popitem(last=False)
        self._cache[key] = {"value": value, "ttl": time.time() + ttl if ttl else None}

    def delete(self, key):
        self._cache.pop(key, None)

    def is_expired(self, key):
        if key in self._cache:
            if ttl := self._cache[key]["ttl"]:
                return time.time() > ttl
        return False
