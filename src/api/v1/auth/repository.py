import uuid

from typing import Optional
from sqlalchemy import Result
from sqlalchemy.orm import selectinload
from sqlalchemy.future import select

from src.core.repo.base import BaseRepo

from src.models import User

class AuthRepository(BaseRepo):


    async def get_user_by_username(self, username: str) -> Optional[User]:
        stmt = select(User).where(User.username == username)
        result: Result = await self.session.scalar(stmt)
        return result
    

    async def get_user_by_id(self, user_oid: uuid.UUID) -> Optional[User]:
        stmt = select(User).where(User.oid == user_oid).options(selectinload(User.department_rel))
        result: Result = await self.session.scalar(stmt)
        return result

    

    
