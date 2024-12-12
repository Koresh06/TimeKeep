from typing import List, TypeVar, Generic
import uuid
from pydantic import BaseModel, ConfigDict, Field
from datetime import date

from api.v1.user.schemas import UserOut


M = TypeVar('M')

class PaginatedResponse(BaseModel, Generic[M]):
    count: int = Field(description='Number of items returned in the response')
    items: List[M] = Field(description='List of items returned in the response following given criteria')



class DayOffBase(BaseModel):
    o_date: date
    reason: str


class DayOffCreate(DayOffBase):
    pass


class DayOffUpdate(DayOffBase):
    o_date: date | None = None
    reason: str | None = None


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