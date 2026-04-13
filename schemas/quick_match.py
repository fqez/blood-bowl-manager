"""Schemas for quick match endpoints."""

from typing import Optional

from pydantic import BaseModel, Field

from schemas.league import (
    MatchTeamResponse,
)


class CreateQuickMatchRequest(BaseModel):
    """Request to create a quick match between two user teams."""

    home_team_id: str = Field(..., description="UserTeam id for home")
    away_team_id: str = Field(..., description="UserTeam id for away")


class QuickMatchSummary(BaseModel):
    """Quick match list item."""

    id: str
    home: MatchTeamResponse
    away: MatchTeamResponse
    status: str
    score_home: int
    score_away: int
    weather: Optional[str] = None
    created_at: Optional[str] = None
    played_at: Optional[str] = None
