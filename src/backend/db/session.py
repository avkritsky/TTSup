from typing import Generator, Type

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
    AsyncEngine,
)
from src.backend.core import config
from src.backend.db.models import Base


class DBSession:
    url: str
    echo: bool
    autoflush: bool
    expire_on_commit: bool
    base: Type[Base]
    engine: AsyncEngine | None
    maker: async_sessionmaker | None
    _instance = None

    def __init__(
            self,
            url: str,
            base: Type[Base],
            *,
            echo: bool = True,
            autoflush: bool = False,
            expire_on_commit: bool = False,
    ):
        self.url = url
        self.echo = echo
        self.autoflush = autoflush
        self.expire_on_commit = expire_on_commit
        self.base = base
        self.engine = None
        self.maker = None

    async def create_connection(self):
        self.engine = create_async_engine(self.url, echo=self.echo)
        self.maker = async_sessionmaker(
            bind=self.engine,
            autoflush=self.autoflush,
            expire_on_commit=self.expire_on_commit,
        )

    async def get_engine(self):
        return create_async_engine(self.url, echo=self.echo)

    async def new_session(self) -> Generator:
        """Function for FastAPI dependency injection"""
        if self.maker is None:
            await self.create_connection()
        async with self.maker() as session:
            session: AsyncSession
            yield session

    async def create_tables(self):
        async with self.engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)


database = DBSession(url=config.POSTGRES_URL, base=Base)