from datetime import datetime
import uuid
from pydantic import BaseModel, ConfigDict, Field, field_validator

from models import Role, WorkSchedule


class UserBase(BaseModel):
    department_oid: uuid.UUID = None
    username: str
    full_name: str
    position: str
    role: Role = Field(..., description="User role: 'user', 'moderator', 'superuser'")
    work_schedule: WorkSchedule = Field(..., description="Work schedule type: 'daily' or 'shift'")


class UserCreate(UserBase):
    password: str = Field(min_length=8) 

    @field_validator("password")
    def validate_password(cls, value: str) -> str:
        if len(value) < 8:
            raise ValueError("Password must be at least 8 characters")
        return value


class UserUpdate(UserBase):
    department_oid: uuid.UUID | None = None
    username: str | None = None
    full_name: str | None = None
    position: str | None = None
    role: Role | None = None


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
    is_active: bool | None = Field(None, description="Filter by active status")
    start_date: datetime | None = Field(None, description="Filter by creation date start")
    end_date: datetime | None = Field(None, description="Filter by creation date end")
    page: int = Field(1, ge=1, description="Page number")
    limit: int = Field(10, ge=1, le=100, description="Number of items per page")