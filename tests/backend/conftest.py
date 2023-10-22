from contextlib import asynccontextmanager
from typing import Generator

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.main import app
from src.backend.db.sessions import database
from src.backend.db.redis import sessions as redis_sess
from src.backend.db.models import Base, User
from src.backend.core import config, security


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


@pytest_asyncio.fixture()
async def client() -> TestClient:
    async with tables_for_test():
        app.dependency_overrides[database.new_session] = database.test_new_session
        client = TestClient(app)
        yield client


@pytest_asyncio.fixture()
async def redis() -> Generator[redis_sess.redis.Redis, None, None]:
    async for con in redis_sess.new_jwt_redis_session():
        yield con


@pytest_asyncio.fixture()
async def create_test_users() -> tuple:
    if config.IS_PROD is True:
        raise RuntimeError('TEST RUNE ON PROD ENV!!!')
    async for connection in database.test_new_session():
        connection: AsyncSession

        user_dict = {
            'login': 'user1',
            'group': 'user',
            'password': 'password',
        }

        support_dict = {
            'login': 'support1',
            'group': 'support',
            'password': 'password',
        }

        # create USER
        user = User()

        user.login = user_dict['login']
        user.password = security.get_encode_password(user_dict['password'])
        user.fullname = 'Mr.User'
        user.chat_id = '0'
        user.group = 'user'

        # CREATE SUPPORT
        support = User()

        support.login = support_dict['login']
        support.password = security.get_encode_password(support_dict['password'])
        support.fullname = 'Mr.Support'
        support.chat_id = '0'
        support.group = 'support'

        connection.add_all((user, support))

        await connection.commit()

        return user_dict, support_dict


@pytest.fixture()
def new_user() -> dict:
    new_user = {
        'login': 'test_user',
        'password': 'test_password',
        'chat_id': '0',
        'fullname': 'testovich',
    }
    return new_user

