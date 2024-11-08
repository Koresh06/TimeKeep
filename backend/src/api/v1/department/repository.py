import uuid

from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from core.repo.base import BaseRepo

from models import Department


class DepartmentRepository(BaseRepo):

    async def get_department_by_id(self, department_oid: uuid.UUID) -> Optional[Department]:
        stmt = select(Department).where(Department.oid == department_oid)
        result = await self.session.scalar(stmt)
        return result






