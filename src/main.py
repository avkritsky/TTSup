from fastapi import FastAPI
from src.core import config


async def lifespan(api: FastAPI):
    print('Start APP')
    yield
    print('Exit APP')


def create_app() -> FastAPI:
    new_app = FastAPI(
        lifespan=lifespan,
        description=config.PROJECT_DESCRIPTION,
        version=config.PROJECT_VERSION,
        title=config.PROJECT_TITLE,
    )
    return new_app


app = create_app()
