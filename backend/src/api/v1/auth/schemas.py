from uuid import UUID
from fastapi_users import schemas
from pydantic import ConfigDict, BaseModel, EmailStr

from models.user import Role


class UserRead(schemas.BaseUser[UUID]):
    username: str
    department_id: UUID | None = None
    full_name: str
    position: str
    role: Role = Role.USER


class UserCreate(schemas.BaseUserCreate):
    username: str
    department_id: UUID | None = None
    full_name: str
    position: str
    role: Role = Role.USER


class UserUpdate(schemas.BaseUserUpdate):
    username: str | None = None
    department_id: UUID | None = None
    full_name: str | None = None
    position: str | None = None
    role: Role | None = Role.USER


class UserOut(UserRead):
    id: UUID
    _password: str

    model_config = ConfigDict(from_attributes=True)
