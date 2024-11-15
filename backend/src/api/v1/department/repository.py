import uuid

from typing import List, Optional
from sqlalchemy.future import select

from core.repo.base import BaseRepo

from models import Department


class DepartmentRepository(BaseRepo):

    async def get_department_by_id(self, department_id: uuid.UUID) -> Optional[Department]:
        stmt = select(Department).where(Department.id == department_id)
        result = await self.session.scalar(stmt)
        return result






