from .base import Cache


class RedisCache(Cache):
    def __init__(self, redis, prefix="redis_cache"):
        for method in ("get", "set", "delete"):
            assert hasattr(redis, method), f"redis client must have method {method}"
        self.redis = redis
        self.prefix = prefix

    def key_name(self, key):
        return f"{self.prefix}:{key}"

    def get(self, key):
        return self.redis.get(self.key_name(key))

    def set(self, key, value, ttl=None):
        self.redis.set(self.key_name(key), value, ex=ttl)

    def delete(self, key):
        self.redis.delete(self.key_name(key))


class AsyncRedisCache(Cache):
    def __init__(self, redis, prefix="redis_cache"):
        for method in ("get", "set", "delete"):
            assert hasattr(redis, method), f"redis client must have method {method}"
        self._redis = redis
        self._prefix = prefix

    def key_name(self, key):
        return f"{self._prefix}:{key}"

    async def get(self, key):
        return await self._redis.get(self.key_name(key))

    async def set(self, key, value, ttl=None):
        await self._redis.set(self.key_name(key), value, ex=ttl)

    async def delete(self, key):
        await self._redis.delete(self.key_name(key))
