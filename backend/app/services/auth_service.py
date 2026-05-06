from sqlalchemy.exc import IntegrityError
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import AppError, ErrorCode
from app.models.user import User
from app.schemas.auth import LoginRequest, RegisterRequest
from app.services.jwt_service import create_access_token
from app.services.security import hash_password, verify_password


def register_user(db: Session, payload: RegisterRequest) -> User:
    existing_user = db.scalar(select(User).where(User.email == payload.email))
    if existing_user is not None:
        raise AppError(
            message="Email already registered.",
            code=ErrorCode.RESOURCE_ERROR,
            status_code=409,
        )

    user = User(email=payload.email, password_hash=hash_password(payload.password))
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise AppError(
            message="Email already registered.",
            code=ErrorCode.RESOURCE_ERROR,
            status_code=409,
        )

    db.refresh(user)
    return user


def authenticate_user(db: Session, payload: LoginRequest) -> str:
    user = db.scalar(select(User).where(User.email == payload.email))
    if user is None or not verify_password(payload.password, user.password_hash):
        raise AppError(
            message="Invalid email or password.",
            code=ErrorCode.AUTH_ERROR,
            status_code=401,
        )

    return create_access_token(data={"sub": str(user.id)})
