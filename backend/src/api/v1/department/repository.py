import uuid

from typing import List, Optional
from fastapi import HTTPException
from sqlalchemy import select, Result
from sqlalchemy.exc import SQLAlchemyError

from core.repo.base import BaseRepo
from models import Department
from .schemas import DepartmentCreate, DepartmentUpdate, DepartmentOut, DepartmentUpdatePartil


class DepartmentRepository(BaseRepo):
    
    async def create(self, department_create: DepartmentCreate) -> DepartmentOut:
        result = await self.session.execute(select(Department).where(Department.name == department_create.name))
        existing_department = result.scalar()

        if existing_department:
            return None

        department = Department(**department_create.model_dump())
        self.session.add(department)
        
        try:
            await self.session.commit()
            await self.session.refresh(department)
            return DepartmentOut.model_validate(department)
        except SQLAlchemyError:
            await self.session.rollback()
            raise HTTPException(status_code=500, detail="Database error during department creation")


    async def get_all(self) -> List[Department]:
        try:
            stmt = select(Department)
            result: Result = await self.session.scalars(stmt)
            departments = result.all()
            return departments
        except SQLAlchemyError as e:
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


    async def get_one(self, oid: uuid.UUID) -> Department:
        try:
            stmt = select(Department).where(Department.oid == oid)
            result: Result = await self.session.scalar(stmt)
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




