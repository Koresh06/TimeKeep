from uuid import UUID
from fastapi_users import schemas

from models.user import Role


class UserRead(schemas.BaseUser[UUID]):
    username: str
    department_id: UUID
    role: Role = Role.USER


class UserCreate(schemas.BaseUserCreate):
    username: str
    department_id: UUID
    role: Role = Role.USER


class UserUpdate(schemas.BaseUserUpdate):
    pass
