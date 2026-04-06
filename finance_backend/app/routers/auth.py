from pydantic import BaseModel, EmailStr
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas.user import Token
from ..services.auth_service import create_access_token
from ..services.user_service import authenticate_user


router = APIRouter(prefix="/api/auth", tags=["Auth"])


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


@router.post("/login", response_model=Token)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> Token:
    user = authenticate_user(db, payload.email, payload.password)
    token = create_access_token(subject=user.email)
    return Token(access_token=token)
