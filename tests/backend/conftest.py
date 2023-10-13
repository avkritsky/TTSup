from contextlib import asynccontextmanager
from typing import Generator

import pytest
from fastapi.testclient import TestClient

from src.backend.main import app
from src.backend.db.session import engine
from src.backend.db.models import User, Base


def rename_models():
    bases = Base.metadata.tables
    for key, val in bases.items():
        bases.pop(key)
        val.__tablename__ = f'test_{val.__tablename__}'
        bases[f'test_{key}'] = val


@asynccontextmanager
async def tables_for_test():
    rename_models()
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
        yield
        await connection.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope='function')
async def client() -> Generator[TestClient, None, None]:
    async with tables_for_test():
        client = TestClient(app)
        yield client
