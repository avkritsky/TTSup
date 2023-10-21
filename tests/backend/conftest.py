from contextlib import asynccontextmanager
from typing import Generator

import pytest
from fastapi.testclient import TestClient

from src.backend.main import app
from src.backend.db.sessions import database
from src.backend.db.redis import sessions as redis_sess
from src.backend.db.models import Base
from src.backend.core import config


@asynccontextmanager
async def tables_for_test():
    engine = await database.get_engine()
    if config.IS_PROD is True:
        raise RuntimeError('TEST RUNE ON PROD ENV!!!')
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
        await connection.run_sync(Base.metadata.create_all)
        await connection.commit()

    yield

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)


@pytest.fixture()
async def client() -> Generator[TestClient, None, None]:
    async with tables_for_test():
        client = TestClient(app)
        yield client


@pytest.fixture()
async def redis() -> Generator[redis_sess.redis.Redis, None, None]:
    async for con in redis_sess.new_jwt_redis_session():
        yield con
