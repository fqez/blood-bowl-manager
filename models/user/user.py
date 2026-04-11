"""User models."""

from datetime import datetime
from typing import Optional

from beanie import Document
from pydantic import BaseModel, EmailStr, Field


class StoredToken(BaseModel):
    """Refresh token stored in the DB (only the hash, never the token itself)."""

    token_family_id: str
    refresh_token_hash: str  # SHA-256 of the refresh token
    expires_at: datetime
    issued_at: datetime = Field(default_factory=datetime.utcnow)
    ip_address: Optional[str] = None


class UserTeamRef(BaseModel):
    """Reference to a user's team (for quick listing)."""

    team_id: str
    team_name: str
    base_roster_id: str
    icon: Optional[str] = None


class UserLeagueRef(BaseModel):
    """Reference to a league the user is participating in."""

    league_id: str
    league_name: str
    team_id: str  # Which team is in this league
    team_name: str


class User(Document):
    """
    User account.

    Teams and leagues are referenced (not embedded) since:
    - User can have multiple teams
    - User can be in multiple leagues with different teams
    - Teams/leagues have their own documents
    """

    username: str = Field(..., min_length=3, max_length=30)
    email: EmailStr
    password_hash: str = Field(..., exclude=True)  # Never serialize
    fullname: Optional[str] = Field(None, max_length=100)
    avatar: Optional[str] = None
    is_active: bool = True

    # Refresh tokens (hashed, max 5 concurrent sessions)
    refresh_tokens: list[StoredToken] = Field(default_factory=list)

    # References (denormalized for quick access)
    team_ids: list[str] = Field(default_factory=list, description="IDs of owned teams")

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None

    class Settings:
        name = "users"

    class Config:
        json_schema_extra = {
            "example": {
                "username": "skull_crusher",
                "email": "skull@crusher.com",
                "fullname": "Skull Crusher",
                "team_ids": ["team_xyz789", "team_abc456"],
            }
        }


class UserPublic(BaseModel):
    """Public user information (safe to expose)."""

    id: str
    username: str
    fullname: Optional[str] = None
    avatar: Optional[str] = None


class UserData(BaseModel):
    """User data for registration/update."""

    fullname: str
    username: str
    email: EmailStr
    avatar: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "fullname": "Skull Crusher",
                "username": "skull99",
                "email": "skull@crusher.com",
                "avatar": "avatar/skull99.png",
            }
        }
