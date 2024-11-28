import uuid

from typing import List, Optional
from fastapi import HTTPException
from sqlalchemy import select, Result
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from core.repo.base import BaseRepo
from models import Overtime

from .schemas import OvertimeCreate


class OvertimeRepository(BaseRepo):

    async def create(self, overtime_create: OvertimeCreate) -> Overtime:
        try:
            overtime = Overtime(**overtime_create.model_dump())
            self.session.add(overtime)
            await self.session.commit()
            await self.session.refresh(overtime)
            return overtime
        except IntegrityError as e:
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    
    async def get_all(self, limit: int, offset: int) -> List[Overtime]:
        try:
            stmt = select(Overtime).limit(limit).offset(offset)
            result: Result = await self.session.scalars(stmt)
            overtime = result.all()
            return overtime
        except SQLAlchemyError as e:
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
        

    async def get_one(self, oid: uuid.UUID) -> Optional[Overtime]:
        try:
            stmt = select(Overtime).where(Overtime.oid == oid)
            result: Result = await self.session.scalar(stmt)
            return result
        except SQLAlchemyError as e:
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")