from datetime import timedelta, datetime

from passlib.context import CryptContext
from jose import jwt

from src.backend.core import config


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
