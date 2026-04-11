"""User team models - Mutable team data with embedded players."""

import uuid
from datetime import datetime
from enum import Enum
from typing import Optional

from beanie import Document
from pydantic import BaseModel, Field


class PlayerStatus(str, Enum):
    """Player availability status."""

    HEALTHY = "healthy"
    BADLY_HURT = "badly_hurt"
    SERIOUSLY_INJURED = "seriously_injured"
    DEAD = "dead"
    MISSING_NEXT_GAME = "missing_next_game"


class PlayerPerk(BaseModel):
    """A skill/perk owned by a player."""

    id: str
    name: str
    category: Optional[str] = None  # G, A, S, P, M


class PlayerStats(BaseModel):
    """Current player statistics (can be modified from base)."""

    MA: int = Field(..., ge=1, le=10)
    ST: int = Field(..., ge=1, le=8)
    AG: int = Field(..., ge=1, le=6)
    PA: Optional[int] = Field(None, ge=1, le=6)
    AV: int = Field(..., ge=3, le=12)


class PlayerCareer(BaseModel):
    """Career statistics for a player."""

    games: int = Field(default=0, ge=0)
    touchdowns: int = Field(default=0, ge=0)
    casualties: int = Field(default=0, ge=0)
    interceptions: int = Field(default=0, ge=0)
    completions: int = Field(default=0, ge=0)
    mvp_awards: int = Field(default=0, ge=0)


class UserPlayer(BaseModel):
    """
    A player owned by a user (embedded in UserTeam).

    Contains copied stats/perks from base that can be modified
    through progression, injuries, and skill purchases.
    """

    id: str = Field(default_factory=lambda: uuid.uuid4().hex)
    base_type: str = Field(..., description="Reference to base player type")
    name: str = Field(..., min_length=1, max_length=50)
    number: int = Field(..., ge=1, le=99)

    # Current values (copied from base, modified over time)
    current_value: int = Field(..., ge=0, description="Current player value in gold")
    stats: PlayerStats
    perks: list[PlayerPerk] = Field(default_factory=list)

    # Progression tracking
    stat_increases: dict[str, int] = Field(
        default_factory=dict, description="Stat improvements purchased"
    )
    injuries: list[str] = Field(default_factory=list, description="Permanent injuries")
    spp: int = Field(default=0, ge=0, description="Star Player Points")

    # Status
    status: PlayerStatus = Field(default=PlayerStatus.HEALTHY)
    career: PlayerCareer = Field(default_factory=PlayerCareer)

    # Visual
    image: Optional[str] = None
    tag_image: Optional[str] = None

    class Config:
        use_enum_values = True


class UserTeam(Document):
    """
    A team owned by a user with all players embedded.

    Players are stored directly in this document since:
    - A team has max 16 players (bounded array)
    - Players are always accessed with their team
    - Updates to players need to be atomic with team
    """

    # Identity
    user_id: str = Field(..., description="Owner user ID")
    base_roster_id: str = Field(..., description="Reference to base roster")
    name: str = Field(..., min_length=1, max_length=50)

    # Roster (embedded, max 16)
    players: list[UserPlayer] = Field(
        default_factory=list, max_length=16, description="Hired players"
    )

    # Team resources
    treasury: int = Field(default=1_000_000, ge=0)
    team_value: int = Field(default=0, ge=0, description="Total team value")

    # Staff & extras
    rerolls: int = Field(default=0, ge=0, le=8)
    fan_factor: int = Field(default=0, ge=0, le=9)
    cheerleaders: int = Field(default=0, ge=0, le=12)
    assistant_coaches: int = Field(default=0, ge=0, le=6)
    apothecary: bool = Field(default=False)

    # Dedicated fans (for league play)
    dedicated_fans: int = Field(default=1, ge=1, le=6)

    # Visual customization
    icon: Optional[str] = None
    wallpaper: Optional[str] = None

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "user_teams"

    def calculate_team_value(self) -> int:
        """Calculate total team value from players and extras."""
        player_value = sum(p.current_value for p in self.players)
        # Note: rerolls counted at current cost (double during season)
        return player_value

    def get_player_count_by_type(self, base_type: str) -> int:
        """Count how many players of a specific type are hired."""
        return sum(1 for p in self.players if p.base_type == base_type)

    def can_hire_player(
        self, base_type: str, max_allowed: int, cost: int
    ) -> tuple[bool, str]:
        """Check if a player type can be hired."""
        if len(self.players) >= 16:
            return False, "Roster is full (max 16 players)"

        current_count = self.get_player_count_by_type(base_type)
        if current_count >= max_allowed:
            return False, f"Maximum {base_type} reached ({max_allowed})"

        if self.treasury < cost:
            return False, f"Insufficient treasury ({self.treasury} < {cost})"

        return True, "OK"

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user_abc123",
                "base_roster_id": "shambling-undead",
                "name": "Los Putrefactos FC",
                "treasury": 850000,
                "team_value": 150000,
                "rerolls": 2,
                "players": [
                    {
                        "id": "p001",
                        "base_type": "skeleton-lineman",
                        "name": "Huesos McGee",
                        "number": 7,
                        "current_value": 50000,
                        "stats": {"MA": 5, "ST": 3, "AG": 4, "PA": 6, "AV": 8},
                        "perks": [
                            {"id": "regeneration", "name": "Regeneration"},
                            {"id": "block", "name": "Block"},
                        ],
                        "spp": 16,
                        "status": "healthy",
                    }
                ],
            }
        }
