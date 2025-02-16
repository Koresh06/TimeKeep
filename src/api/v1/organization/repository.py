import uuid

from typing import List, Optional, Tuple
from fastapi import HTTPException
from sqlalchemy import and_, func, select, Result
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from src.core.repo.base import BaseRepo
from src.models import Organization, User
from src.api.v1.organization.schemas import OrganizationCreate, OrganizationOut



class OrganizationRepository(BaseRepo):

    async def create(
        self,
        organization_create: OrganizationCreate,
    ) -> Organization:
        try:
            organization = Organization(
                name=organization_create.name,
                name_boss=organization_create.name_boss,
                position=organization_create.position,
                rank=organization_create.rank,
            )
            self.session.add(organization)
            await self.session.commit()
            await self.session.refresh(organization)
            return organization
        except IntegrityError as e:
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


    async def get_all_register(self) -> List[Organization]:
        try:
            stmt = select(Organization)
            result: Result = await self.session.scalars(stmt)
            organizations = result.all()
            return organizations
        except SQLAlchemyError as e:
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


    async def get_all(self, limit: int, offset: int) -> Tuple[List[Organization], int]:
        try:
            stmt_count = select(func.count()).select_from(Organization)
            total_count = await self.session.scalar(stmt_count)

            stmt = (
                select(Organization)
                .options(selectinload(Organization.department_rel))  
                .limit(limit)
                .offset(offset)
                .order_by(Organization.create_at.desc())
            )
            result = await self.session.scalars(stmt)

            return result.all(), total_count 
        except SQLAlchemyError as e:
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")