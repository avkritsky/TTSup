import json

import pytest


@pytest.mark.asyncio
async def test_create_user(client):
    new_user = {
        'login': 'test_user',
        'password': 'test_password',
        'chat_id': '0',
        'fullname': 'testovich',
    }

    async for app in client:
        response = app.post('/v1/auth', content=json.dumps(new_user))

        assert response.status_code == 200
        data = response.json()
        assert data['login'] == new_user['login']
        assert 'id' in data
