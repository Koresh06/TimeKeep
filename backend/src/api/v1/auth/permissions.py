from fastapi import HTTPException, Depends
from models.user import User, Role
from .dependencies import get_current_user


class RoleRequired:
    def __init__(self, required_role: Role):
        self.required_role = required_role

    def __call__(self, user: User = Depends(get_current_user)) -> User:
        if user.role != self.required_role:
            raise HTTPException(status_code=403, detail="Not enough permissions")
        return user
