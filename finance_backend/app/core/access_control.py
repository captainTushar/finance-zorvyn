from collections.abc import Callable

from fastapi import Depends, HTTPException, status

from ..dependencies import get_current_user
from ..models.user import User, UserRole


def require_role(*roles: UserRole) -> Callable:
    def role_dependency(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return current_user

    return role_dependency
