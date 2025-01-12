from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi_admin.app import app as admin_app
from fastapi_admin.providers.login import UsernamePasswordProvider

from models.admin import Admin
from core.session import async_session_maker

from .providers import LoginProvider


@asynccontextmanager
async def lifespan(app: FastAPI):
    await admin_app.configure(
        app=app,
        session_maker=async_session_maker,
        providers=[
            LoginProvider(
                login_logo_url="https://preview.tabler.io/static/logo.svg",
                admin_model=Admin,
            )
        ],
    )
    
    yield