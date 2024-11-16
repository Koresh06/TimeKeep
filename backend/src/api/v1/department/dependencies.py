import uuid
from typing import Annotated

from fastapi import Path, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.session import get_async_session
from models.department import Department

from .service import DepartmentService



async def department_by_id(
    id: Annotated[uuid.UUID, Path],
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> Department:
    department = await DepartmentService(session).get_one(id=id)
    if department is not None:
        return department

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Department {id} not found!",
    )