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
    username: str


class MatchEventResponse(BaseModel):
    """Event during a match."""

    id: str
    type: str
    team: str
    player_name: Optional[str] = None
    victim_name: Optional[str] = None
    injury: Optional[str] = None
    half: int
    turn: int


class MatchSummary(BaseModel):
    """Match summary for list."""

    id: str
    round: int
    home: MatchTeamResponse
    away: MatchTeamResponse
    status: str
    score_home: int
    score_away: int
    scheduled_at: Optional[datetime] = None
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
    events: list[MatchEventResponse]
    mvp_home: Optional[str] = None
    mvp_away: Optional[str] = None
    gate: int
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
    half: int = Field(default=1, ge=1, le=2)
    turn: int = Field(default=1, ge=1, le=8)


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
    created_at: datetime


class LeagueDetail(BaseModel):
    """Full league detail."""

    id: str
    name: str
    description: Optional[str]
    owner_id: str
    owner_username: str

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
