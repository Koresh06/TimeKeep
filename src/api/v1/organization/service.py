from typing import List, Optional
import uuid
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.v1.organization.repository import OrganizationRepository
from src.api.v1.organization.schemas import (
    OrganizationOut,
    PaginatedResponse,
    OrganizationCreate,
)
from src.models import User


class OrganizationService:

    def __init__(self, session: AsyncSession):
        self.repo = OrganizationRepository(session)

    async def create(
        self,
        organization_create: OrganizationCreate,
    ) -> OrganizationOut:
        organization = await self.repo.create(
            organization_create=organization_create,
        )
        return OrganizationOut.model_validate(organization)

    async def get_all(
        self,
        limit: int = None,
        offset: int = None,
    ) -> PaginatedResponse[OrganizationOut] | List[OrganizationOut]:
        if limit is None and offset is None:
            return await self.repo.get_all_register()
        
        organizations, total_count = await self.repo.get_all(limit=limit, offset=offset)
        organizations_data = [
            OrganizationOut.model_validate(org).model_dump() for org in organizations
        ]

        return PaginatedResponse(count=total_count, items=organizations_data)
