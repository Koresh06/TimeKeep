from fastapi import APIRouter, Depends

from models.user import Role, User


from ..auth.users import fastapi_users, role_required, current_active_user, current_superuser
from ..auth.schemas import UserRead, UserUpdate


router = APIRouter(
    prefix="/users",
    tags=["users"],
)


@router.get("/authenticated-route")
async def authenticated_route(user: User = Depends(role_required(Role.MODERATOR))):
    return {"message": f"Hello {user.username}!"}


@router.get("/superuser-route")
async def superuser_route(user: User = Depends(current_superuser)):
    return {"message": f"Hello superuser {user.username}!"}


router.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate)
)
