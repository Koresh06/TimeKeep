import uuid
from fastapi import Form
from pydantic import BaseModel



class Token(BaseModel):
    access_token: str
    token_type: str


class TokenPayload(BaseModel):
    user_oid: uuid.UUID


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginForm(BaseModel):
    username: str
    password: str 

    @classmethod
    def as_form(cls, 
                username: str = Form(...), 
                password: str = Form(...)) -> "LoginForm":
        
        return cls(username=username, password=password)

