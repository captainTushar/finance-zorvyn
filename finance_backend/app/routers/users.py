from typing import Annotated

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from ..core.access_control import require_role
from ..database import get_db
from ..dependencies import get_current_user
from ..models.user import User, UserRole
from ..schemas.user import UserCreate, UserRead, UserUpdate
from ..services import user_service


router = APIRouter(prefix="/api/users", tags=["Users"])


@router.get("/me", response_model=UserRead)
def get_me(current_user: User = Depends(get_current_user)) -> User:
    return current_user


@router.get("", response_model=list[UserRead])
def list_users(
    page: int = 1,
    limit: int = 10,
    db: Session = Depends(get_db),
    _: User = Depends(require_role(UserRole.admin)),
) -> list[User]:
    return user_service.list_users(db, page=page, limit=limit)


@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(
    payload: UserCreate,
    db: Annotated[Session, Depends(get_db)],
    _: User = Depends(require_role(UserRole.admin)),
) -> User:
    return user_service.create_user(db, payload)


@router.patch("/{user_id}", response_model=UserRead)
def update_user(
    user_id: int,
    payload: UserUpdate,
    db: Annotated[Session, Depends(get_db)],
    _: User = Depends(require_role(UserRole.admin)),
) -> User:
    return user_service.update_user(db, user_id, payload)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def deactivate_user(
    user_id: int,
    db: Annotated[Session, Depends(get_db)],
    _: User = Depends(require_role(UserRole.admin)),
) -> Response:
    user_service.deactivate_user(db, user_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
