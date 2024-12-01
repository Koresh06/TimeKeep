import uuid
from pydantic import BaseModel, ConfigDict
from datetime import date


class DayOffBase(BaseModel):
    user_oid: uuid.UUID
    o_date: date
    reason: str


class DayOffCreate(DayOffBase):
    pass


class DayOffUpdate(DayOffBase):
    user_oid: uuid.UUID | None = None
    o_date: date | None = None
    reason: str | None = None



class DayOffOut(DayOffBase):
    oid: uuid.UUID

    model_config = ConfigDict(from_attributes=True)


class DayOffUpdateStatus(BaseModel):
    oid: uuid.UUID
    is_approved: bool