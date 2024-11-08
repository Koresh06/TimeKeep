from datetime import datetime
import uuid
from typing import Optional
from fastapi import Form
from pydantic import BaseModel, ConfigDict


class UserCreateSchema(BaseModel):
    oid: uuid.UUID
    department_oid: uuid.UUID
    username: str
    password: str

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "oid": "uuid",
                    "department_oid": "uuid",
                    "username": "username",
                    "password": "password",
                }
            ]
        }
    }

    @classmethod    
    def as_form(
        cls,
        oid: uuid.UUID = Form(...),
        department_oid: uuid.UUID = Form(...),
        username: str = Form(...),
        password: str = Form(...),
    ):
        return cls(
            oid=oid,
            department_oid=department_oid,
            username=username,
            password=password,
        )


class UserUpdateSchema(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None
    is_admin: Optional[bool] = None


class UserResponseSchema(BaseModel):
    oid: uuid.UUID
    username: str
    _hashed_password: str
    is_admin: bool
    is_superuser: bool
    create_at: datetime
    update_at: datetime

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "oid": "uuid",
                    "username": "username",
                    "is_admin": True,
                    "is_superuser": True,
                    "create_at": "2023-05-27T16:22:54.231",
                }
            ]
        }
    }
    