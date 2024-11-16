from fastapi import APIRouter, Depends

from models.user import Role, User


from ..auth.users import fastapi_users, role_required, current_active_user, current_superuser
from ..auth.schemas import UserRead, UserUpdate


router = APIRouter(
    prefix="/users",
    tags=["users"],
)


router.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate)
)
