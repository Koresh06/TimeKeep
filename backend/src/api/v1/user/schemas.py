from datetime import datetime
from typing import Optional
import uuid
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from models.user import Role


class UserBase(BaseModel):
    department_oid: uuid.UUID = None
    username: str
    full_name: str
    position: str
    role: Role = Role.USER


class UserCreate(UserBase):
    password: str = Field(min_length=8) 
    is_superuser: bool = False

    @field_validator("password")
    def validate_password(cls, value: str) -> str:
        if len(value) < 8:
            raise ValueError("Password must be at least 8 characters")
        return value


class UserUpdate(UserBase):
    department_oid: Optional[uuid.UUID] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    position: Optional[str] = None
    role: Optional[Role] = None


class UserUpdatePartial(UserUpdate):
    pass



class UserOut(UserBase):
    oid: uuid.UUID
    is_active: bool
    is_superuser: bool
    create_at: datetime
    update_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserFilterParams(BaseModel):
    is_active: Optional[bool] = Field(None, description="Filter by active status")
    start_date: Optional[datetime] = Field(None, description="Filter by creation date start")
    end_date: Optional[datetime] = Field(None, description="Filter by creation date end")
    page: int = Field(1, ge=1, description="Page number")
    limit: int = Field(10, ge=1, le=100, description="Number of items per page")