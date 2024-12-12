from typing import Annotated
import uuid

from fastapi import Path, status, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from core.session import get_async_session
from models import DayOff, User
from .service import DayOffService
from api.v1.auth.dependencies import get_current_user
from .errors import DayOffNotFoundError


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