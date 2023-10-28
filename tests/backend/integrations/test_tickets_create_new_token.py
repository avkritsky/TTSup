import json

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection

from src.backend.db.sessions import database
from src.backend.db.models import Ticket


@pytest.mark.asyncio
async def test_create_ticket (client: TestClient, new_ticket, user_token, create_test_users):
    user, _ = create_test_users
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
    assert data['author_login'] == user['login']

    # was returned new user ID
    assert 'id' in data


@pytest.mark.asyncio
async def test_error_create_ticket_for_user_with_active_ticket(client, new_ticket, create_test_users, user_token):
    response = client.post(
        '/v1/tickets',
        content=json.dumps(new_ticket),
        headers={
            'Authorization': f'Bearer {user_token}'
        }
    )

    assert response.status_code == 200

    response = client.post(
        '/v1/tickets',
        content=json.dumps(new_ticket),
        headers={
            'Authorization': f'Bearer {user_token}'
        }
    )

    # can't create ticket when user already have active ticket
    assert response.status_code == 425


@pytest.mark.asyncio
async def test_set_active_flag_and_state(client, new_ticket, create_test_users, user_token):
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

    engine = await database.get_engine()
    async with engine.begin() as conn:
        conn: AsyncConnection
        db_data_raw = await conn.execute(
            text(
                'select is_closed, state '
                f'from {Ticket.__tablename__} '
                f'where "id" = {data["id"]}'
            )
        )
        db_data = dict(next(db_data_raw.mappings()))

        # for user sets default group 'user'
        assert db_data['is_closed'] == False
        assert db_data['state'] == 'new'