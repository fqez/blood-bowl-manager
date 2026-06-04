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
    SENT_OFF = "sent_off"


class PlayerPerk(BaseModel):
    """A skill/perk owned by a player."""

    id: str
    name: str
    parameter: Optional[str] = None
    category: Optional[str] = None  # G, A, S, P, M


class PlayerStats(BaseModel):
    """Current player statistics (can be modified from base)."""

    MA: int = Field(..., ge=1, le=10)
    ST: int = Field(..., ge=1, le=8)
    AG: int = Field(..., ge=1, le=7)
    PA: Optional[int] = Field(None, ge=1, le=7)
    AV: int = Field(..., ge=3, le=12)


class PlayerCareer(BaseModel):
    """Career statistics for a player."""

    games: int = Field(default=0, ge=0)
    touchdowns: int = Field(default=0, ge=0)
    casualties: int = Field(default=0, ge=0)
    interceptions: int = Field(default=0, ge=0)
    completions: int = Field(default=0, ge=0)
    mvp_awards: int = Field(default=0, ge=0)


class PlayerInjuryRecord(BaseModel):
    """Historical injury, death or send-off recorded for a player."""

    id: str = Field(default_factory=lambda: uuid.uuid4().hex)
    type: str
    label: str
    notes: Optional[str] = None
    roll: Optional[int] = None
    stat: Optional[str] = None
    reduction: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class TeamValueBreakdown(BaseModel):
    """Official TV/CTV components. Treasury and Dedicated Fans do not count."""

    player_value: int = Field(default=0, ge=0)
    unavailable_player_value: int = Field(default=0, ge=0)
    reroll_value: int = Field(default=0, ge=0)
    assistant_coach_value: int = Field(default=0, ge=0)
    cheerleader_value: int = Field(default=0, ge=0)
    apothecary_value: int = Field(default=0, ge=0)
    sideline_staff_value: int = Field(default=0, ge=0)
    treasury_value: int = Field(default=0, ge=0)
    dedicated_fans_value: int = Field(default=0, ge=0)
    team_value: int = Field(default=0, ge=0)
    current_team_value: int = Field(default=0, ge=0)


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
    advancements: int = Field(default=0, ge=0, description="Advancements gained")
    injuries: list[str] = Field(default_factory=list, description="Permanent injuries")
    injury_history: list[PlayerInjuryRecord] = Field(default_factory=list)
    spp: int = Field(default=0, ge=0, description="Star Player Points")

    # Status
    status: PlayerStatus = Field(default=PlayerStatus.HEALTHY)
    career: PlayerCareer = Field(default_factory=PlayerCareer)

    # Temporary match-day players / Journeymen
    temporary_for_match: bool = Field(default=False)
    temporary_match_id: Optional[str] = None
    journeyman: bool = Field(default=False)

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
        default_factory=list,
        description="Hired players and temporary match-day players",
    )

    # Team resources
    treasury: int = Field(default=1_000_000, ge=0)
    team_value: int = Field(default=0, ge=0, description="Total team value")

    # Staff & extras
    rerolls: int = Field(default=0, ge=0, le=8)
    fan_factor: int = Field(default=0, ge=0, le=9)
    cheerleaders: int = Field(default=0, ge=0)
    assistant_coaches: int = Field(default=0, ge=0, le=6)
    apothecary: bool = Field(default=False)
    favoured_of: Optional[str] = None

    # Dedicated fans (for league play)
    dedicated_fans: int = Field(default=1, ge=0)

    # Coach notes
    notes: str = Field(default="")

    # Public sharing code. Detail lookups by this code never expose notes.
    share_code: Optional[str] = None

    # Visual customization
    icon: Optional[str] = None
    wallpaper: Optional[str] = None

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "user_teams"

    def calculate_team_value_breakdown(
        self,
        reroll_cost: int = 0,
        ignored_player_types: Optional[set[str]] = None,
    ) -> TeamValueBreakdown:
        """Calculate official TV and CTV from current roster state."""
        ignored_player_types = ignored_player_types or set()
        player_value = sum(
            p.current_value
            for p in self.players
            if (p.status.value if isinstance(p.status, PlayerStatus) else p.status)
            != PlayerStatus.DEAD.value
            and p.base_type not in ignored_player_types
        )
        unavailable_player_value = sum(
            p.current_value
            for p in self.players
            if (p.status.value if isinstance(p.status, PlayerStatus) else p.status)
            != PlayerStatus.DEAD.value
            and (p.status.value if isinstance(p.status, PlayerStatus) else p.status)
            != PlayerStatus.HEALTHY.value
            and p.base_type not in ignored_player_types
        )
        reroll_value = self.rerolls * reroll_cost
        assistant_coach_value = self.assistant_coaches * 10000
        cheerleader_value = self.cheerleaders * 10000
        apothecary_value = 50000 if self.apothecary else 0
        sideline_staff_value = (
            reroll_value + assistant_coach_value + cheerleader_value + apothecary_value
        )
        team_value = player_value + sideline_staff_value
        return TeamValueBreakdown(
            player_value=player_value,
            unavailable_player_value=unavailable_player_value,
            reroll_value=reroll_value,
            assistant_coach_value=assistant_coach_value,
            cheerleader_value=cheerleader_value,
            apothecary_value=apothecary_value,
            sideline_staff_value=sideline_staff_value,
            treasury_value=0,
            dedicated_fans_value=0,
            team_value=team_value,
            current_team_value=max(0, team_value - unavailable_player_value),
        )

    def calculate_team_value(
        self,
        reroll_cost: int = 0,
        ignored_player_types: Optional[set[str]] = None,
    ) -> int:
        """Calculate official full Team Value."""
        return self.calculate_team_value_breakdown(
            reroll_cost=reroll_cost,
            ignored_player_types=ignored_player_types,
        ).team_value

    @staticmethod
    def _is_dead_player(player: UserPlayer) -> bool:
        status = player.status.value if isinstance(player.status, PlayerStatus) else player.status
        return status == PlayerStatus.DEAD.value

    def permanent_player_count(self) -> int:
        """Count non-temporary, non-dead players on the Team Draft List."""
        return sum(
            1
            for p in self.players
            if not p.temporary_for_match and not self._is_dead_player(p)
        )

    def get_player_count_by_type(self, base_type: str) -> int:
        """Count how many living players of a specific type are hired."""
        return sum(
            1
            for p in self.players
            if p.base_type == base_type and not self._is_dead_player(p)
        )

    def can_hire_player(
        self, base_type: str, max_allowed: int, cost: int
    ) -> tuple[bool, str]:
        """Check if a player type can be hired."""
        if self.permanent_player_count() >= 16:
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
