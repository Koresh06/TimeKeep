import uuid
from pydantic import BaseModel, ConfigDict


class OrganizationBase(BaseModel):
    name: str
    name_boss: str
    position: str
    rank: str


class OrganizationCreate(OrganizationBase):
    pass


class OrganizationUpdate(OrganizationCreate):
    pass


class OrganizationUpdatePartil(OrganizationCreate):
    name: str | None = None
    name_boss: str | None = None
    position: str | None = None
    rank: str | None = None

    model_config = ConfigDict(from_attributes=True)


class OrganizationOut(OrganizationBase):
    oid: uuid.UUID

    model_config = ConfigDict(from_attributes=True)

