from typing import List
import uuid
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Department
from src.api.v1.department.repository import DepartmentRepository
from src.api.v1.department.schemas import (
    DepartmentCreate,
    DepartmentUpdate,
    DepartmentOut,
    DepartmentUpdatePartil,
)


class DepartmentService:

    def __init__(self, session: AsyncSession):
        self.repository = DepartmentRepository(session=session)

    async def create(
        self,
        department_create: DepartmentCreate,
    ) -> DepartmentOut:
        department = await self.repository.create(
            department_create=department_create,
        )
        return DepartmentOut.model_validate(department)

    async def get_all(self) -> List[DepartmentOut]:
        departments = await self.repository.get_all()
        return [DepartmentOut.model_validate(department) for department in departments]

    async def get_one(self, oid: uuid.UUID) -> Department:
        department = await self.repository.get_one(oid=oid)
        return department

    async def modify(
        self,
        department: Department,
        department_update: DepartmentUpdatePartil,
        partil: bool,
    ) -> DepartmentOut:
        department = await self.repository.update(
            department=department,
            department_update=department_update,
            partil=partil,
        )
        return DepartmentOut.model_validate(department)

    async def replace(
        self,
        department: Department,
        department_update: DepartmentUpdate,
    ) -> DepartmentOut:
        department = await self.repository.update(
            department=department,
            department_update=department_update,
        )
        return DepartmentOut.model_validate(department)

    async def delete(self, department: Department):
        await self.repository.delete(department=department)

    async def get_by_organization(
        self, organization_oid: uuid.UUID
    ) -> List[DepartmentOut]:
        departments = await self.repository.get_by_organization(
            organization_oid=organization_oid
        )
        return [DepartmentOut.model_validate(department) for department in departments]
