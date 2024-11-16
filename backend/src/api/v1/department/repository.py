import uuid

from typing import List, Optional
from fastapi import HTTPException
from sqlalchemy import select, Result
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from core.repo.base import BaseRepo
from models import Department
from .schemas import DepartmentCreate, DepartmentUpdate, DepartmentOut, DepartmentUpdatePartil


class DepartmentRepository(BaseRepo):
    
    async def create(self, department_create: DepartmentCreate) -> Optional[Department]:
        department = Department(**department_create.model_dump())
        self.session.add(department)
        try:
            await self.session.commit()
            await self.session.refresh(department)
            return department
        except IntegrityError:
            await self.session.rollback()
            return None
        except SQLAlchemyError:
            await self.session.rollback()
            raise HTTPException(status_code=500, detail="Database error during department creation")


    async def get_all(self) -> List[Department]:
        try:
            stmt = select(Department)
            result: Result = await self.session.scalars(stmt)
            departments = result.all()
            if not departments:
                raise HTTPException(status_code=404, detail="No departments found.")
            return departments
        except SQLAlchemyError as e:
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


    async def get_one(self, id: uuid.UUID) -> Department:
        try:
            stmt = select(Department).where(Department.id == id)
            result: Result = await self.session.scalar(stmt)
            if not result:
                raise HTTPException(status_code=404, detail=f"Department with ID {id} not found.")
            return result
        except SQLAlchemyError as e:
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


    async def update(
        self,
        department: Department,
        department_update: DepartmentUpdate | DepartmentUpdatePartil,
        partil: bool = False,
    ) -> Optional[Department]:
        try:
            for key, value in department_update.model_dump(exclude_unset=partil).items():
                setattr(department, key, value)

            await self.session.commit()
            await self.session.refresh(department)
            return department
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


    async def delete(self, department: Department):
        try:
            await self.session.delete(department)
            await self.session.commit()
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")




