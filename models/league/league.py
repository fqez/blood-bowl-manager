"""League models with embedded matches and standings."""

import uuid
from datetime import datetime
from enum import Enum
from typing import Optional

from beanie import Document
from pydantic import BaseModel, Field


class LeagueStatus(str, Enum):
    """League lifecycle status."""

    DRAFT = "draft"  # Accepting teams
    ACTIVE = "active"  # Season in progress
    COMPLETED = "completed"  # Season finished
    CANCELLED = "cancelled"


class MatchStatus(str, Enum):
    """Match status."""

    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class LeagueTeam(BaseModel):
    """
    Reference to a team participating in a league.

    Contains denormalized data for quick display without
    needing to look up the full UserTeam document.
    """

    team_id: str = Field(..., description="Reference to UserTeam._id")
    team_name: str
    user_id: str
    username: str
    base_roster_id: str
    icon: Optional[str] = None
    joined_at: datetime = Field(default_factory=datetime.utcnow)


class LeagueStanding(BaseModel):
    """Team standing within a league."""

    team_id: str
    team_name: str

    # Record
    wins: int = Field(default=0, ge=0)
    draws: int = Field(default=0, ge=0)
    losses: int = Field(default=0, ge=0)

    # Stats
    touchdowns_for: int = Field(default=0, ge=0)
    touchdowns_against: int = Field(default=0, ge=0)
    casualties_for: int = Field(default=0, ge=0)
    casualties_against: int = Field(default=0, ge=0)

    @property
    def points(self) -> int:
        """Calculate league points (3 for win, 1 for draw)."""
        return (self.wins * 3) + self.draws

    @property
    def touchdown_diff(self) -> int:
        return self.touchdowns_for - self.touchdowns_against

    @property
    def games_played(self) -> int:
        return self.wins + self.draws + self.losses


class MatchTeamInfo(BaseModel):
    """Team info snapshot for a match."""

    team_id: str
    team_name: str
    user_id: str
    username: str


class MatchEvent(BaseModel):
    """An event that occurred during a match."""

    id: str = Field(default_factory=lambda: uuid.uuid4().hex[:8])
    type: str = Field(
        ..., description="touchdown, casualty, interception, completion, mvp, etc."
    )
    team: str = Field(..., pattern="^(home|away)$")
    player_id: Optional[str] = None
    player_name: Optional[str] = None

    # For casualties
    victim_id: Optional[str] = None
    victim_name: Optional[str] = None
    injury: Optional[str] = None

    # Timing
    half: int = Field(default=1, ge=1, le=2)
    turn: int = Field(default=1, ge=1, le=8)

    timestamp: datetime = Field(default_factory=datetime.utcnow)


class Match(BaseModel):
    """
    A match within a league.

    Embedded in League document since:
    - A league has bounded matches (8 teams = ~28 matches round-robin)
    - You always view matches in league context
    - Match results update standings atomically
    """

    id: str = Field(default_factory=lambda: uuid.uuid4().hex)
    round: int = Field(..., ge=1)

    # Teams
    home: MatchTeamInfo
    away: MatchTeamInfo

    # Result
    status: MatchStatus = Field(default=MatchStatus.SCHEDULED)
    score_home: int = Field(default=0, ge=0)
    score_away: int = Field(default=0, ge=0)

    # Weather (affects gameplay)
    weather: Optional[str] = None

    # Match events (goals, casualties, etc.)
    events: list[MatchEvent] = Field(default_factory=list)

    # MVPs
    mvp_home: Optional[str] = None  # Player ID
    mvp_away: Optional[str] = None

    # Gate (money from fans)
    gate: int = Field(default=0, ge=0)

    # Timing
    scheduled_at: Optional[datetime] = None
    played_at: Optional[datetime] = None

    class Config:
        use_enum_values = True


class LeagueRules(BaseModel):
    """League configuration and rules."""

    starting_budget: int = Field(default=1_000_000, ge=0)
    resurrection: bool = Field(
        default=False, description="If true, dead players return after match"
    )
    inducements: bool = Field(
        default=True, description="Allow inducements for underdogs"
    )
    spiraling_expenses: bool = Field(
        default=True, description="Apply spiraling expenses rule"
    )
    max_team_value: Optional[int] = Field(None, description="Cap on team value if set")


class League(Document):
    """
    A Blood Bowl league with embedded matches and standings.

    Design decisions:
    - Teams are referenced (not embedded) because a team can be in multiple leagues
    - Matches are embedded because they only exist in league context
    - Standings are embedded for atomic updates with match results
    """

    # Identity
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    owner_id: str = Field(..., description="User who created the league")

    # Configuration
    status: LeagueStatus = Field(default=LeagueStatus.DRAFT)
    season: int = Field(default=1, ge=1)
    format: str = Field(
        default="round_robin", description="round_robin, knockout, swiss"
    )
    max_teams: int = Field(default=8, ge=2, le=20)
    rules: LeagueRules = Field(default_factory=LeagueRules)

    # Participants (references to UserTeam, bounded by max_teams)
    teams: list[LeagueTeam] = Field(default_factory=list)

    # Standings (one per team, updated after each match)
    standings: list[LeagueStanding] = Field(default_factory=list)

    # Matches (embedded, bounded by format)
    matches: list[Match] = Field(default_factory=list)

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None

    class Settings:
        name = "leagues"

    def get_team_standing(self, team_id: str) -> Optional[LeagueStanding]:
        """Get standing for a specific team."""
        for standing in self.standings:
            if standing.team_id == team_id:
                return standing
        return None

    def get_sorted_standings(self) -> list[LeagueStanding]:
        """Get standings sorted by points, then TD diff."""
        return sorted(
            self.standings,
            key=lambda s: (s.points, s.touchdown_diff, s.touchdowns_for),
            reverse=True,
        )

    def can_join(self, team_id: str) -> tuple[bool, str]:
        """Check if a team can join this league."""
        if self.status != LeagueStatus.DRAFT:
            return False, "League is not accepting teams"

        if len(self.teams) >= self.max_teams:
            return False, f"League is full ({self.max_teams} teams)"

        if any(t.team_id == team_id for t in self.teams):
            return False, "Team is already in this league"

        return True, "OK"

    class Config:
        use_enum_values = True
        json_schema_extra = {
            "example": {
                "name": "Summer League 2026",
                "owner_id": "user_abc123",
                "status": "active",
                "max_teams": 8,
                "teams": [
                    {
                        "team_id": "team_xyz789",
                        "team_name": "Los Putrefactos FC",
                        "user_id": "user_abc123",
                        "username": "skull_crusher",
                    }
                ],
                "standings": [
                    {
                        "team_id": "team_xyz789",
                        "team_name": "Los Putrefactos FC",
                        "wins": 3,
                        "draws": 1,
                        "losses": 1,
                        "touchdowns_for": 8,
                        "touchdowns_against": 5,
                    }
                ],
            }
        }
