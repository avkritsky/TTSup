import json

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection

from src.backend.db.session import database


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

        # successfully created status code
        assert response.status_code == 200
        data = response.json()

        # created correct user
        assert data['login'] == new_user['login']

        # was returned new user ID
        assert 'id' in data

        engine = await database.get_engine()
        async with engine.begin() as conn:
            conn: AsyncConnection
            db_data = await conn.execute(
                text(
                    f'select "group" from user_test where "id" = {data["id"]}'
                )
            )
            db_data = db_data.mappings().first()

            # for user sets default group 'user'
            assert dict(db_data)['group'] == 'user'
