import uuid
from typing import List, TypeVar, Generic
from fastapi import Form
from pydantic import BaseModel, ConfigDict, Field
from datetime import date

from api.v1.user.schemas import UserOut


M = TypeVar("M")


class PaginatedResponse(BaseModel, Generic[M]):
    count: int = Field(description="Number of items returned in the response")
    items: List[M] = Field(
        description="List of items returned in the response following given criteria"
    )


class OvertimeBase(BaseModel):
    o_date: date
    hours: int = Field(..., ge=1, le=24)
    description: str | None


class OvertimeCreate(OvertimeBase):
    o_date: date = Form(...)
    hours: int = Form(..., ge=1, le=24)
    description: str

    @classmethod
    def as_form(
        cls,
        o_date: date = Form(...),
        hours: int = Form(..., ge=1, le=24),
        description: str = Form(...),
    ):
        return cls(
            o_date=o_date,
            hours=hours,
            description=description,
        )


class OvertimeUpdate(OvertimeBase):
    o_date: date | None = None
    hours: int | None = None
    description: str | None = None


class OvertimeUpdatePartial(OvertimeUpdate):
    pass


class OvertimeOut(OvertimeBase):
    oid: uuid.UUID

    model_config = ConfigDict(from_attributes=True)


class OvertimeExtendedOut(OvertimeOut):
    user: UserOut

    model_config = ConfigDict(from_attributes=True)