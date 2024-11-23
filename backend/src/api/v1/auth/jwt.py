import uuid
from jose import jwt
from datetime import datetime, timedelta, timezone

from core.config import settings
from .schemas import Token

ALGORITHM = "HS256"
access_token_jwt_subject = "access"


def create_token(user_oid: uuid.UUID) -> Token:
    """Создание токена доступа"""
    access_token_expires = timedelta(minutes=settings.api.access_token_expire_minutes)

    access_token = create_access_token(
        data={"user_oid": str(user_oid)},
        expires_delta=access_token_expires,
    )

    return Token(
        access_token=access_token,
        token_type="bearer"
    )

def create_access_token(*, data: dict, expires_delta: timedelta = None) -> str:
    """Генерация JWT токена"""
    to_encode = data.copy()

    expire = datetime.now(tz=timezone.utc) + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire, "sub": "access"})

    try:
        encoded_jwt = jwt.encode(to_encode, settings.api.secret_key, algorithm=ALGORITHM)
    except Exception as e:
        raise RuntimeError(f"Ошибка создания токена: {str(e)}")

    return encoded_jwt