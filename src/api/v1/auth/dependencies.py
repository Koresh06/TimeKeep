from typing import Annotated
from jose import jwt, JWTError
from fastapi import Depends, HTTPException, Request, Security, status
from fastapi.security import APIKeyCookie
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.core.session import get_async_session

from src.models import User
from src.api.v1.auth.service import AuthService

from src.api.v1.auth.jwt import ALGORITHM
from src.api.v1.auth.schemas import TokenPayload


cookie_scheme = APIKeyCookie(name="access_token", auto_error=False)


async def get_current_user(
    session: Annotated[AsyncSession, Depends(get_async_session)],
    token: Annotated[str, Security(cookie_scheme)],
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    not_authenticated = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not token:
        raise not_authenticated
    try:
        payload = jwt.decode(token, settings.api.secret_key, algorithms=[ALGORITHM])
        token_data = TokenPayload(**payload)
    except (JWTError, KeyError):
        raise credentials_exception

    user: User = await AuthService(session).get_user_by_id(user_oid=token_data.user_oid)
    if not user:
        raise credentials_exception

    return user


def get_is_authenticated(request: Request):
    return "access_token" in request.cookies





