import uuid
from typing import Annotated

from fastapi import Path, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database.infrastructure import db_helper
from src.models.department import Department

from src.api.v1.department.service import DepartmentService



async def department_by_oid(
    oid: Annotated[uuid.UUID, Path],
    session: Annotated[AsyncSession, Depends(db_helper.get_session)],
) -> Department:
    department = await DepartmentService(session).get_one(oid=oid)
    if department is not None:
        return department

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Department {oid} not found!",
    )