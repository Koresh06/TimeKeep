from typing import Optional
import uuid
from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from .repository import AuthRepository
from models import User

from .schemas import Token
from .security import verify_password
from .jwt import create_token


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


    async def authenticate_user(
        self,
        username: str,
        password: str,
    ):
        user: User = await self.get_user(username=username)
        if not user:
            return False
        if not verify_password(password, user.hashed_password):
            return False
        return user


    async def authenticate_and_create_token(
        self,
        form_data: OAuth2PasswordRequestForm,
    ) -> Token:
        user = await self.authenticate_user(
            username=form_data.username,
            password=form_data.password,
        )
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
            )
        return create_token(user_oid=user.oid)

