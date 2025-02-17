import uuid
from typing import Annotated

from fastapi import Path, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database.infrastructure import db_helper
from src.models import User

from src.api.v1.user.service import UserService



async def user_by_oid(
    oid: Annotated[uuid.UUID, Path],
    session: Annotated[AsyncSession, Depends(db_helper.get_session)],
) -> User:
    user = await UserService(session).get_user_by_id(oid=oid)
    if user is not None:
        return user

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"User {oid} not found!",
    )

