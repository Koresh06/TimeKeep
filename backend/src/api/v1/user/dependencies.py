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
) -> User:
    user = await UserService(session).get_user_by_id(oid=oid)
    if user is not None:
        return user

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"User {oid} not found!",
    )

