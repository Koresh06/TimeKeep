from typing import Optional
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from .repository import AuthRepository
from models import User

class AuthService:

    def __init__(self, session: AsyncSession):
        self.repository = AuthRepository(session=session)


    async def get_user(self, username: str) -> User:
        user = await self.repository.get_user_by_username(username=username)
        if not user:
            return None
        return user
    

    async def get_user_by_id(self, user_oid: uuid.UUID) -> Optional[User]:
        user = await self.repository.get_user_by_id(user_oid=user_oid)
        return user
    

    