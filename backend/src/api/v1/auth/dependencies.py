from typing import Annotated
from jose import jwt, JWTError
from fastapi import Depends, HTTPException, Security, Request, status
from fastapi.security import APIKeyCookie
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.session import get_async_session
from .security import verify_password

from models import User
from .service import AuthService

from .jwt import ALGORITHM
from .schemas import TokenPayload


cookie_scheme = APIKeyCookie(name="access_token", auto_error=False)


async def authenticate_user(session: AsyncSession, username: str, password: str):
    user: User = await AuthService(session).get_user(username=username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


async def get_current_user(
    request: Request,
    session: Annotated[
        AsyncSession,
        Depends(get_async_session),
    ],
    token: Annotated[
        str,
        Security(cookie_scheme),
    ]
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    # token = request.cookies.get("access_token")
    try:
        payload = jwt.decode(token, settings.api.secret_key, algorithms=[ALGORITHM])
        token_data = TokenPayload(**payload)
    except JWTError:
        raise credentials_exception
        
    user: User = await AuthService(session).get_user_by_id(user_oid=token_data.user_oid)
    if user is None:
        raise credentials_exception

    return user




