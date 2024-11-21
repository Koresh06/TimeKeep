import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from src.api.v1.auth.schemas import UserCreate
from src.api.v1.auth.service import AuthService


async def test_create_superuser(async_db_session: AsyncSession):
    email = "superuser@example.com"
    password = "password123"
    username = "superuser"
    full_name = "Super User"
    position = "superuser"
    role = "moderator"

    super_user = await AuthService(async_db_session).create_superuser(
            UserCreate(
                username=username,
                full_name=full_name,
                position=position,
                role=role,
                email=email,
                password=password
            )
        )
    
    assert super_user == f"Superuser created successfully.\nUsername: {username}"