from fastapi import APIRouter, HTTPException, status

from ..schemas.auth import LoginRequest, TokenResponse
from ..security import authenticate_admin, create_access_token

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse, status_code=status.HTTP_200_OK)
def login(request: LoginRequest):
    if not authenticate_admin(request.username, request.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return TokenResponse(access_token=create_access_token(request.username))
