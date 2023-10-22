import asyncio
import json
from datetime import timedelta

import pytest
from fastapi.testclient import TestClient

from src.backend.core.security import create_token


@pytest.mark.asyncio
async def test_refresh_user_tokens(client: TestClient, create_test_users, redis):
    user, _ = create_test_users

    form_data = {
        'username': user['login'],
        'password': user['password'],
    }

    response = client.post('/v1/auth/token', data=form_data)

    # successfully created status code
    assert response.status_code == 200
    data = response.json()

    user_refresh = data['refresh_token']
    user_access = data['access_token']

    await asyncio.sleep(1)

    response = client.get(
        '/v1/auth/refresh',
        params={'refresh_token': user_refresh},
    )

    assert response.status_code == 200

    data = response.json()

    assert user['login'] == data['login']
    assert user_access != data['access_token']
    assert user_refresh != data['refresh_token']

    redis_data = json.loads(
        await redis.get(user['login']),
    )

    redis_refresh_token = redis_data['refresh_token']

    assert redis_refresh_token == data['refresh_token']


@pytest.mark.asyncio
async def test_refresh_with_expired_token(client: TestClient, create_test_users):
    user, _ = create_test_users

    user_refresh = create_token(
        login=user['login'],
        group=user['group'],
        ttl=-timedelta(hours=1)
    )

    response = client.get(
        '/v1/auth/refresh',
        params={'refresh_token': user_refresh},
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_refresh_redis_not_valid(client: TestClient, create_test_users, redis):
    user, _ = create_test_users

    form_data = {
        'username': user['login'],
        'password': user['password'],
    }

    response = client.post('/v1/auth/token', data=form_data)

    # successfully created status code
    assert response.status_code == 200
    data = response.json()

    user_refresh = data['refresh_token']

    raw_data = await redis.get(user['login'])

    saved_data = json.loads(raw_data)

    saved_data['refresh_token'] = 'wrong'

    await redis.set(user['login'], json.dumps(saved_data))

    response = client.get(
        '/v1/auth/refresh',
        params={'refresh_token': user_refresh},
    )

    assert response.status_code == 401
