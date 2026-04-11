"""Authentication endpoints: register, login, refresh, logout, me."""

from fastapi import APIRouter, Depends, HTTPException, Request, status

from auth.jwt_bearer import get_current_user
from models.user.user import User
from schemas.auth import (
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
    UserProfile,
)
from services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])

_service = AuthService()


@router.post(
    "/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED
)
async def register(req: RegisterRequest, request: Request):
    """Register a new user account."""
    try:
        _, tokens = await _service.register(
            username=req.username,
            email=req.email,
            password=req.password,
            ip=request.client.host if request.client else None,
        )
        return tokens
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/login", response_model=TokenResponse)
async def login(req: LoginRequest, request: Request):
    """Login with email and password."""
    try:
        _, tokens = await _service.login(
            email=req.email,
            password=req.password,
            ip=request.client.host if request.client else None,
        )
        return tokens
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(req: RefreshRequest, request: Request):
    """Rotate refresh token and return new access + refresh token pair."""
    try:
        tokens = await _service.refresh(
            refresh_token=req.refresh_token,
            ip=request.client.host if request.client else None,
        )
        return tokens
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(current_user_id: str = Depends(get_current_user)):
    """Logout: revoke all refresh tokens for the current user."""
    await _service.logout(current_user_id)


@router.get("/me", response_model=UserProfile)
async def get_me(current_user_id: str = Depends(get_current_user)):
    """Get the profile of the authenticated user."""
    user = await User.get(current_user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return UserProfile(
        user_id=str(user.id),
        username=user.username,
        email=str(user.email),
        fullname=user.fullname,
        avatar=user.avatar,
        team_ids=user.team_ids,
    )
