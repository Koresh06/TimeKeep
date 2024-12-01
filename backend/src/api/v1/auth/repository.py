import uuid

from typing import Optional
from sqlalchemy.future import select

from core.repo.base import BaseRepo

from models import User

class AuthRepository(BaseRepo):

    async def get_user_by_username(self, username: str) -> Optional[User]:
        stmt = select(User).where(User.username == username)
        result = await self.session.scalar(stmt)
        return result
    

    async def get_user_by_id(self, user_oid: uuid.UUID) -> Optional[User]:
        stmt = select(User).where(User.oid == user_oid)
        result = await self.session.scalar(stmt)
        return result
    

    
