from typing import Annotated
import uuid

from fastapi import Path, status, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from core.session import get_async_session
from models import DayOff, User
from .service import DayOffService
from .schemas import DayOffOut, DayOffExtendedOut
from api.v1.auth.dependencies import get_current_user


async def day_off_by_oid(
    oid: Annotated[uuid.UUID, Path],
    session: Annotated[AsyncSession, Depends(get_async_session)],
    current_user: User = Depends(get_current_user),
) -> DayOffOut | DayOffExtendedOut:
    day_off = await DayOffService(session).get_one(current_user=current_user, oid=oid)
    if day_off is not None:
        return day_off

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Day off {oid} not found!",
    )