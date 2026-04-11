"""Routes for league endpoints."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from auth.jwt_bearer import get_current_user
from exceptions.exceptions import (
    InvalidOperationException,
    LeagueNotFoundException,
    TeamNotFoundException,
)
from schemas.league import (
    CreateLeagueRequest,
    JoinLeagueRequest,
    LeagueDetail,
    LeagueSummary,
    MatchDetail,
    RecordMatchResultRequest,
)
from services.league_service import LeagueService

router = APIRouter(prefix="/leagues", tags=["Leagues"])


# ============== League CRUD ==============


@router.post("/", response_model=LeagueDetail, status_code=status.HTTP_201_CREATED)
async def create_league(
    request: CreateLeagueRequest,
    user_id: str = Depends(get_current_user),
):
    """Create a new league."""
    league = await LeagueService.create_league(user_id, request)
    return await LeagueService.get_league_detail(str(league.id))


@router.get("/", response_model=list[LeagueSummary])
async def get_all_leagues(
    status: Optional[str] = Query(
        None, description="Filter by status: draft, active, completed"
    ),
):
    """Get all leagues, optionally filtered by status."""
    return await LeagueService.get_all_leagues(status)


@router.get("/my", response_model=list[LeagueSummary])
async def get_my_leagues(user_id: str = Depends(get_current_user)):
    """Get leagues where the current user has a team."""
    return await LeagueService.get_leagues_by_user(user_id)


@router.get("/{league_id}", response_model=LeagueDetail)
async def get_league(league_id: str):
    """Get full league detail with teams, standings, and matches."""
    detail = await LeagueService.get_league_detail(league_id)

    if not detail:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"League '{league_id}' not found",
        )

    return detail


# ============== Team Management ==============


@router.post("/{league_id}/teams", response_model=LeagueDetail)
async def join_league(
    league_id: str,
    request: JoinLeagueRequest,
    user_id: str = Depends(get_current_user),
):
    """Join a league with a team."""
    try:
        await LeagueService.join_league(league_id, user_id, request.team_id)
        return await LeagueService.get_league_detail(league_id)
    except LeagueNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"League '{league_id}' not found",
        )
    except TeamNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Team '{request.team_id}' not found",
        )
    except InvalidOperationException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{league_id}/teams/{team_id}", status_code=status.HTTP_204_NO_CONTENT)
async def leave_league(
    league_id: str,
    team_id: str,
    user_id: str = Depends(get_current_user),
):
    """Leave a league (only before it starts)."""
    try:
        await LeagueService.leave_league(league_id, team_id, user_id)
    except LeagueNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"League '{league_id}' not found",
        )
    except InvalidOperationException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# ============== League Lifecycle ==============


@router.post("/{league_id}/start", response_model=LeagueDetail)
async def start_league(league_id: str, user_id: str = Depends(get_current_user)):
    """Start the league and generate fixtures (owner only)."""
    try:
        await LeagueService.start_league(league_id, user_id)
        return await LeagueService.get_league_detail(league_id)
    except LeagueNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"League '{league_id}' not found",
        )
    except InvalidOperationException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# ============== Match Operations ==============


@router.get("/{league_id}/matches/{match_id}", response_model=MatchDetail)
async def get_match(league_id: str, match_id: str):
    """Get full match detail."""
    match = await LeagueService.get_match_detail(league_id, match_id)

    if not match:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Match '{match_id}' not found",
        )

    return match


@router.post("/{league_id}/matches/{match_id}/result", response_model=LeagueDetail)
async def record_match_result(
    league_id: str,
    match_id: str,
    request: RecordMatchResultRequest,
):
    """Record the result of a match."""
    try:
        await LeagueService.record_match_result(league_id, match_id, request)
        return await LeagueService.get_league_detail(league_id)
    except LeagueNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"League '{league_id}' not found",
        )
    except InvalidOperationException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
