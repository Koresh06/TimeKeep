import uuid
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from .repository import DepartmentRepository
from .schemas import DepartmentCreate, DepartmentUpdate, DepartmentOut


class DepartmentService():
   
    def __init__(self, session: AsyncSession):
      self.repository = DepartmentRepository(session=session)
      

    async def create(self, department_create: DepartmentCreate) -> DepartmentOut:
        department = await self.repository.create(data=department_create)
        if not department:
            raise HTTPException(status_code=400, detail="Department already exists")
        return department
    

    async def get_one(self, id: uuid.UUID) -> DepartmentOut:
       department = await self.repository.get_one(id=id)
       if not department:
           raise HTTPException(status_code=400, detail="Department not found")
       return department