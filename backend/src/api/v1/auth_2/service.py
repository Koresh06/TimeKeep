from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from api.v1.auth_2.security import verify_password
from .repository import AuthRepository
from .schemas import UserResponse
from models import User

class AuthService(AuthRepository):

    async def get_user(self, user_id: int) -> UserResponse:
        user = await self.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return UserResponse.model_config.from_orm(user)
    

    async def authenticate(self, username, password: str) -> Optional[User]:
        stmt = select(User).where(User.username == username)
        user: User = await self.session.scalar(stmt)

        if not user:
            return None
        if not verify_password(password, user._hashed_password):
            return None
        return user