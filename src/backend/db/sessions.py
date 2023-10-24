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
            echo: bool = False,
            autoflush: bool = False,
            expire_on_commit: bool = True,
    ):
        self.url = url
        self.echo = echo
        self.autoflush = autoflush
        self.expire_on_commit = expire_on_commit
        self.base = base
        self.engine = None
        self.engine = create_async_engine(self.url, echo=self.echo)
        self.maker = async_sessionmaker(bind=self.engine)

    async def get_engine(self):
        """Create new(!) engine. Use for tests"""
        return create_async_engine(self.url, echo=self.echo)

    async def new_session(self) -> Generator[AsyncSession, None, None]:
        """Function for FastAPI dependency injection"""
        async with AsyncSession(bind=self.engine) as session:
            session: AsyncSession
            yield session

    async def new_sess_maker(self) -> Generator[AsyncSession, None, None]:
        """Function for FastAPI dependency injection"""
        async with AsyncSession(bind=self.engine) as session:
            session: AsyncSession
            yield session

    async def test_new_session(self) -> Generator[AsyncSession, None, None]:
        """Function for overriding `new_session` dependency"""
        engine = create_async_engine(self.url, echo=self.echo)

        # when tests with one engine, I got Runtime errors . Find in SO answer
        # for same problem:
        # This happens because the asyncio event loop when using pytest-asyncio
        # is created anew for each test execution and the client caches
        # the first event loop it finds within each AIOHttpNode instance.
        # To work-around this you'll need to create a new instance of
        # AsyncElasticsearch for each test execution rather than using a
        # single global instance. Hope this helps!

        async with AsyncSession(bind=engine) as session:
            session: AsyncSession

            yield session

        await self.engine.dispose()

    async def test_new_sess_maker(self) -> Generator[AsyncSession, None, None]:
        """Function for overriding `new_sess_maker` dependency"""
        engine = create_async_engine(self.url, echo=self.echo)

        # when tests with one engine, I got Runtime errors . Find in SO answer
        # for same problem:
        # This happens because the asyncio event loop when using pytest-asyncio
        # is created anew for each test execution and the client caches
        # the first event loop it finds within each AIOHttpNode instance.
        # To work-around this you'll need to create a new instance of
        # AsyncElasticsearch for each test execution rather than using a
        # single global instance. Hope this helps!

        maker = async_sessionmaker(bind=engine)

        yield maker

        await self.engine.dispose()

    async def create_tables(self):
        """Create all tables in Metadata"""
        async with self.engine.begin() as session:
            await session.run_sync(Base.metadata.create_all)


database = DBSession(url=config.POSTGRES_URL, base=Base)
