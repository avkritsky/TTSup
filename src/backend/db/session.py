from typing import Generator

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
)
from src.backend.core import config


engine = create_async_engine(config.POSTGRES_URL)
session_maker = async_sessionmaker(
    bind=engine,
    autoflush=False,
    expire_on_commit=True,
)


async def new_session() -> Generator:
    """Function for FastAPI dependency injection"""
    async with session_maker() as session:
        yield session
