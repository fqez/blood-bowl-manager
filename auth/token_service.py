"""JWT token generation and decoding."""

from datetime import datetime, timedelta, timezone

import jwt

from config.config import Settings


class TokenService:
    def __init__(self):
        settings = Settings()
        self.secret_key = settings.secret_key
        self.algorithm = settings.algorithm
        self.access_expire_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES
        self.refresh_expire_days = settings.REFRESH_TOKEN_EXPIRE_DAYS

    def create_access_token(self, user_id: str) -> str:
        """Create short-lived JWT access token (15 min by default)."""
        payload = {
            "sub": user_id,
            "type": "access",
            "exp": datetime.now(timezone.utc)
            + timedelta(minutes=self.access_expire_minutes),
            "iat": datetime.now(timezone.utc),
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def create_refresh_token(self, user_id: str, family_id: str) -> str:
        """Create long-lived JWT refresh token (7 days by default)."""
        payload = {
            "sub": user_id,
            "family_id": family_id,
            "type": "refresh",
            "exp": datetime.now(timezone.utc)
            + timedelta(days=self.refresh_expire_days),
            "iat": datetime.now(timezone.utc),
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def decode_token(self, token: str) -> dict:
        """Decode and verify a JWT. Raises ValueError on invalid/expired."""
        try:
            return jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
        except jwt.ExpiredSignatureError:
            raise ValueError("Token has expired")
        except jwt.InvalidTokenError:
            raise ValueError("Invalid token")
