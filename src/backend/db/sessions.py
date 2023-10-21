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

    def __init__(
            self,
            url: str,
            base: Type[Base],
            *,
            echo: bool = True,
            autoflush: bool = False,
            expire_on_commit: bool = True,
    ):
        self.url = url
        self.echo = echo
        self.autoflush = autoflush
        self.expire_on_commit = expire_on_commit
        self.base = base
        self.engine = None
        self.maker = None
        self.engine = create_async_engine(self.url, echo=self.echo)

    async def get_engine(self):
        """Create new(!) engine. Use for tests"""
        return create_async_engine(self.url, echo=self.echo)

    async def new_session(self) -> Generator:
        """Function for FastAPI dependency injection"""
        async with AsyncSession(bind=self.engine) as session:
            session: AsyncSession
            yield session
            if not config.IS_PROD:
                await self.engine.dispose()

    async def create_tables(self):
        """Create all tables in Metadata"""
        async with self.engine.begin() as session:
            await session.run_sync(Base.metadata.create_all)


database = DBSession(url=config.POSTGRES_URL, base=Base)
