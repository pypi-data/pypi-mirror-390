import redis
from redis import asyncio as aioredis


class RedisClient(redis.Redis):
    """同步的客户端"""

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        password: str = None,
        decode_responses=True,
        health_check_interval=10,
        socket_connect_timeout=5,
        retry_on_timeout=True,
        socket_keepalive=True,
        **kwargs,
    ):
        super().__init__(
            host=host,
            port=port,
            db=db,
            password=password,
            decode_responses=decode_responses,
            health_check_interval=health_check_interval,
            socket_connect_timeout=socket_connect_timeout,
            retry_on_timeout=retry_on_timeout,
            socket_keepalive=socket_keepalive,
            **kwargs,
        )


class AsyncRedisClient(aioredis.Redis):
    """异步的客户端"""

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        password: str = None,
        decode_responses=True,
        health_check_interval=10,
        socket_connect_timeout=5,
        retry_on_timeout=True,
        socket_keepalive=True,
        **kwargs,
    ):
        super().__init__(
            host=host,
            port=port,
            db=db,
            password=password,
            decode_responses=decode_responses,
            health_check_interval=health_check_interval,
            socket_connect_timeout=socket_connect_timeout,
            retry_on_timeout=retry_on_timeout,
            socket_keepalive=socket_keepalive,
            **kwargs,
        )
