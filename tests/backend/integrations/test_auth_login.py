import json

import pytest
from fastapi.testclient import TestClient


@pytest.mark.asyncio
async def test_save_tokens_to_redis2(client: TestClient, create_test_users):
    user, _ = create_test_users

    form_data = {
        'username': user['login'],
        'password': user['password'],
    }

    response = client.post('/v1/auth/token', data=form_data)

    # successfully created status code
    assert response.status_code == 200
    data = response.json()

    # created correct user
    assert data['login'] == user['login']

    assert 'access_token' in data
