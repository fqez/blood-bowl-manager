"""Routes for base roster endpoints (read-only catalog)."""

from fastapi import APIRouter, HTTPException, status

from schemas.base_roster import BaseRosterDetail, BaseRosterSummary
from services.base_roster_service import BaseRosterService

router = APIRouter(prefix="/base-rosters", tags=["Base Rosters"])


@router.get("/", response_model=list[BaseRosterSummary])
async def get_all_rosters():
    """
    Get all available team rosters.

    Returns a summary list of all races/rosters available in the game.
    """
    return await BaseRosterService.get_all_rosters()


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
