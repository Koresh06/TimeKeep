import uuid
from typing import List, TypeVar, Generic
from pydantic import BaseModel, ConfigDict, Field
from datetime import date


M = TypeVar('M')

class PaginatedResponse(BaseModel, Generic[M]):
    count: int = Field(description='Number of items returned in the response')
    items: List[M] = Field(description='List of items returned in the response following given criteria')


class OvertimeBase(BaseModel):
    user_oid: uuid.UUID
    o_date: date
    hours: int
    description: str | None



class OvertimeCreate(OvertimeBase):
    pass


class OvertimeUpdate(OvertimeBase):
    user_oid: uuid.UUID | None = None
    o_date: date | None = None
    hours: int | None = None
    description: str | None = None


class OvertimeUpdatePartial(OvertimeUpdate):
    pass


class OvertimeOut(OvertimeBase):
    oid: uuid.UUID

    model_config = ConfigDict(from_attributes=True)