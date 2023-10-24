from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from src.backend.core import security
from src.backend.db.models import User
from src.backend.schemas import schemas_auth


async def create_new_user(
        source: schemas_auth.NewUserRequest,
        db: AsyncSession,
) -> dict:
    user = User()

    user.login = source.login
    user.fullname = source.fullname
    user.chat_id = source.chat_id

    # hash password
    user.password = security.get_encode_password(source.password)

    # set default group
    user.group = 'user'

    try:
        db.add(user)
        await db.commit()
    except IntegrityError:
        # catch error from asyncpg, its mean that User's table checks fault
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={'error': 'Login already used', 'login': source.login},
        )
    await db.refresh(user)

    return user.jwt_model


async def get_user_by_login(login: str, session: AsyncSession) -> User:
    """Load user from DB by login"""
    query = select(
        User
    ).where(
        User.login == login,
    )

    data = await session.scalar(query)

    return data
