import uuid

from typing import List, Optional, Tuple
from fastapi import HTTPException
from sqlalchemy import and_, func, select, Result
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from src.core.repo.base import BaseRepo
from src.models import Organization



class OrganizationRepository(BaseRepo):

    async def get_all(self) -> List[Organization]:
        try:
            stmt = select(Organization)
            result: Result = await self.session.scalars(stmt)
            organizations = result.all()
            return organizations
        except SQLAlchemyError as e:
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")