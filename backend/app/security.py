"""Authentication helpers: bcrypt password check and JWT issue/verify.

There is no users table — a single admin account is configured via environment
variables (ADMIN_USERNAME, ADMIN_PASSWORD_HASH). Write endpoints depend on
``require_admin`` to validate the Bearer token.
"""

from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .config import settings

_bearer = HTTPBearer(auto_error=True)


def verify_password(plain_password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(plain_password.encode(), password_hash.encode())
    except ValueError:
        return False


def authenticate_admin(username: str, password: str) -> bool:
    return (
        username == settings.admin_username
        and verify_password(password, settings.admin_password_hash)
    )


def create_access_token(subject: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.access_token_expire_minutes
    )
    payload = {"sub": subject, "exp": expire}
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def require_admin(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
) -> str:
    """Validate the Bearer token and return the admin username."""
    invalid = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
        )
    except jwt.PyJWTError:
        raise invalid

    username = payload.get("sub")
    if username != settings.admin_username:
        raise invalid
    return username
