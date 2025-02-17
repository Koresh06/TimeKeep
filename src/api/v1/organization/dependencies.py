import uuid
from typing import Annotated

from fastapi import Path, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database.infrastructure import db_helper
from src.models import Organization

from src.api.v1.organization.service import OrganizationService



async def organization_by_oid(
    oid: Annotated[uuid.UUID, Path],
    session: Annotated[AsyncSession, Depends(db_helper.get_session)],
) -> Organization:
    organization = await OrganizationService(session).get_one(oid=oid)
    if organization is not None:
        return organization

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Organization {oid} not found!",
    )