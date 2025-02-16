from typing import List, Optional
import uuid
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.v1.organization.repository import OrganizationRepository
from src.api.v1.organization.schemas import (
    OrganizationOut,
    PaginatedResponse,
    OrganizationCreate,
    OrganizationExtendedOut
)
from src.api.v1.department.schemas import DepartmentOut



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

        organizations, total_count = await self.repo.get_all(limit=limit,   offset=offset)

        # Правильная обработка департаментов как списка
        extended_organizations_data = [
            OrganizationExtendedOut.model_validate(
                {
                    **OrganizationOut.model_validate(organization).model_dump   (),
                    "departments": [
                        department
                        for department in organization.department_rel
                    ],
                }
            )
            for organization in organizations
        ]

        return PaginatedResponse(
            count=total_count,
            items=extended_organizations_data,
        )

