from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from src.backend.db.models import Ticket


async def create_new_ticket(
        text: str,
        login: str,
        db: async_sessionmaker,
) -> dict:
    async with db() as session:
        if await check_user_have_a_ticket(login, session):
            raise HTTPException(
                status_code=status.HTTP_425_TOO_EARLY,
                detail=f'User {login} already has active ticket!',
            )

        ticket = Ticket()

        ticket.text = text

        await session.commit()
        await session.refresh(ticket)

        return ticket.jwt_model


async def check_user_have_a_ticket(login: str, session: AsyncSession) -> bool:
    """Load user from DB by login. Return true if user HAS active ticket"""
    query = select(
        Ticket.id,
    ).where(
        Ticket.author_login == login,
        Ticket.is_closed == False,
    )

    data = await session.execute(query)

    return data.one_or_none() is not None
