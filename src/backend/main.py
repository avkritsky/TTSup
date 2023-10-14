from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.backend.apis import root_api
from src.backend.core import config
from src.backend.db.session import database


@asynccontextmanager
async def lifespan(api: FastAPI):
    print('Start APP')
    await database.create_connection()
    await database.create_tables()
    yield
    print('Exit APP')


def create_app() -> FastAPI:
    # create APP
    new_app = FastAPI(
        lifespan=lifespan,
        description=config.PROJECT_DESCRIPTION,
        version=config.PROJECT_VERSION,
        title=config.PROJECT_TITLE,
    )
    # include routes
    new_app.include_router(root_api.router)
    return new_app


app = create_app()

@app.get('/healthy')
def health_check():
    return {'healthy': True}
