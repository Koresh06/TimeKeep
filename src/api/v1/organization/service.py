from typing import List, Optional
import uuid
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.v1.organization.repository import OrganizationRepository
from src.api.v1.organization.schemas import (
    OrganizationOut,
    PaginatedResponse,
    OrganizationCreate,
    OrganizationExtendedOut,
    OrganizationUpdatePartil
)
from src.models import Organization
from src.api.v1.department.schemas import DepartmentOut



class OrganizationService:

    def __init__(self, session: AsyncSession):
        self.repository = OrganizationRepository(session)

    async def create(
        self,
        organization_create: OrganizationCreate,
    ) -> OrganizationOut:
        organization = await self.repository.create(
            organization_create=organization_create,
        )
        return OrganizationOut.model_validate(organization)

    async def get_all(
        self,
        limit: int = None,
        offset: int = None,
    ) -> PaginatedResponse[OrganizationOut] | List[OrganizationOut]:
        if limit is None and offset is None:
            return await self.repository.get_all_register()

        organizations, total_count = await self.repository.get_all(limit=limit,   offset=offset)
        
        extended_organizations_data = [
            OrganizationExtendedOut.model_validate(
                {
                    **OrganizationOut.model_validate(organization).model_dump(),
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


    async def get_all_dep_organizations(self) -> List[OrganizationOut]:
        organizations = await self.repository.get_all_dep_organizations()
        return [OrganizationOut.model_validate(organization) for organization in organizations]


    async def get_one(self, oid: uuid.UUID) -> Organization:
        organization = await self.repository.get_one(oid=oid)
        return organization
    

    async def modify(
        self,
        organization: Organization,
        organization_update: OrganizationUpdatePartil,
        partial: bool,
    ) -> OrganizationOut:
        organization = await self.repository.update(
            organization=organization,
            organization_update=organization_update,
            partial=partial,
        )
        return OrganizationOut.model_validate(organization)