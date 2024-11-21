import uuid

from typing import List, Optional
from fastapi import HTTPException
from fastapi_users.password import PasswordHelperProtocol, PasswordHelper
from sqlalchemy import select, Result
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from core.repo.base import BaseRepo
from models import User
from .schemas import UserCreate, UserOut


class AuthRepository(BaseRepo):

    __password_helper: PasswordHelperProtocol = PasswordHelper()

    async def create_superuser(self, user_create: UserCreate) -> UserOut:
        try:
            superuser = User(
                email=user_create.email,
                hashed_password=self.__password_helper.hash(user_create.password),
                username=user_create.username,
                full_name=user_create.full_name,
                position=user_create.position,
                role=user_create.role,
                department_id=user_create.department_id,
                is_superuser=True,
                is_active=True,
            )
            self.session.add(superuser)
            await self.session.commit()
            await self.session.refresh(superuser)
            return superuser
        except Exception as e:
            print(f"Error creating superuser: {str(e)}")
            return False
        
