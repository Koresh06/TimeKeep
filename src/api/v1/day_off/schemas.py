from typing import List, TypeVar, Generic, Optional
import uuid
from fastapi import Form
from pydantic import BaseModel, ConfigDict, Field
from datetime import date, datetime

from api.v1.user.schemas import UserOut


M = TypeVar('M')

class PaginatedResponse(BaseModel, Generic[M]):
    count: int = Field(description='Number of items returned in the response')
    items: List[M] = Field(description='List of items returned in the response following given criteria')



class DayOffBase(BaseModel):
    o_date: date
    reason: str
    is_approved: Optional[bool] = False
    create_at: Optional[datetime] = None


class DayOffCreate(DayOffBase):
    o_date: date = Form(...)
    reason: str = Form(...)

    @classmethod
    def as_form(
        cls,
        o_date: date = Form(...),
        reason: str = Form(...),
    ):
        return cls(
            o_date=o_date,
            reason=reason,
        )


class DayOffUpdate(DayOffCreate):
    o_date: date | None = None
    reason: str | None = None
    is_approved: bool | None = None


class DayOffUpdatePartil(DayOffUpdate):
    pass



class DayOffOut(DayOffBase):
    oid: uuid.UUID

    model_config = ConfigDict(from_attributes=True)


class DayOffExtendedOut(DayOffOut):
    user: UserOut

    model_config = ConfigDict(from_attributes=True)


class DayOffUpdateStatus(BaseModel):
    oid: uuid.UUID
    is_approved: bool