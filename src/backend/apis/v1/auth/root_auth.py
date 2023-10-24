from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.db import sessions, repository
from src.backend.db import redis
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
    response_model=schemas_auth.UserResponse,
    responses={
        '409': {
            'description': 'Login already used (may be)',
            'model': schemas_auth.NewUserError,
        },
    },
)
async def create_user(
        source: schemas_auth.NewUserRequest,
        session: AsyncSession = Depends(sessions.database.new_session),
        redis_sess: Redis = Depends(redis.sessions.new_jwt_redis_session),
):
    res = await repository.users.create_new_user(source, session)

    access_token, refresh_token = await security.get_new_tokens(
        decoded_token=res,
        session=redis_sess,
    )

    response = JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            **res,
            'access_token': access_token,
            'refresh_token': refresh_token,  # ??? need or ... ???
        },
    )

    security.set_tokens_in_response(response, access_token, refresh_token)

    return response


@router.post(
    '/token',
    response_model=schemas_auth.UserResponse,
    responses={
        '401': {
            'description': 'UNAUTHORIZED',
        },
    },
)
async def login_user(
        form_data: OAuth2PasswordRequestForm = Depends(),
        session: AsyncSession = Depends(sessions.database.new_session),
        redis_sess: Redis = Depends(redis.sessions.new_jwt_redis_session),
):
    user = await security.authenticate_user(
        form_data.username,
        form_data.password,
        session,
    )

    access_token, refresh_token = await security.get_new_tokens(
        decoded_token=user.jwt_model,
        session=redis_sess,
    )

    response = JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            **user.jwt_model,
            'access_token': access_token,
            'refresh_token': refresh_token,  # ??? need or ... ???
        },
    )

    return response


@router.get(
    '/refresh',
    response_model=schemas_auth.UserResponse,
    responses={
        '401': {
            'description': 'Refresh token was expired',
        },
    },
)
async def refresh_user_tokens(
        refresh_token: str,
        redis_sess: Redis = Depends(redis.sessions.new_jwt_redis_session),
):
    """Create new tokens for user from users refresh token"""
    data = await security.refresh_user_tokens(refresh_token, redis_sess)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=data,
    )
