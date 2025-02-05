from typing import List, Optional
import uuid
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.v1.organization.repository import OrganizationRepository
from src.api.v1.organization.schemas import OrganizationOut



class OrganizationService:

    def __init__(self, session: AsyncSession):
        self.repo = OrganizationRepository(session)


    async def get_all(self) -> List[OrganizationOut]:
        organizations = await self.repo.get_all()
        return [OrganizationOut.model_validate(organization) for organization in organizations]