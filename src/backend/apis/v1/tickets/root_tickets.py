from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.backend.core.security import get_current_user
from src.backend.db.models import User
from src.backend.db.repository import tickets
from src.backend.db.sessions import database
from src.backend.schemas import schemas_tickets

router = APIRouter(
    prefix='/tickets',
    tags=[
        'tickets',
    ],
    dependencies=(
        Depends(get_current_user),
    )
)


@router.post(
    '',
    response_model=schemas_tickets.NewTicketResponse,
    responses={
        '425': {
            'description': 'User already has active ticket!',
        },
    },
)
async def create_new_ticket(
        source: schemas_tickets.NewTicketRequest,
        user: User = Depends(get_current_user),
        db: async_sessionmaker = Depends(database.new_sess_maker),
):
    """Create new ticket with TXT for user"""

    ticket = await tickets.create_new_ticket(
        text=source.text,
        login=user.login,
        db=db,
    )

    return ticket


@router.get(
    '',
    response_model=schemas_tickets.GetTicketsResponse,
)
async def get_active_tickets(
        ticket_id: int | None = None,
        author_login: str | None = None,
        db: async_sessionmaker = Depends(database.new_sess_maker),
):
    """Get all active tickets"""
    if ticket_id is None:
        items = await tickets.get_all(
            db=db,
        )
    elif ticket_id is not None or author_login is not None:
        items = await tickets.get(
            ticket_id,
            author_login,
            db,
        )
    else:
        items = []

    return JSONResponse(
        content={'items': items},
    )
