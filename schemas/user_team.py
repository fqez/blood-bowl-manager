"""Schemas for user team endpoints."""

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field

# ============== Player Schemas ==============


class PlayerPerkResponse(BaseModel):
    """Perk owned by a player."""

    id: str
    name: str
    parameter: Optional[str] = None
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


class PlayerInjuryRecordResponse(BaseModel):
    """Historical injury, death or send-off for a player."""

    id: str
    type: str
    label: str
    notes: Optional[str] = None
    roll: Optional[int] = None
    stat: Optional[str] = None
    reduction: Optional[str] = None
    created_at: datetime


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
    advancements: int
    level: int
    injuries: list[str]
    injury_history: list[PlayerInjuryRecordResponse]
    spp: int
    status: str
    career: PlayerCareerResponse
    temporary_for_match: bool = False
    temporary_match_id: Optional[str] = None
    journeyman: bool = False
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
    temporary_for_match: bool = Field(default=False)
    temporary_match_id: Optional[str] = Field(default=None)
    mercenary: bool = Field(default=False)
    riotous_rookie: bool = Field(default=False)
    league_id: Optional[str] = Field(default=None)


class CreateTeamPlayerRequest(HirePlayerRequest):
    """Player to hire while creating a team."""


class HireStarPlayerRequest(BaseModel):
    """Request to hire a star player."""

    star_player_id: str = Field(..., description="Star player ID")
    name: Optional[str] = Field(
        None,
        max_length=50,
        description="Custom name (uses star player name if not provided)",
    )
    number: Optional[int] = Field(
        None, ge=1, le=99, description="Jersey number (auto-assigned if not provided)"
    )
    temporary_for_match: bool = Field(default=False)
    temporary_match_id: Optional[str] = Field(default=None)
    league_id: Optional[str] = Field(default=None)


class HirePlayerResponse(BaseModel):
    """Response after hiring a player."""

    player: UserPlayerResponse
    treasury_remaining: int
    team_value: int


class UpdatePlayerRequest(BaseModel):
    """Request to update a player."""

    name: Optional[str] = Field(None, max_length=50)
    number: Optional[int] = Field(None, ge=1, le=99)
    image: Optional[str] = Field(None, max_length=5_000_000)
    status: Optional[
        Literal[
            "healthy",
            "badly_hurt",
            "seriously_injured",
            "missing_next_game",
            "dead",
            "sent_off",
        ]
    ] = None
    injury_category: Optional[
        Literal["miss_next_game", "sent_off", "dead", "lasting_injury"]
    ] = None
    injury_note: Optional[str] = Field(None, max_length=500)
    lasting_injury_roll: Optional[int] = Field(None, ge=1, le=6)
    league_id: Optional[str] = None
    match_id: Optional[str] = None
    quick_match_id: Optional[str] = None


class AddPerkRequest(BaseModel):
    """Request to add a perk to a player."""

    perk_id: str
    perk_name: str
    parameter: Optional[str] = None
    category: Optional[str] = None
    league_id: Optional[str] = None


class ApplyPlayerAdvancementRequest(BaseModel):
    """Request to spend SPP on an official player advancement."""

    advancement_type: Literal[
        "random_primary_skill",
        "choose_primary_skill",
        "choose_secondary_skill",
        "characteristic_improvement",
    ]
    perk_id: Optional[str] = None
    skill_category: Optional[str] = None
    random_skill_first_d6: Optional[int] = Field(None, ge=1, le=6)
    random_skill_second_d6: Optional[int] = Field(None, ge=1, le=6)
    characteristic: Optional[Literal["MA", "ST", "AG", "PA", "AV"]] = None
    characteristic_roll: Optional[int] = Field(None, ge=1, le=8)
    league_id: Optional[str] = None


# ============== Team Schemas ==============


class CreateTeamRequest(BaseModel):
    """Request to create a new team."""

    base_roster_id: str = Field(..., description="Which race/roster to use")
    name: str = Field(..., min_length=1, max_length=50)
    players: list[CreateTeamPlayerRequest] = Field(default_factory=list, max_length=16)
    rerolls: int = Field(default=0, ge=0, le=8)
    cheerleaders: int = Field(default=0, ge=0, le=6)
    assistant_coaches: int = Field(default=0, ge=0, le=6)
    apothecary: bool = False
    dedicated_fans: int = Field(default=1, ge=1, le=3)
    favoured_of: Optional[str] = Field(default=None)


class UpdateTeamRequest(BaseModel):
    """Request to update team settings."""

    name: Optional[str] = Field(None, max_length=50)
    rerolls: Optional[int] = Field(None, ge=0, le=8)
    cheerleaders: Optional[int] = Field(None, ge=0, le=6)
    assistant_coaches: Optional[int] = Field(None, ge=0, le=6)
    apothecary: Optional[bool] = None
    fan_factor: Optional[int] = Field(None, ge=0, le=9)
    dedicated_fans: Optional[int] = Field(None, ge=1, le=7)
    treasury: Optional[int] = Field(None, ge=0)
    notes: Optional[str] = None
    favoured_of: Optional[str] = Field(default=None)
    league_id: Optional[str] = None
    commissioner_edit: bool = False


class TeamLeagueMembership(BaseModel):
    """League where a user team is enrolled."""

    id: str
    name: str
    status: str
    season: int


class TeamValueBreakdownResponse(BaseModel):
    """Official Team Value and Current Team Value components."""

    player_value: int
    unavailable_player_value: int
    reroll_value: int
    assistant_coach_value: int
    cheerleader_value: int
    apothecary_value: int
    sideline_staff_value: int
    treasury_value: int
    dedicated_fans_value: int
    team_value: int
    current_team_value: int


class UserTeamSummary(BaseModel):
    """Summary for team list."""

    id: str
    name: str
    base_roster_id: str
    team_value: int
    current_team_value: int
    treasury: int
    player_count: int
    can_manage_roster: bool = True
    share_code: str
    favoured_of: Optional[str] = None
    special_rules: list[str] = Field(default_factory=list)
    league_memberships: list[TeamLeagueMembership] = Field(default_factory=list)
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
    current_team_value: int
    team_value_breakdown: TeamValueBreakdownResponse
    rerolls: int
    reroll_cost: int  # From base roster
    fan_factor: int
    cheerleaders: int
    assistant_coaches: int
    apothecary: bool
    apothecary_allowed: bool  # From base roster
    dedicated_fans: int
    notes: str = ""
    share_code: str
    can_manage_roster: bool = True
    favoured_of: Optional[str] = None
    special_rules: list[str] = Field(default_factory=list)
    league_memberships: list[TeamLeagueMembership] = Field(default_factory=list)

    icon: Optional[str] = None
    wallpaper: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class BuyItemRequest(BaseModel):
    """Request to buy team items (rerolls, cheerleaders, etc.)."""

    item: str = Field(..., pattern="^(reroll|cheerleader|assistant_coach|apothecary)$")
    quantity: int = Field(default=1, ge=1)
