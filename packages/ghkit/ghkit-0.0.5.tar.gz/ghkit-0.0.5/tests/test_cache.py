from unittest.mock import AsyncMock, MagicMock

import pytest

from ghkit.cache import AsyncRedisCache, MemoryCache, RedisCache


def test_memory_cache():
    """测试内存缓存"""
    cache = MemoryCache(cache_size=100)

    # 测试设置和获取
    cache.set("test_key", "test_value")
    assert cache.get("test_key") == "test_value"

    # 测试删除
    cache.delete("test_key")
    assert cache.get("test_key") is None

    # 测试过期时间
    cache.set("expire_key", "expire_value", ttl=1)
    assert cache.get("expire_key") == "expire_value"
    import time

    time.sleep(1.1)
    assert cache.get("expire_key") is None

    # 测试缓存大小限制
    for i in range(150):
        cache.set(f"key_{i}", f"value_{i}")
    assert len(cache._cache) <= 100


def test_redis_cache():
    """测试 Redis 缓存"""
    # 创建模拟的 Redis 客户端
    mock_redis = MagicMock()
    mock_redis.get.return_value = b"test_value"
    mock_redis.set.return_value = True
    mock_redis.delete.return_value = 1

    cache = RedisCache(mock_redis, prefix="test_cache")

    # 测试设置和获取
    cache.set("test_key", "test_value")
    mock_redis.set.assert_called_once_with("test_cache:test_key", "test_value", ex=None)

    assert cache.get("test_key") == b"test_value"
    mock_redis.get.assert_called_once_with("test_cache:test_key")

    # 测试删除
    cache.delete("test_key")
    mock_redis.delete.assert_called_once_with("test_cache:test_key")

    # 测试过期时间
    cache.set("expire_key", "expire_value", ttl=1)
    mock_redis.set.assert_called_with("test_cache:expire_key", "expire_value", ex=1)


@pytest.mark.asyncio
async def test_async_redis_cache():
    """测试异步 Redis 缓存"""
    # 创建模拟的异步 Redis 客户端
    mock_redis = AsyncMock()
    mock_redis.get.return_value = b"test_value"
    mock_redis.set.return_value = True
    mock_redis.delete.return_value = 1

    cache = AsyncRedisCache(mock_redis, prefix="test_async_cache")

    # 测试设置和获取
    await cache.set("test_key", "test_value")
    mock_redis.set.assert_called_once_with("test_async_cache:test_key", "test_value", ex=None)

    assert await cache.get("test_key") == b"test_value"
    mock_redis.get.assert_called_once_with("test_async_cache:test_key")

    # 测试删除
    await cache.delete("test_key")
    mock_redis.delete.assert_called_once_with("test_async_cache:test_key")

    # 测试过期时间
    await cache.set("expire_key", "expire_value", ttl=1)
    mock_redis.set.assert_called_with("test_async_cache:expire_key", "expire_value", ex=1)
