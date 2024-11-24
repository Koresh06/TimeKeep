import uuid
from typing import Annotated

from fastapi import Path, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.session import get_async_session
from models import User

from .service import UserService
from .schemas import UserOut
from ..auth.dependencies import get_current_user



async def user_by_oid(
    oid: Annotated[uuid.UUID, Path],
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> UserOut:
    user = await UserService(session).get_one(oid=oid)
    if user is not None:
        return user

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"User {oid} not found!",
    )


async def get_current_moderator(
    current_user: Annotated[UserOut, Depends(get_current_user)]
) -> UserOut:
    if not current_user.role == "moderator":
        raise HTTPException(
            status_code=400, detail="The user doesn't have enough privileges"
        )
    return current_user


async def get_current_superuser(
    current_user: Annotated[UserOut, Depends(get_current_user)]
) -> UserOut:
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=400, detail="The user doesn't have enough privileges"
        )
    return current_user