from datetime import datetime
import uuid
from fastapi import Form
from pydantic import BaseModel, ConfigDict


class DepartmentBase(BaseModel):
    name: str
    description: str
    organization_oid: uuid.UUID


class DepartmentCreate(DepartmentBase):
    @classmethod
    def as_form(
        cls,
        name: str = Form(...),
        description: str = Form(...),
        organization_oid: uuid.UUID = Form(...),

    ):
        return cls(
            name=name,
            description=description,
            organization_oid=organization_oid,
        )


class DepartmentUpdate(DepartmentCreate):
    pass


class DepartmentUpdatePartil(DepartmentCreate):
    name: str | None = None
    description: str | None = None


class DepartmentOut(DepartmentBase):
    oid: uuid.UUID

    model_config = ConfigDict(from_attributes=True)
    


