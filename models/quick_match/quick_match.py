"""Standalone quick match model (not embedded in a league)."""

from datetime import datetime

from beanie import Document
from pydantic import Field

from models.league.league import Match


class QuickMatch(Document):
    """
    A standalone friendly match (not part of any league).

    Wraps the existing Match model inside a Beanie Document
    so it can be stored independently in MongoDB.
    """

    owner_id: str = Field(..., description="User who created the quick match")
    match: Match = Field(..., description="Embedded match data")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "quick_matches"

    class Config:
        use_enum_values = True
