from datetime import datetime

import pytest
from fastapi import HTTPException

from src.backend.core import security
from src.backend.db.models import User


class FakeSession:
    _items: list
    _data: dict

    def __init__(self, items: list | None = None, data: dict | None = None):
        self._items = items or []
        self._data = data or {}

    async def scalar(self, *args, **kwargs):
        return self._items.pop(0)

    async def get(self, key):
        return self._data.get(key)

# 50, 116-117, 134-135, 226-250

@pytest.mark.asyncio
async def test_authenticate_user_no_user_in_db():
    session = FakeSession([None])

    with pytest.raises(HTTPException) as excinfo:
        await security.authenticate_user('login', 'password', session)

    assert 'login' in str(excinfo)


@pytest.mark.asyncio
async def test_authenticate_user_bad_password():
    user = User()
    user.password = security.get_encode_password('pswd')
    session = FakeSession([user])

    with pytest.raises(HTTPException) as excinfo:
        await security.authenticate_user('login', 'password', session)

    assert 'password' in str(excinfo)


@pytest.mark.asyncio
async def test_authenticate_user():
    user = User()
    user.password = security.get_encode_password('password')
    session = FakeSession([user])

    res = await security.authenticate_user('login', 'password', session)

    assert user == res


def test_create_token_with_int_ttl():
    token = security.create_token('login', 'password', 60)

    data = security.decode_token(token)

    assert data['exp'] > datetime.utcnow().timestamp()


@pytest.mark.asyncio
async def test_load_token_from_redis_with_invalid_token():
    session = FakeSession()

    data = {'fake': 'login'}

    with pytest.raises(HTTPException) as excinfo:
        await security.load_token_from_redis(data, session)

    assert 'token' in str(excinfo)


def test_is_token_valid_error():
    token = ''
    data = {'fake': 'login'}

    with pytest.raises(HTTPException) as excinfo:
        security.is_token_valid(token, data)

    assert 'token' in str(excinfo)

