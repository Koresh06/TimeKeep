from datetime import datetime
from typing import Optional
import uuid
from pydantic import BaseModel, ConfigDict, Field, field_validator

from models.user import Role


class UserBase(BaseModel):
    department_oid: uuid.UUID
    username: str
    full_name: str
    position: str
    role: Role = Role.USER


class UserCreate(UserBase):
    password: str = Field(min_length=8)  # Клиент передаёт "password"

    @field_validator("password")
    def validate_password(cls, value: str) -> str:
        # Проверка длины или других условий пароля
        if len(value) < 8:
            raise ValueError("Password must be at least 8 characters")
        return value


class UserUpdate(UserBase):
    username: Optional[str] = None
    full_name: Optional[str] = None
    position: Optional[str] = None
    role: Optional[str] = None


class UserUpdatePartial(UserBase):
    username: Optional[str] = None
    full_name: Optional[str] = None
    position: Optional[str] = None
    role: Optional[str] = None



class UserOut(UserBase):
    oid: uuid.UUID
    is_active: bool
    is_superuser: bool
    create_at: datetime
    update_at: datetime

    model_config = ConfigDict(from_attributes=True)