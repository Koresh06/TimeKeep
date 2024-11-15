from fastapi import Depends, APIRouter, HTTPException, Request, status
from fastapi_users.router.common import ErrorCode, ErrorModel
from fastapi_users import exceptions

from models.user import Role, User
from .schemas import UserCreate, UserRead, UserUpdate
from .users import UserManager, get_user_manager, role_required
from .users import auth_backend, fastapi_users
from .schemas import UserRead
from .users import current_active_user, current_superuser

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)


router.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/jwt",
)

# router.include_router(
#     fastapi_users.get_reset_password_router(),
# )

@router.post(
    "/register",
    response_model=UserRead,
    dependencies=[Depends(role_required(Role.MODERATOR))],
    status_code=status.HTTP_201_CREATED,
    tags=["auth"],
    name="register:register",
    description="Register a new user",
    responses={
            status.HTTP_400_BAD_REQUEST: {
                "model": ErrorModel,
                "content": {
                    "application/json": {
                        "examples": {
                            ErrorCode.REGISTER_USER_ALREADY_EXISTS: {
                                "summary": "A user with this email already exists.",
                                "value": {
                                    "detail": ErrorCode.REGISTER_USER_ALREADY_EXISTS
                                },
                            },
                            ErrorCode.REGISTER_INVALID_PASSWORD: {
                                "summary": "Password validation failed.",
                                "value": {
                                    "detail": {
                                        "code": ErrorCode.REGISTER_INVALID_PASSWORD,
                                        "reason": "Password should be"
                                        "at least 3 characters",
                                    }
                                },
                            },
                        }
                    }
                },
            },
        },
)
async def register_user(
    request: Request,
    user_create: UserCreate,
    user_manager: UserManager = Depends(get_user_manager)
):
    try:
        created_user = await user_manager.create(
            user_create, safe=True, request=request
        )
    except exceptions.UserAlreadyExists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorCode.REGISTER_USER_ALREADY_EXISTS,
        )
    except exceptions.InvalidPasswordException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": ErrorCode.REGISTER_INVALID_PASSWORD,
                "reason": e.reason,
            },
        )
    
    return UserRead.model_validate(created_user)


