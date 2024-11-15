import uuid

from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from core.repo.base import BaseRepo

from models import User
from api.v1.user.schemas import UserCreateSchema, UserUpdateSchema


class AuthRepository(BaseRepo):

    async def get_user_by_id(self, user_oid: uuid.UUID) -> Optional[User]:
        stmt = select(User).where(User.oid == user_oid)
        result = await self.session.scalar(stmt)
        return result