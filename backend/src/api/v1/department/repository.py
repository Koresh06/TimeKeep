import uuid

from typing import List, Optional
from sqlalchemy import select, Result

from core.repo.base import BaseRepo
from models import Department
from .schemas import DepartmentCreate, DepartmentUpdate, DepartmentOut


class DepartmentRepository(BaseRepo):
    
    async def create(self, data: Department) -> Optional[Department]:
        department = Department(**data.model_dump())
        self.session.add(department)
        await self.session.commit()
        await self.session.refresh(department)
        return DepartmentOut.model_validate(department)
    

    async def get_one(self, id: uuid.UUID) -> DepartmentOut:
        stmt = select(Department).where(Department.id == id)
        result: Result = await self.session.scalar(stmt)
        return DepartmentOut.model_validate(result)






