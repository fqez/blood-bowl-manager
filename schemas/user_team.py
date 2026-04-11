"""Schemas for user team endpoints."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

# ============== Player Schemas ==============


class PlayerPerkResponse(BaseModel):
    """Perk owned by a player."""

    id: str
    name: str
    category: Optional[str] = None


class PlayerStatsResponse(BaseModel):
    """Player stats for display."""

    MA: int
    ST: int
    AG: str  # "4+" format
    PA: Optional[str]  # "6+" or "-"
    AV: str  # "8+" format


class PlayerCareerResponse(BaseModel):
    """Career statistics."""

    games: int
    touchdowns: int
    casualties: int
    interceptions: int
    completions: int
    mvp_awards: int


class UserPlayerResponse(BaseModel):
    """Player in a user's team."""

    id: str
    base_type: str
    name: str
    number: int
    current_value: int
    stats: PlayerStatsResponse
    perks: list[PlayerPerkResponse]
    stat_increases: dict[str, int]
    injuries: list[str]
    spp: int
    status: str
    career: PlayerCareerResponse
    image: Optional[str] = None


class HirePlayerRequest(BaseModel):
    """Request to hire a new player."""

    base_type: str = Field(..., description="Player type from base roster")
    name: Optional[str] = Field(
        None, max_length=50, description="Custom name (auto-generated if not provided)"
    )
    number: Optional[int] = Field(
        None, ge=1, le=99, description="Jersey number (auto-assigned if not provided)"
    )


class HirePlayerResponse(BaseModel):
    """Response after hiring a player."""

    player: UserPlayerResponse
    treasury_remaining: int
    team_value: int


class UpdatePlayerRequest(BaseModel):
    """Request to update a player."""

    name: Optional[str] = Field(None, max_length=50)
    number: Optional[int] = Field(None, ge=1, le=99)


class AddPerkRequest(BaseModel):
    """Request to add a perk to a player."""

    perk_id: str
    perk_name: str
    category: Optional[str] = None


# ============== Team Schemas ==============


class CreateTeamRequest(BaseModel):
    """Request to create a new team."""

    base_roster_id: str = Field(..., description="Which race/roster to use")
    name: str = Field(..., min_length=1, max_length=50)


class UpdateTeamRequest(BaseModel):
    """Request to update team settings."""

    name: Optional[str] = Field(None, max_length=50)
    rerolls: Optional[int] = Field(None, ge=0, le=8)
    cheerleaders: Optional[int] = Field(None, ge=0, le=12)
    assistant_coaches: Optional[int] = Field(None, ge=0, le=6)
    apothecary: Optional[bool] = None
    fan_factor: Optional[int] = Field(None, ge=0, le=9)


class UserTeamSummary(BaseModel):
    """Summary for team list."""

    id: str
    name: str
    base_roster_id: str
    team_value: int
    treasury: int
    player_count: int
    icon: Optional[str] = None
    created_at: datetime


class UserTeamDetail(BaseModel):
    """Full team detail with players."""

    id: str
    user_id: str
    base_roster_id: str
    name: str

    players: list[UserPlayerResponse]

    treasury: int
    team_value: int
    rerolls: int
    reroll_cost: int  # From base roster
    fan_factor: int
    cheerleaders: int
    assistant_coaches: int
    apothecary: bool
    apothecary_allowed: bool  # From base roster
    dedicated_fans: int

    icon: Optional[str] = None
    wallpaper: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class BuyItemRequest(BaseModel):
    """Request to buy team items (rerolls, cheerleaders, etc.)."""

    item: str = Field(..., pattern="^(reroll|cheerleader|assistant_coach|apothecary)$")
    quantity: int = Field(default=1, ge=1)
