import json

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection

from src.backend.db.sessions import database
from src.backend.db.models import Ticket


@pytest.mark.asyncio
async def test_close_ticket(client: TestClient, new_ticket, user_token, create_test_users):
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

    response = client.patch(
        '/v1/tickets/close',
        params={
            'ticket_id': 1,
        },
        headers={
            'Authorization': f'Bearer {user_token}'
        }
    )

    assert response.status_code == 200

    engine = await database.get_engine()
    async with engine.begin() as conn:
        conn: AsyncConnection
        db_data_raw = await conn.execute(
            text(
                'select is_closed, state '
                f'from {Ticket.__tablename__} '
                f'where "id" = 1'
            )
        )
        db_data = dict(next(db_data_raw.mappings()))

        # for user sets default group 'user'
        assert db_data['is_closed'] == True
        assert db_data['state'] == 'closed'
