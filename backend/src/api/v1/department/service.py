from typing import List
import uuid
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from models import Department
from .repository import DepartmentRepository
from .schemas import (
    DepartmentCreate,
    DepartmentUpdate,
    DepartmentOut,
    DepartmentUpdatePartil,
)


class DepartmentService:

    def __init__(self, session: AsyncSession):
        self.repository = DepartmentRepository(session=session)


    async def create(self, department_create: DepartmentCreate) -> DepartmentOut:
        department = await self.repository.create(department_create=department_create)
        if not department:
            raise HTTPException(status_code=400, detail="Department already exists.")
        return DepartmentOut.model_validate(department)  


    async def get_all(self) -> List[DepartmentOut]:
        departments = await self.repository.get_all()
        return [DepartmentOut.model_validate(department) for department in departments]  


    async def get_one(self, oid: uuid.UUID) -> DepartmentOut:
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
        if not department:
            raise HTTPException(status_code=404, detail="Department not found for update.")
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
        if not department:
            raise HTTPException(status_code=404, detail="Department not found for update.")
        return DepartmentOut.model_validate(department)
    

    async def delete(self, department: Department):
        await self.repository.delete(department=department)
