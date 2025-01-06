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


    async def authenticate_and_create_token(self, oauth_form_data: OAuth2PasswordRequestForm) -> Token:
        user = await self.get_user(oauth_form_data.username)  # Получаем пользователя по имени
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Неверное имя пользователя или пароль")
        
        # Проверка на активность аккаунта
        if not user.is_active:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ваш аккаунт не подтверждён. Пожалуйста, подождите.")

        # Проверка пароля
        if not verify_password(oauth_form_data.password, user.hashed_password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Неверное имя пользователя или пароль")

        return create_token(user_oid=user.oid)

