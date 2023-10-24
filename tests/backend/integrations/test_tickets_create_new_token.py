import json

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection

from src.backend.db.sessions import database


@pytest.mark.asyncio
async def test_create_user(client: TestClient, new_ticket, user_token, create_test_users):
    response = client.post(
        '/v1/tickets',
        content=json.dumps(new_ticket),
        headers={
            'Authorization': f'Bearer {user_token}'
        }
    )

    # successfully created status code
    assert response.status_code == 200
    data = response.json()

    # created correct user
    assert data['author_login'] == new_ticket['login']

    # was returned new user ID
    assert 'id' in data


@pytest.mark.asyncio
async def test_error_create_ticket_for_user_with_active_ticket(client, new_ticket, create_test_users):
    response = client.post('/v1/tickets', content=json.dumps(new_ticket))

    assert response.status_code == 200

    response = client.post('/v1/tickets', content=json.dumps(new_ticket))

    # can't create ticket when user already have active ticket
    assert response.status_code == 425


@pytest.mark.asyncio
async def test_set_active_flag_and_state(client, new_ticket, create_test_users):
    response = client.post('/v1/tickets', content=json.dumps(new_ticket))

    # successfully created status code
    assert response.status_code == 200
    data = response.json()

    engine = await database.get_engine()
    async with engine.begin() as conn:
        conn: AsyncConnection
        db_data_raw = await conn.execute(
            text(
                f'select "is_closed", "state" from tickets_test where "id" = {data["id"]}'
            )
        )
        db_data = db_data_raw.scalar()
        flag, state = db_data
        # for user sets default group 'user'
        assert flag == False
        assert state == 'new'