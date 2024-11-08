from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from models import User
from .repository import UserRepository
from .schemas import UserCreateSchema
from ..department.repository import DepartmentRepository


class UserService(UserRepository):

    async def get_user(self, user_id: int) -> User:
        user = await self.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return user
    

    async def registration(self, user_create: UserCreateSchema) -> User:
        check_user = await self.get_user_by_id(user_create.oid)
        if check_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User already exists"
            )
        
        department = await DepartmentRepository(self.session).get_department_by_id(user_create.department_oid)
        if not department:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Department not found"
            )
        
        user = await self.create_user(user_create)
        return user