from datetime import datetime
import uuid
from typing import Optional
from fastapi import Request
from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenPayload(BaseModel):
    user_oid: uuid.UUID


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    oid: uuid.UUID
    username: str
    is_admin: bool
    create_at: datetime
    update_at: datetime

    class Config:
        from_attributes = True


class LoginForm:
    def __init__(self, request: Request) -> None:
        self.request: Request = request
        self.username: Optional[str] = None
        self.password: Optional[str] = None


    async def create_oauth_form(self):
        form = await self.request.form()
        self.username = form.get("username")
        self.password = form.get("password")