from datetime import datetime
from typing import Generic, List, TypeVar
import uuid
from fastapi import Form
from pydantic import BaseModel, ConfigDict, Field


M = TypeVar("M")


class PaginatedResponse(BaseModel, Generic[M]):
    count: int = Field(description="Number of items returned in the response")
    items: List[M] = Field(
        description="List of items returned in the response following given criteria"
    )


class OrganizationBase(BaseModel):
    name: str
    name_boss: str
    position: str
    rank: str


class OrganizationCreate(OrganizationBase):

    @classmethod
    def as_form(
        cls,
        name: str = Form(...),
        name_boss: str = Form(...),
        position: str = Form(...),
        rank: str = Form(...),
    ):
        return cls(
            name=name,
            name_boss=name_boss,
            position=position,
            rank=rank,
        )


class OrganizationUpdate(OrganizationCreate):
    pass


class OrganizationUpdatePartil(OrganizationCreate):
    name: str | None = None
    name_boss: str | None = None
    position: str | None = None
    rank: str | None = None


class OrganizationOut(OrganizationBase):
    oid: uuid.UUID

    model_config = ConfigDict(from_attributes=True)
