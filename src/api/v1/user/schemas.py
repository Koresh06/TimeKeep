from datetime import datetime
from typing import Generic, List, Optional, TypeVar
import uuid
from fastapi import Form
from pydantic import BaseModel, ConfigDict, Field, field_validator

from src.models import Role, WorkSchedule

from src.api.v1.department.schemas import DepartmentOut


M = TypeVar("M")


class PaginatedResponse(BaseModel, Generic[M]):
    count: int = Field(description="Number of items returned in the response")
    items: List[M] = Field(
        description="List of items returned in the response following given criteria"
    )
    total_pages: int = Field(description="Number of pages")
    current_page: int = Field(description="Current page number")


class UserBase(BaseModel):
    organization_oid: uuid.UUID | None = None
    department_oid: uuid.UUID | None = None
    username: str
    full_name: str
    position: str
    rank: str
    work_schedule: WorkSchedule = Field(
        ..., description="Work schedule type: 'daily' or 'shift'"
    )


class UserCreate(UserBase):
    password: str

    @field_validator("password")
    def validate_password(cls, value: str) -> str:
        if len(value) < 8:
            raise ValueError("Password must be at least 8 characters")
        return value

    @classmethod
    def as_form(
        cls,
        organization_oid: uuid.UUID = Form(...),
        department_oid: uuid.UUID = Form(...),
        username: str = Form(...),
        full_name: str = Form(...),
        position: str = Form(...),
        rank: str = Form(...),
        password: str = Form(...),
        work_schedule: WorkSchedule = Form(...),
    ):
        return cls(
            organization_oid=organization_oid,
            department_oid=department_oid,
            username=username,
            full_name=full_name,
            position=position,
            rank=rank,
            password=password,
            work_schedule=work_schedule,
        )


class UserUpdate(UserBase):
    organization_oid: uuid.UUID | None = None
    department_oid: uuid.UUID | None = None
    username: str | None = None
    full_name: str | None = None
    position: str | None = None
    rank: str | None = None
    role: Role | None = None
    work_schedule: WorkSchedule | None = None


class UserUpdatePartial(UserUpdate):
    pass


class UserOut(UserBase):
    oid: uuid.UUID
    is_active: bool
    create_at: datetime
    update_at: datetime
    # department_rel: Optional[DepartmentOut] = None

    model_config = ConfigDict(from_attributes=True)


class UserFilterParams(BaseModel):
    is_active: bool | None = Field(None, description="Filter by active status")
    start_date: datetime | None = Field(
        None, description="Filter by creation date start"
    )
    end_date: datetime | None = Field(None, description="Filter by creation date end")
    page: int = Field(1, ge=1, description="Page number")
    limit: int = Field(10, ge=1, le=100, description="Number of items per page")
