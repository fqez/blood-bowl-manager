"""Schemas for league endpoints."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

# ============== League Team/Standing Schemas ==============


class LeagueTeamResponse(BaseModel):
    """Team participating in a league."""

    team_id: str
    team_name: str
    user_id: str
    username: str
    base_roster_id: str
    icon: Optional[str] = None
    joined_at: datetime


class LeagueStandingResponse(BaseModel):
    """Team standing in a league."""

    team_id: str
    team_name: str
    wins: int
    draws: int
    losses: int
    points: int
    touchdowns_for: int
    touchdowns_against: int
    touchdown_diff: int
    casualties_for: int
    casualties_against: int
    games_played: int


# ============== Match Schemas ==============


class MatchTeamResponse(BaseModel):
    """Team info in a match."""

    team_id: str
    team_name: str
    user_id: str = ""
    username: str
    base_roster_id: str = ""


class MatchEventResponse(BaseModel):
    """Event during a match."""

    id: str
    type: str
    team: str
    player_id: Optional[str] = None
    player_name: Optional[str] = None
    victim_id: Optional[str] = None
    victim_name: Optional[str] = None
    injury: Optional[str] = None
    detail: Optional[str] = None
    half: int
    turn: int
    timestamp: Optional[datetime] = None
    created_by: Optional[str] = None
    created_by_name: Optional[str] = None


class MatchSummary(BaseModel):
    """Match summary for list."""

    id: str
    round: int
    home: MatchTeamResponse
    away: MatchTeamResponse
    status: str
    score_home: int
    score_away: int
    weather: Optional[str] = None
    kickoff_event: Optional[str] = None
    current_half: int = 0
    current_turn: int = 0
    started_at: Optional[datetime] = None
    scheduled_at: Optional[datetime] = None
    played_at: Optional[datetime] = None


class FlatMatchResponse(BaseModel):
    """Flat match response compatible with the frontend Match model."""

    id: str
    league_id: str
    round: int
    home_team_id: str
    home_team_name: str
    away_team_id: str
    away_team_name: str
    home_score: int
    away_score: int
    status: str
    played_at: Optional[datetime] = None


class MatchDetail(BaseModel):
    """Full match detail."""

    id: str
    round: int
    home: MatchTeamResponse
    away: MatchTeamResponse
    status: str
    score_home: int
    score_away: int
    weather: Optional[str] = None
    kickoff_event: Optional[str] = None
    home_ready: bool = False
    away_ready: bool = False
    home_squad: list[str] = []
    away_squad: list[str] = []
    current_half: int = 0
    current_turn: int = 0
    rerolls_used_home: int = 0
    rerolls_used_away: int = 0
    events: list[MatchEventResponse]
    mvp_home: Optional[str] = None
    mvp_away: Optional[str] = None
    gate: int
    started_at: Optional[datetime] = None
    scheduled_at: Optional[datetime] = None
    played_at: Optional[datetime] = None


class RecordMatchResultRequest(BaseModel):
    """Request to record match result."""

    score_home: int = Field(..., ge=0)
    score_away: int = Field(..., ge=0)
    weather: Optional[str] = None
    events: list["MatchEventRequest"] = Field(default_factory=list)
    mvp_home_player_id: Optional[str] = None
    mvp_away_player_id: Optional[str] = None
    gate: int = Field(default=0, ge=0)


class MatchEventRequest(BaseModel):
    """Event to record in a match."""

    type: str = Field(..., description="touchdown, casualty, interception, completion")
    team: str = Field(..., pattern="^(home|away)$")
    player_id: Optional[str] = None
    player_name: Optional[str] = None
    victim_id: Optional[str] = None
    victim_name: Optional[str] = None
    injury: Optional[str] = None
    detail: Optional[str] = None
    half: int = Field(default=1, ge=0, le=2)
    turn: int = Field(default=1, ge=0, le=16)


class AddMatchEventRequest(BaseModel):
    """Request to add a single event to a live match."""

    type: str = Field(
        ...,
        description="touchdown, casualty, interception, completion, mvp, "
        "weather, kickoff, inducement, reroll, foul, pass_attempt, etc.",
    )
    team: str = Field(..., pattern="^(home|away)$")
    player_id: Optional[str] = None
    player_name: Optional[str] = None
    victim_id: Optional[str] = None
    victim_name: Optional[str] = None
    injury: Optional[str] = None
    detail: Optional[str] = None
    half: int = Field(default=0, ge=0, le=2)
    turn: int = Field(default=0, ge=0, le=16)


class UpdateMatchStateRequest(BaseModel):
    """Request to update live match state (score, half, turn, weather, etc.)."""

    score_home: Optional[int] = Field(None, ge=0)
    score_away: Optional[int] = Field(None, ge=0)
    current_half: Optional[int] = Field(None, ge=0, le=2)
    current_turn: Optional[int] = Field(None, ge=0, le=16)
    weather: Optional[str] = None
    kickoff_event: Optional[str] = None
    home_ready: Optional[bool] = None
    away_ready: Optional[bool] = None
    home_squad: Optional[list[str]] = None
    away_squad: Optional[list[str]] = None
    rerolls_used_home: Optional[int] = Field(None, ge=0)
    rerolls_used_away: Optional[int] = Field(None, ge=0)
    mvp_home: Optional[str] = None
    mvp_away: Optional[str] = None
    gate: Optional[int] = Field(None, ge=0)


# ============== League Schemas ==============


class LeagueRulesRequest(BaseModel):
    """League rules configuration."""

    starting_budget: int = Field(default=1_000_000, ge=0)
    resurrection: bool = Field(default=False)
    inducements: bool = Field(default=True)
    spiraling_expenses: bool = Field(default=True)
    max_team_value: Optional[int] = None


class CreateLeagueRequest(BaseModel):
    """Request to create a league."""

    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    format: str = Field(default="round_robin", pattern="^(round_robin|knockout|swiss)$")
    max_teams: int = Field(default=8, ge=2, le=20)
    rules: Optional[LeagueRulesRequest] = None


class UpdateLeagueRequest(BaseModel):
    """Request to update league settings."""

    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    max_teams: Optional[int] = Field(None, ge=2, le=20)


class JoinLeagueRequest(BaseModel):
    """Request to join a league with a team."""

    team_id: str
    invite_code: str = Field(..., description="League invite code")


class LeagueByCodePreview(BaseModel):
    """League preview returned when looking up by invite code."""

    id: str
    name: str
    owner_username: str
    status: str
    format: str
    team_count: int
    max_teams: int
    season: int
    invite_code: str


class LeagueSummary(BaseModel):
    """Summary for league list."""

    id: str
    name: str
    owner_username: str
    status: str
    format: str
    team_count: int
    max_teams: int
    season: int
    invite_code: Optional[str] = None
    created_at: datetime
    # User-specific fields
    is_owner: bool = False
    user_team_name: Optional[str] = None
    current_round: Optional[int] = None


class LeagueDetail(BaseModel):
    """Full league detail."""

    id: str
    name: str
    description: Optional[str]
    owner_id: str
    owner_username: str
    invite_code: Optional[str] = None

    status: str
    season: int
    format: str
    max_teams: int
    rules: LeagueRulesRequest

    teams: list[LeagueTeamResponse]
    standings: list[LeagueStandingResponse]
    matches: list[MatchSummary]

    created_at: datetime
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
