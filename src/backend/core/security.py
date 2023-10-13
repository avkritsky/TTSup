from passlib.context import CryptContext


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
