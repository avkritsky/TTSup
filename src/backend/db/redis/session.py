from typing import Generator

import redis.asyncio as redis

from src.backend.core import config


async def new_jwt_redis_session() -> Generator[redis.Redis, None, None]:
    """Create new connect to redis for JWT shelter (for FastAPI DI)"""
    r = redis.Redis(
        host='127.0.0.1',
        port=6379,
        db=config.REDIS_DB_FOR_JWT,
        password=config.REDIS_PASSWORD,
    )

    yield r

    await r.close()
