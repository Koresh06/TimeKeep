from datetime import datetime
import uuid
from pydantic import BaseModel, ConfigDict


class DepartmentBase(BaseModel):
    name: str
    description: str
    # create_at: datetime
    # update_at: datetime


class DepartmentCreate(DepartmentBase):
    pass


class DepartmentUpdate(DepartmentCreate):
    pass


class DepartmentUpdatePartil(DepartmentCreate):
    name: str | None = None
    description: str | None = None


class DepartmentOut(DepartmentBase):
    id: uuid.UUID

    model_config = ConfigDict(from_attributes=True)

