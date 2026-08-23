from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.rate_limit import ip_auth_limiter
from app.db.session import get_db
from app.schemas.auth import LoginRequest, SignupRequest, TokenResponse, UserOut
from app.services import auth_service

router = APIRouter()


@router.post(
    "/signup",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(ip_auth_limiter)],
)
def signup(
    data: SignupRequest,
    db: Session = Depends(get_db),
) -> UserOut:
    return auth_service.signup(db, data)


@router.post(
    "/login",
    response_model=TokenResponse,
    dependencies=[Depends(ip_auth_limiter)],
)
def login(
    data: LoginRequest,
    db: Session = Depends(get_db),
) -> TokenResponse:
    return auth_service.login(db, data)
