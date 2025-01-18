from typing import Annotated
import uuid

from fastapi import Path, status, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.session import get_async_session
from src.models import DayOff, User
from src.api.v1.day_off.service import DayOffService
from src.api.v1.auth.dependencies import get_current_user
from src.api.v1.day_off.errors import DayOffNotFoundError


async def day_off_by_oid(
    oid: Annotated[uuid.UUID, Path],
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> DayOff:
    try:
        day_off = await DayOffService(session).get_day_off_oid(oid=oid)
        if not day_off:
            raise DayOffNotFoundError(oid)

        return day_off

    except DayOffNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Day off with oid {oid} not found",
        )


async def count_notifications_day_offs(
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_async_session)],
):
    return await DayOffService(session).count_notifications(current_user=current_user)
