"""Routes for quick (friendly) match endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status

from auth.jwt_bearer import get_current_user
from exceptions.exceptions import InvalidOperationException
from schemas.league import AddMatchEventRequest, MatchDetail, UpdateMatchStateRequest
from schemas.quick_match import CreateQuickMatchRequest, QuickMatchSummary
from services.quick_match_service import QuickMatchService

router = APIRouter(prefix="/quick-matches", tags=["Quick Matches"])


@router.post("/", response_model=MatchDetail, status_code=status.HTTP_201_CREATED)
async def create_quick_match(
    request: CreateQuickMatchRequest,
    user_id: str = Depends(get_current_user),
):
    """Create a quick (friendly) match between two teams."""
    try:
        return await QuickMatchService.create_quick_match(
            user_id, request.home_team_id, request.away_team_id
        )
    except InvalidOperationException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/", response_model=list[QuickMatchSummary])
async def list_quick_matches(user_id: str = Depends(get_current_user)):
    """List quick matches created by the current user."""
    return await QuickMatchService.list_quick_matches(user_id)


@router.get("/{match_id}", response_model=MatchDetail)
async def get_quick_match(match_id: str):
    """Get quick match detail."""
    try:
        return await QuickMatchService.get_detail(match_id)
    except InvalidOperationException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Quick match '{match_id}' not found",
        )


@router.post("/{match_id}/start", response_model=MatchDetail)
async def start_quick_match(
    match_id: str,
    user_id: str = Depends(get_current_user),
):
    """Start a quick match."""
    try:
        return await QuickMatchService.start_match(match_id, user_id)
    except InvalidOperationException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/{match_id}/events", response_model=MatchDetail)
async def add_quick_match_event(
    match_id: str,
    request: AddMatchEventRequest,
    user_id: str = Depends(get_current_user),
):
    """Add an event to a live quick match."""
    try:
        return await QuickMatchService.add_event(match_id, user_id, request)
    except InvalidOperationException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{match_id}/events/{event_id}", response_model=MatchDetail)
async def delete_quick_match_event(
    match_id: str,
    event_id: str,
    user_id: str = Depends(get_current_user),
):
    """Remove an event from a live quick match."""
    try:
        return await QuickMatchService.delete_event(match_id, event_id, user_id)
    except InvalidOperationException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.patch("/{match_id}/state", response_model=MatchDetail)
async def update_quick_match_state(
    match_id: str,
    request: UpdateMatchStateRequest,
    user_id: str = Depends(get_current_user),
):
    """Update live quick match state."""
    try:
        return await QuickMatchService.update_state(match_id, user_id, request)
    except InvalidOperationException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/{match_id}/complete", response_model=MatchDetail)
async def complete_quick_match(
    match_id: str,
    user_id: str = Depends(get_current_user),
):
    """Complete a quick match."""
    try:
        return await QuickMatchService.complete_match(match_id, user_id)
    except InvalidOperationException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{match_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_quick_match(
    match_id: str,
    user_id: str = Depends(get_current_user),
):
    """Delete a quick match (creator only)."""
    try:
        await QuickMatchService.delete_quick_match(match_id, user_id)
    except InvalidOperationException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
