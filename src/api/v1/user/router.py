from typing import Annotated, List
from fastapi import APIRouter, Depends, Query, status, Request, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession

from models.user import Role, User
from core.session import get_async_session
from api.conf_static import templates
from api.v1.auth.permissions import RoleRequired
from api.v1.auth.dependencies import get_current_user
from api.v1.department.service import DepartmentService
from .service import UserService
from .schemas import (
    UserOut,
    UserCreate,
    UserFilterParams,
    UserUpdatePartial,
    UserUpdate,
)
from .dependencies import user_by_oid


router = APIRouter(
    prefix="/user",
    tags=["user"],
)


@router.get(
    "/register",
    response_class=HTMLResponse,
    status_code=status.HTTP_200_OK,
    name="users:register",
    description="Register page",
)
async def register_page(
    request: Request,
    session: Annotated[
        AsyncSession,
        Depends(get_async_session),
    ],
):
    departments = await DepartmentService(session).get_all()

    return templates.TemplateResponse(
        request=request,
        name="register.html",
        context={
            "departments": departments,
        },
    )


@router.post(
    "/register",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED,
    name="users:register",
    description="Create user",
)
async def register(
    request: Request,
    session: Annotated[
        AsyncSession,
        Depends(get_async_session),
    ],
    user_create: UserCreate = Depends(UserCreate.as_form),
):
    print(user_create)
    try:
        await UserService(session).create(data=user_create)

        return templates.TemplateResponse(
            request=request,
            name="auth.html",
        )
    except HTTPException as e:
        departments = await DepartmentService(session).get_all()

        return templates.TemplateResponse(
            request=request,
            name="register.html",
            context={
                "msg": e.detail,
                "departments": departments,
            },
        )


@router.get(
    "/",
    response_model=List[UserOut],
    dependencies=[Depends(RoleRequired([Role.SUPERUSER, Role.MODERATOR]))],
    status_code=status.HTTP_200_OK,
    name="users:get_all",
    description="Get all users with filters and pagination",
)
async def get_all(
    session: Annotated[
        AsyncSession,
        Depends(get_async_session),
    ],
    filters_params: UserFilterParams = Depends(),
):
    return await UserService(session).get_all(filters_params=filters_params)


@router.get(
    "/me",
    response_model=UserOut,
    dependencies=[Depends(RoleRequired([Role.SUPERUSER, Role.MODERATOR, Role.USER]))],
    status_code=status.HTTP_200_OK,
    name="users:me",
    description="Get current user",
)
async def get_me(
    user: Annotated[
        User,
        Depends(get_current_user),
    ]
):
    return UserOut.model_validate(user)


@router.get(
    "/{oid}",
    response_model=UserOut,
    dependencies=[Depends(RoleRequired([Role.SUPERUSER, Role.MODERATOR]))],
    status_code=status.HTTP_200_OK,
    name="users:get_one",
    description="Get one user by id",
)
async def get_one(
    user: UserOut = Depends(user_by_oid),
):
    return user


@router.patch(
    "/{oid}",
    response_model=UserOut,
    dependencies=[Depends(RoleRequired(Role.SUPERUSER))],
    status_code=status.HTTP_200_OK,
    name="users:modify",
    description="Modify user by id",
)
async def modify(
    session: Annotated[
        AsyncSession,
        Depends(get_async_session),
    ],
    user_update: UserUpdatePartial,
    user: User = Depends(user_by_oid),
):
    return await UserService(session).modify(
        user=user,
        user_update=user_update,
        partil=True,
    )


@router.put(
    "/{oid}",
    response_model=UserOut,
    dependencies=[Depends(RoleRequired(Role.SUPERUSER))],
    status_code=status.HTTP_200_OK,
    name="users:replace",
    description="Replace user by id",
)
async def replace(
    session: Annotated[
        AsyncSession,
        Depends(get_async_session),
    ],
    user_update: UserUpdate,
    user: User = Depends(user_by_oid),
):
    return await UserService(session).replace(
        user=user,
        user_update=user_update,
        partil=False,
    )


@router.delete(
    "/{oid}",
    dependencies=[Depends(RoleRequired(Role.SUPERUSER))],
    status_code=status.HTTP_204_NO_CONTENT,
    name="users:delete",
    description="Delete user by id",
)
async def delete(
    session: Annotated[
        AsyncSession,
        Depends(get_async_session),
    ],
    user: User = Depends(user_by_oid),
):
    await UserService(session).delete(user=user)


@router.post(
    "/toggle-role/{oid}",
    dependencies=[Depends(RoleRequired(Role.SUPERUSER))],
    response_model=UserOut,
    status_code=status.HTTP_200_OK,
    name="users:toggle-role",
    description="Toggle user's role between USER and MODERATOR on each call",
)
async def toggle(
    session: Annotated[
        AsyncSession,
        Depends(get_async_session),
    ],
    user: User = Depends(user_by_oid),
    role: Role = Query(Role),
):
    return await UserService(session).toggle_role(user=user, role=role)
