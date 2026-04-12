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
    FlatMatchResponse,
    JoinLeagueRequest,
    LeagueByCodePreview,
    LeagueDetail,
    LeagueSummary,
    MatchDetail,
    RecordMatchResultRequest,
    UpdateLeagueRequest,
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


@router.get("/by-code/{invite_code}", response_model=LeagueByCodePreview)
async def get_league_by_invite_code(
    invite_code: str,
    user_id: str = Depends(get_current_user),
):
    """Look up a league by its invite code."""
    preview = await LeagueService.get_league_by_code(invite_code)
    if not preview:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No se encontró ninguna liga con el código '{invite_code}'",
        )
    return preview


@router.patch("/{league_id}", response_model=LeagueDetail)
async def update_league_settings(
    league_id: str,
    request: UpdateLeagueRequest,
    user_id: str = Depends(get_current_user),
):
    """Update league settings (owner only)."""
    try:
        await LeagueService.update_league(league_id, user_id, request)
        return await LeagueService.get_league_detail(league_id)
    except LeagueNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"League '{league_id}' not found",
        )
    except InvalidOperationException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{league_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_league(
    league_id: str,
    user_id: str = Depends(get_current_user),
):
    """Delete a league (owner only)."""
    try:
        await LeagueService.delete_league(league_id, user_id)
    except LeagueNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"League '{league_id}' not found",
        )
    except InvalidOperationException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/{league_id}/archive", status_code=status.HTTP_204_NO_CONTENT)
async def archive_league(
    league_id: str,
    user_id: str = Depends(get_current_user),
):
    """Archive/complete a league (owner only)."""
    try:
        await LeagueService.archive_league(league_id, user_id)
    except LeagueNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"League '{league_id}' not found",
        )
    except InvalidOperationException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# ============== Team Management ==============


@router.post("/{league_id}/teams", response_model=LeagueDetail)
async def join_league(
    league_id: str,
    request: JoinLeagueRequest,
    user_id: str = Depends(get_current_user),
):
    """Join a league with a team using the invite code."""
    try:
        await LeagueService.join_league(
            league_id, user_id, request.team_id, request.invite_code
        )
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


@router.get("/{league_id}/matches", response_model=list[FlatMatchResponse])
async def get_league_matches(league_id: str):
    """Get all matches for a league as a flat list."""
    detail = await LeagueService.get_league_detail(league_id)
    if not detail:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"League '{league_id}' not found",
        )
    return [
        FlatMatchResponse(
            id=m.id,
            league_id=league_id,
            round=m.round,
            home_team_id=m.home.team_id,
            home_team_name=m.home.team_name,
            away_team_id=m.away.team_id,
            away_team_name=m.away.team_name,
            home_score=m.score_home,
            away_score=m.score_away,
            status=m.status,
            played_at=m.played_at,
        )
        for m in detail.matches
    ]


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
