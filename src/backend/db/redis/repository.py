import json
from datetime import timedelta

from redis.asyncio import Redis


async def set_item(key: str, val: dict, ttl: timedelta | int, session: Redis):
    """Set VAL in redis by KEY"""
    await session.set(
        name=key,
        value=json.dumps(val, default=str),
        ex=ttl,
    )


async def get_item(key: str, session: Redis) -> dict | None:
    """Get and return VAL from redis by KEY"""
    val = await session.get(key)

    if val is not None:
        val = json.loads(val)

    return val
