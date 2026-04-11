"""Authentication business logic."""

from datetime import datetime, timedelta, timezone
from uuid import uuid4

from auth.password_utils import (
    hash_password,
    hash_token,
    validate_password_strength,
    verify_password,
)
from auth.token_service import TokenService
from config.config import Settings
from models.user.user import StoredToken, User
from schemas.auth import TokenResponse


class AuthService:
    def __init__(self):
        self.token_service = TokenService()
        self.refresh_expire_days = Settings().REFRESH_TOKEN_EXPIRE_DAYS
        self.access_expire_minutes = Settings().ACCESS_TOKEN_EXPIRE_MINUTES

    async def register(
        self,
        username: str,
        email: str,
        password: str,
        ip: str | None = None,
    ) -> tuple[User, TokenResponse]:
        """Register a new user and return tokens."""
        is_valid, msg = validate_password_strength(password)
        if not is_valid:
            raise ValueError(msg)

        if await User.find_one(User.email == email):
            raise ValueError("Email already registered")
        if await User.find_one(User.username == username):
            raise ValueError("Username already taken")

        user = User(
            username=username,
            email=email,
            password_hash=hash_password(password),
        )
        await user.insert()

        tokens = await self._generate_and_store_tokens(user, ip)
        return user, tokens

    async def login(
        self,
        email: str,
        password: str,
        ip: str | None = None,
    ) -> tuple[User, TokenResponse]:
        """Authenticate user and return tokens."""
        user = await User.find_one(User.email == email)
        # Use constant-time comparison to avoid timing attacks
        if not user or not verify_password(password, user.password_hash):
            raise ValueError("Invalid email or password")

        if not user.is_active:
            raise ValueError("Account is disabled")

        user.last_login = datetime.now(timezone.utc)
        await user.save()

        tokens = await self._generate_and_store_tokens(user, ip)
        return user, tokens

    async def refresh(
        self,
        refresh_token: str,
        ip: str | None = None,
    ) -> TokenResponse:
        """Rotate refresh token and return new token pair."""
        try:
            payload = self.token_service.decode_token(refresh_token)
        except ValueError:
            raise ValueError("Invalid or expired refresh token")

        if payload.get("type") != "refresh":
            raise ValueError("Invalid token type")

        user_id = payload.get("sub")
        user = await User.get(user_id)
        if not user or not user.is_active:
            raise ValueError("User not found or disabled")

        token_hash = hash_token(refresh_token)
        stored = next(
            (t for t in user.refresh_tokens if t.refresh_token_hash == token_hash),
            None,
        )
        if not stored:
            # Token hash not found → possible reuse of stolen token. Revoke all.
            user.refresh_tokens = []
            await user.save()
            raise ValueError("Refresh token revoked or already used")

        user.refresh_tokens.remove(stored)
        await user.save()

        return await self._generate_and_store_tokens(user, ip)

    async def logout(self, user_id: str) -> None:
        """Revoke all refresh tokens for the user (full logout)."""
        user = await User.get(user_id)
        if user:
            user.refresh_tokens = []
            await user.save()

    async def _generate_and_store_tokens(
        self,
        user: User,
        ip: str | None = None,
    ) -> TokenResponse:
        """Generate access + refresh token pair and persist refresh hash in DB."""
        family_id = str(uuid4())
        access_token = self.token_service.create_access_token(str(user.id))
        refresh_token = self.token_service.create_refresh_token(str(user.id), family_id)

        stored = StoredToken(
            token_family_id=family_id,
            refresh_token_hash=hash_token(refresh_token),
            expires_at=datetime.now(timezone.utc)
            + timedelta(days=self.refresh_expire_days),
            ip_address=ip,
        )

        user.refresh_tokens.append(stored)
        # Keep at most 5 concurrent sessions (drop oldest)
        if len(user.refresh_tokens) > 5:
            user.refresh_tokens = user.refresh_tokens[-5:]
        await user.save()

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=self.access_expire_minutes * 60,
        )
