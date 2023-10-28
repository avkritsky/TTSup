from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from src.backend.db.models import Ticket, User


async def create_new_ticket(
        text: str,
        login: str,
        db: async_sessionmaker,
) -> dict:
    async with db() as session:
        session: AsyncSession
        if await _check_user_have_a_ticket(login, session):
            raise HTTPException(
                status_code=status.HTTP_425_TOO_EARLY,
                detail=f'User {login} already has active ticket!',
            )

        ticket = Ticket()

        ticket.text = text
        ticket.author_login = login

        session.add(ticket)
        await session.commit()
        await session.refresh(ticket)

        return ticket.created_json


async def _check_user_have_a_ticket(login: str, session: AsyncSession) -> bool:
    """Load user from DB by login. Return true if user HAS active ticket"""
    query = select(
        Ticket.id,
    ).where(
        Ticket.author_login == login,
        Ticket.is_closed == False,
    )

    data = await session.execute(query)

    return data.one_or_none() is not None


async def get_all(db: async_sessionmaker) -> list[dict]:
    """Return all active tickets"""
    query = select(
        Ticket
    ).where(
        Ticket.is_closed == False,
    ).order_by(
        Ticket.last_update
    )

    async with db() as session:
        session: AsyncSession
        data = await session.execute(query)

        items = [item.ticket_json for item in data.scalars()]

    return items


async def get(
        ticket_id: int | None,
        author_login: str | None,
        db: async_sessionmaker,
) -> list[dict]:
    """Return ticket by ID or author"""
    query = select(
        Ticket
    )

    if ticket_id is not None:
        query.where(
            Ticket.id == ticket_id,
        )
    elif author_login is not None:
        query.where(
            Ticket.author_login == author_login,
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail='No input data (ID or Author_login)',
        )

    query.order_by(Ticket.last_update)

    async with db() as session:
        session: AsyncSession
        data = await session.execute(query)

        items = [item.ticket_json for item in data.scalars()]

    return items


async def close(
        ticket_id: int,
        user: User,
        db: async_sessionmaker,
) -> None:
    """Close ticket by ID"""
    async with db() as session:
        session: AsyncSession

        ticket = await session.execute(
            select(Ticket).where(Ticket.id == ticket_id)
        )
        ticket = ticket.scalar()

        if ticket is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Ticket with id={ticket_id} not found',
            )

        if ticket.author_login != user.login and user.group != 'support':
            raise HTTPException(
                status_code=status.HTTP_406_NOT_ACCEPTABLE,
                detail="You can't close this ticket!",
            )

        ticket.close()

        await session.commit()

