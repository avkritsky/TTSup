from fastapi import Response, Depends
from fastapi.security import APIKeyCookie

from datetime import timedelta, datetime
from typing import TypeAlias

from fastapi import HTTPException, status
from jose import jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.core import config
from src.backend.db import redis, repository, sessions

pwd_context = CryptContext(
    schemes=['bcrypt'],
    deprecated='auto',
)


def verify_password(
        decode_password: str,
        encode_password: str,
) -> bool:
    return pwd_context.verify(decode_password, encode_password)


def get_encode_password(password: str) -> str:
    return pwd_context.hash(password)


def create_token(
        login: str,
        group: str,
        ttl: timedelta | int,
) -> str:
    """Create JWT token"""
    if isinstance(ttl, int):
        ttl = timedelta(seconds=ttl)

    exp = datetime.utcnow() + ttl

    data = {
        'login': login,
        'group': group,
        'exp': exp,
    }

    token = jwt.encode(data, config.JWT_SECRET_CODE, config.JWT_ALGORITHM)

    return token


AccessToken: TypeAlias = str
RefreshToken: TypeAlias = str


def create_new_tokens(
        login: str,
        group: str,
) -> tuple[AccessToken, RefreshToken]:
    """Create tokens tuple"""
    access_token = create_token(login, group, ttl=config.JWT_TTL_ACCESS)
    refresh_token = create_token(login, group, ttl=config.JWT_TTL_REFRESH)

    return access_token, refresh_token


def decode_token(
        token: RefreshToken | AccessToken,
) -> dict:
    """Try decode token. Raise HTTP exception 401 if expired"""
    try:
        data = jwt.decode(
            token,
            config.JWT_SECRET_CODE,
            config.JWT_ALGORITHM,
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Refresh token was expired',
        )

    return data


async def load_token_from_redis(
        data: dict,
        session: redis.repository.Redis,
) -> dict:
    """Load user tokens from redis by decode refresh token"""
    try:
        login = data['login']
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid token!',
        )

    redis_data = await redis.repository.get_item(login, session)

    return redis_data


async def is_token_valid(
        token: RefreshToken,
        redis_data: dict,
) -> bool:
    """Check that token in redis equal received token from user"""
    try:
        return redis_data['refresh_token'] == token
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid token!',
        )


async def get_new_tokens(
        decoded_token: dict,
        session: redis.repository.Redis,
) -> tuple[AccessToken, RefreshToken]:
    """Create new tokens by decoded token, save to redis and return new
    pair tokens"""
    new_access, new_refresh = create_new_tokens(
        login=decoded_token['login'],
        group=decoded_token['group'],
    )

    new_redis_data = {
        'access_token': new_access,
        'refresh_token': new_refresh,
    }

    await redis.repository.set_item(
        key=decoded_token['login'],
        val=new_redis_data,
        ttl=config.JWT_TTL_REFRESH,
        session=session,
    )

    return new_access, new_refresh


async def refresh_user_tokens(
        refresh_token: RefreshToken,
        session: redis.repository.Redis,
) -> tuple[AccessToken, RefreshToken]:
    """Re-create user tokens and save is in redis by valid refresh token"""
    decoded_token = decode_token(refresh_token)

    redis_tokens = await load_token_from_redis(decoded_token, session)

    if not is_token_valid(refresh_token, redis_tokens):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid token!',
        )

    return await get_new_tokens(decoded_token, session)


def set_tokens_in_response(
        response: Response,
        access_token: AccessToken,
        refresh_token: RefreshToken,
):
    """Set tokens in response cookies"""
    response.set_cookie(
        key='access_token',
        value=access_token,
        expires=config.JWT_TTL_ACCESS,
        httponly=True,
        samesite=None,
        secure=True,
    )
    response.set_cookie(
        key='refresh_token',
        value=refresh_token,
        expires=config.JWT_TTL_REFRESH,
        httponly=True,
        samesite=None,
        secure=True,
    )


auth_scheme = APIKeyCookie(
    name='access_token',
    auto_error=False,
)


async def get_current_user(
        token: str = Depends(auth_scheme),
        session: AsyncSession = Depends(sessions.database.new_session),
):
    exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate credentials',
    )

    print(token)

    try:
        payload = jwt.decode(
            token,
            config.JWT_SECRET_CODE,
            config.JWT_ALGORITHM,
        )
        login = payload['login']
    except (jwt.JWTError, KeyError):
        raise exception
    except AttributeError:
        raise exception

    user = await repository.users.get_user_by_login(login, session)

    if user is None:
        raise exception

    return user
