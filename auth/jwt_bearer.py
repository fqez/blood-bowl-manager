from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> str | None:
        credentials: HTTPAuthorizationCredentials | None = await super().__call__(
            request
        )
        if not credentials:
            return None
        if credentials.scheme != "Bearer":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid authentication scheme",
            )
        return credentials.credentials


async def get_current_user(token: str = Depends(JWTBearer())) -> str:
    """FastAPI dependency: validates JWT and returns user_id (sub claim)."""
    from auth.token_service import TokenService

    try:
        payload = TokenService().decode_token(token)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )

    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid token type",
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    return user_id


async def get_current_user_optional(
    token: str | None = Depends(JWTBearer(auto_error=False)),
) -> str | None:
    """Best-effort JWT validation for routes that can fall back to other auth data."""
    if not token:
        return None

    from auth.token_service import TokenService

    try:
        payload = TokenService().decode_token(token)
    except ValueError:
        return None

    if payload.get("type") != "access":
        return None

    user_id = payload.get("sub")
    return user_id if user_id else None
