import uuid
from typing import List, TypeVar, Generic, Optional
from fastapi import Form
from pydantic import BaseModel, ConfigDict, Field
from datetime import date, datetime

from api.v1.user.schemas import UserOut


M = TypeVar("M")


class PaginatedResponse(BaseModel, Generic[M]):
    count: int = Field(description="Number of items returned in the response")
    items: List[M] = Field(
        description="List of items returned in the response following given criteria"
    )


class OvertimeBase(BaseModel):
    o_date: date
    hours: int
    description: Optional[str] = None
    remaining_hours: Optional[int] = None
    is_used: bool = False
    create_at: Optional[datetime] = None


class OvertimeCreate(OvertimeBase):
    o_date: date
    hours: int
    description: str

    @classmethod
    def as_form(
        cls,
        o_date: date = Form(...),
        hours: int = Form(..., ge=1, le=24),
        description: str = Form(...),
    ) -> "OvertimeCreate":
        return cls(
            o_date=o_date,
            hours=hours,
            description=description,
        )


class OvertimeUpdate(OvertimeCreate):
    o_date: date | None = None
    description: str | None = None


class OvertimeUpdatePartial(BaseModel):
    o_date: Optional[date] = None
    description: Optional[str] = None

    @classmethod
    def as_form(
        cls,
        o_date: Optional[date] = Form(None),
        description: Optional[str] = Form(None),
    ) -> "OvertimeUpdatePartial":
        return cls(o_date=o_date, description=description)



class OvertimeOut(OvertimeBase):
    oid: uuid.UUID

    model_config = ConfigDict(from_attributes=True)


class OvertimeExtendedOut(OvertimeOut):
    user: UserOut

    model_config = ConfigDict(from_attributes=True)
