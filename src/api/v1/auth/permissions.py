from typing import List, Union
from fastapi import Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from src.api.v1.auth.dependencies import get_current_user
from src.models.user import User, Role

class RoleRequired:
    def __init__(self, required_roles: Union[Role, List[Role]]):
        if isinstance(required_roles, Role):
            self.required_roles = [required_roles]
        else:
            self.required_roles = required_roles

    def __call__(self, user: User = Depends(get_current_user)) -> User:
        try:
            if user.role not in self.required_roles:
                raise HTTPException(status_code=403, detail="Not enough permissions")
            return user
        except HTTPException as e:
            print(e.detail)
            return RedirectResponse(url='/auth/', status_code=status.HTTP_302_FOUND)