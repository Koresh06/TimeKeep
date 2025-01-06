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
        token_type="bearer",
        access_token_expires=str(access_token_expires),
    )

def create_access_token(*, data: dict, expires_delta: timedelta = None) -> str:
    """Генерация JWT токена"""
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(tz=timezone.utc) + expires_delta
    else:
        expire = datetime.now(tz=timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire, "sub": access_token_jwt_subject})
    encoded_jwt = jwt.encode(to_encode, settings.api.secret_key, algorithm=ALGORITHM)
    return encoded_jwt