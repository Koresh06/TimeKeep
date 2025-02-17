import uuid
from typing import Annotated

from fastapi import Path, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database.infrastructure import db_helper
from src.models import Overtime

from src.api.v1.overtime.service import OvertimeService



async def overtime_by_oid(
    oid: Annotated[uuid.UUID, Path],
    session: Annotated[AsyncSession, Depends(db_helper.get_session)],
) -> Overtime:
    overtime = await OvertimeService(session).get_one(oid=oid)
    if overtime is not None:
        return overtime

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Overtime {oid} not found!",
    )