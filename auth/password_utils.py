"""Password hashing and validation utilities."""

import hashlib

import bcrypt


def hash_password(password: str) -> str:
    """Hash a password with bcrypt (auto salt)."""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=12)).decode()


def verify_password(plain: str, hashed: str) -> bool:
    """Verify a plain password against a bcrypt hash."""
    return bcrypt.checkpw(plain.encode(), hashed.encode())


def hash_token(token: str) -> str:
    """SHA-256 hash for refresh tokens (stored in DB, never in clear)."""
    return hashlib.sha256(token.encode()).hexdigest()


def validate_password_strength(password: str) -> tuple[bool, str]:
    """Validate password meets minimum security requirements."""
    if len(password) < 8:
        return False, "Password must be at least 8 characters"
    if not any(c.isupper() for c in password):
        return False, "Password must contain at least one uppercase letter"
    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least one number"
    if not any(c in "!@#$%^&*()-_=+[]{}|;:,.<>?" for c in password):
        return False, "Password must contain at least one special character"
    return True, "Valid"
