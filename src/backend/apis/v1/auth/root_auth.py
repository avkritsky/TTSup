from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.db import sessions, repository
from src.backend.db import redis, models
from src.backend.schemas import schemas_auth
from src.backend.core import security


router = APIRouter(
    prefix='/auth',
    tags=[
        'auth',
    ],
)


@router.post(
    '/register',
    response_model=schemas_auth.NewUserResult,
    responses={
        '409': {
            'description': 'Login already used (may be)',
            'model': schemas_auth.ErrorNewUser,
        },
    }
)
async def create_user(
        source: schemas_auth.NewUser,
        session: AsyncSession = Depends(sessions.database.new_session),
        redis_sess: Redis = Depends(redis.sessions.new_jwt_redis_session),
):
    res = await repository.users.create_new_user(source, session)

    access_token, refresh_token = await security.get_new_tokens(
        decoded_token=res.model_dump(),
        session=redis_sess,
    )

    response = JSONResponse(
        status_code=status.HTTP_200_OK,
        content=res.model_dump(),
    )

    security.set_tokens_in_response(response, access_token, refresh_token)

    return res


@router.post(
    '/token',
)
async def login_user(
        form_data: OAuth2PasswordRequestForm = Depends(),
        session: AsyncSession = Depends(sessions.database.new_session),
):
    ...


@router.post('/auth_test')
async def auth_test_route(
        user: models.User = Depends(security.get_current_user),
):
    return {'response': f'{user.login}'}
