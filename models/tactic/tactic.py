"""Tactic document model for storing user kickoff formations."""

from datetime import datetime

from beanie import Document
from pydantic import BaseModel, Field


class PlacedPlayer(BaseModel):
    """A player placed on the pitch grid."""

    row: int = Field(..., ge=0, le=12)
    col: int = Field(..., ge=0, le=14)
    position_id: str


class Tactic(Document):
    """User-created kickoff formation tactic."""

    user_id: str
    name: str = Field(..., min_length=1, max_length=100)
    base_roster_id: str
    mode: str = Field(default="attack", pattern="^(attack|defense)$")

    # Grid placements
    placements: list[PlacedPlayer] = Field(default_factory=list)

    # "Good against" opponent teams
    good_against: list[str] = Field(default_factory=list)

    # Freeform notes
    notes: str = Field(default="", max_length=2000)

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "tactics"
