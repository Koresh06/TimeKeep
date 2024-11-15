from typing import Annotated
from jose import jwt, JWTError
from fastapi import Depends, Security, Request
from fastapi.security import APIKeyCookie
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.session import get_db

from models import User
from api.v1.user.service import UserService

from .jwt import ALGORITHM
from .schemas import TokenPayload


cookie_scheme = APIKeyCookie(name="access_token", auto_error=False)


async def get_current_user(
    request: Request,
    session: Annotated[
        AsyncSession,
        Depends(get_db),
    ],
    token: Annotated[
        str,
        Security(cookie_scheme),
    ]
):
    """Check auth user and redirect if inactive"""
    token = request.cookies.get("access_token")
    if not token: 
        return False
    try:
        payload = jwt.decode(token, settings.api.secret_key, algorithms=[ALGORITHM])
        token_data = TokenPayload(**payload)
    except JWTError:
        False
        
    user: User = await UserService(session).get_user(user_id=token_data.user_oid)
    if not user:
        False

    return user