import json

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection

from src.backend.db.sessions import database


@pytest.mark.asyncio
async def test_create_user(client):
    new_user = {
        'login': 'test_user',
        'password': 'test_password',
        'chat_id': '0',
        'fullname': 'testovich',
    }

    async for app in client:
        response = app.post('/v1/auth/register', content=json.dumps(new_user))

        # successfully created status code
        assert response.status_code == 200
        data = response.json()

        # created correct user
        assert data['login'] == new_user['login']

        # was returned new user ID
        assert 'id' in data


@pytest.mark.asyncio
async def test_set_default_user_group(client):
    new_user = {
        'login': 'test_user',
        'password': 'test_password',
        'chat_id': '0',
        'fullname': 'testovich',
    }

    async for app in client:
        response = app.post('/v1/auth/register', content=json.dumps(new_user))

        # successfully created status code
        assert response.status_code == 200
        data = response.json()

        engine = await database.get_engine()
        async with engine.begin() as conn:
            conn: AsyncConnection
            db_data = await conn.execute(
                text(
                    f'select "group" from user_test where "id" = {data["id"]}'
                )
            )
            user_group = db_data.scalar()
            # for user sets default group 'user'
            assert user_group == 'user'


@pytest.mark.asyncio
async def test_error_create_user_with_same_login(client):
    new_user = {
        'login': 'test_user',
        'password': 'test_password',
        'chat_id': '0',
        'fullname': 'testovich',
    }

    async for app in client:
        response = app.post('/v1/auth/register', content=json.dumps(new_user))

        assert response.status_code == 200

        response = app.post('/v1/auth/register', content=json.dumps(new_user))

        # can't create user with same login
        assert response.status_code == 409


@pytest.mark.asyncio
async def test_save_tokens_to_redis(client, redis):
    new_user = {
        'login': 'test_user',
        'password': 'test_password',
        'chat_id': '0',
        'fullname': 'testovich',
    }

    async for app in client:
        response = app.post('/v1/auth/register', content=json.dumps(new_user))

        # successfully created status code
        assert response.status_code == 200
        data = response.json()

        # created correct user
        assert data['login'] == new_user['login']

        token = data['access_token']

        async for con in redis:
            redis_data = await con.get(new_user['login'])

            redis_tokens = json.loads(redis_data)


            assert redis_tokens['access_token'] == 'sasa'
