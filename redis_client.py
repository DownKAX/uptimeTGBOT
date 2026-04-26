import os
import redis
from redis.asyncio import Redis as AsyncRedis, ConnectionPool as AsyncConnectionPool

redis_host = os.getenv("REDIS_HOST", "localhost")

async def get_async_redis():
    async_pool = AsyncConnectionPool(host=redis_host, port=6379, db=0, decode_responses=True)
    return AsyncRedis(connection_pool=async_pool)

def get_sync_redis():
    sync_pool = redis.ConnectionPool(host=redis_host, port=6379, db=0, decode_responses=True)
    return redis.Redis(connection_pool=sync_pool)