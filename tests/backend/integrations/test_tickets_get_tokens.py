import json

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection

from src.backend.db.sessions import database
from src.backend.db.models import Ticket


@pytest.mark.asyncio
async def test_get_all_tickets(client: TestClient, new_ticket, user_token, create_test_users):
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

    response = client.get(
        '/v1/tickets',
        headers={
            'Authorization': f'Bearer {user_token}'
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data['items']) == 1

    item = data['items'][0]

    assert item['text'] == new_ticket['text']


@pytest.mark.asyncio
async def test_get_ticket_by_id(client: TestClient, new_ticket, user_token, create_test_users):
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

    response = client.get(
        '/v1/tickets',
        params={
            'ticket_id': 1,
        },
        headers={
            'Authorization': f'Bearer {user_token}'
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data['items']) == 1

    item = data['items'][0]

    assert item['id'] == 1


@pytest.mark.asyncio
async def test_get_ticket_by_login(client: TestClient, new_ticket, user_token, create_test_users):
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

    response = client.get(
        '/v1/tickets',
        params={
            'author_login': user['login'],
        },
        headers={
            'Authorization': f'Bearer {user_token}'
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data['items']) == 1

    item = data['items'][0]

    assert item['author_login'] == user['login']



