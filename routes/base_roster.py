"""Routes for base roster endpoints (read-only catalog)."""

from fastapi import APIRouter, HTTPException, status

from schemas.base_roster import (
    BaseRosterDetail,
    BaseRosterHatredKeywordsResponse,
    BaseRosterSummary,
)
from services.base_roster_service import BaseRosterService

router = APIRouter(prefix="/base-rosters", tags=["Base Rosters"])


@router.get("/", response_model=list[BaseRosterSummary])
async def get_all_rosters():
    """
    Get all available team rosters.

    Returns a summary list of all races/rosters available in the game.
    """
    return await BaseRosterService.get_all_rosters()


@router.get("/hatred-keywords", response_model=BaseRosterHatredKeywordsResponse)
async def get_all_hatred_keywords():
    """Get all valid Hatred(X) keywords across all base rosters."""
    return await BaseRosterService.get_all_hatred_keywords()


@router.get(
    "/{roster_id}/hatred-keywords",
    response_model=BaseRosterHatredKeywordsResponse,
)
async def get_roster_hatred_keywords(roster_id: str):
    """Get valid Hatred(X) keywords for a roster."""
    response = await BaseRosterService.get_hatred_keywords(roster_id)

    if not response:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Roster '{roster_id}' not found",
        )

    return response


@router.get("/{roster_id}", response_model=BaseRosterDetail)
async def get_roster_detail(roster_id: str):
    """
    Get full roster detail with all player types.

    Use this to display the roster catalog when a user is creating
    a team or wants to hire players.
    """
    roster = await BaseRosterService.get_roster_by_id(roster_id)

    if not roster:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Roster '{roster_id}' not found",
        )

    return roster
