from fastapi import Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.errors import AppError, ErrorCode
from app.db.session import get_db
from app.models.user import User
from app.services.jwt_service import decode_access_token

security = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise AppError(
            message="Authentication required.",
            code=ErrorCode.AUTH_ERROR,
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    payload = decode_access_token(credentials.credentials)
    if payload is None:
        raise AppError(
            message="Invalid or expired token.",
            code=ErrorCode.AUTH_ERROR,
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    user_id = payload.get("sub")
    if user_id is None:
        raise AppError(
            message="Invalid token payload.",
            code=ErrorCode.AUTH_ERROR,
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    user = db.get(User, int(user_id))
    if user is None:
        raise AppError(
            message="User not found.",
            code=ErrorCode.AUTH_ERROR,
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    return user
