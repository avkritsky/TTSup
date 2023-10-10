from fastapi import FastAPI


async def lifespan():
    print('Start APP')
    yield
    print('Exit APP')


def create_app() -> FastAPI:
    new_app = FastAPI(
        lifespan=lifespan,
    )
    return new_app
