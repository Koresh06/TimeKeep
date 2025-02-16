from datetime import datetime
import uuid
from pydantic import BaseModel, ConfigDict


class DepartmentBase(BaseModel):
    name: str
    description: str


class DepartmentCreate(DepartmentBase):
    pass


class DepartmentUpdate(DepartmentCreate):
    pass


class DepartmentUpdatePartil(DepartmentCreate):
    name: str | None = None
    description: str | None = None


class DepartmentOut(DepartmentBase):
    oid: uuid.UUID

    model_config = ConfigDict(from_attributes=True)
    


