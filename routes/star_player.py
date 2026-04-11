"""Routes for star player endpoints (read-only catalog)."""

from fastapi import APIRouter, HTTPException, status

from schemas.star_player import StarPlayerDetail, StarPlayerSummary
from services.star_player_service import StarPlayerService

router = APIRouter(prefix="/star-players", tags=["Star Players"])


@router.get("/", response_model=list[StarPlayerSummary])
async def get_all_star_players():
    """
    Get all available star players.

    Returns a summary list of all star players in the game.
    """
    return await StarPlayerService.get_all_star_players()


@router.get("/team/{team_id}", response_model=list[StarPlayerSummary])
async def get_star_players_for_team(team_id: str):
    """
    Get star players available for a specific team.

    Use this to show which star players a team can hire.
    """
    star_players = await StarPlayerService.get_star_players_for_team(team_id)
    return star_players


@router.get("/{star_player_id}", response_model=StarPlayerDetail)
async def get_star_player_detail(star_player_id: str):
    """
    Get full star player detail.

    Use this to display detailed information about a star player
    including their stats, skills, and special ability.
    """
    star_player = await StarPlayerService.get_star_player_by_id(star_player_id)

    if not star_player:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Star player '{star_player_id}' not found",
        )

    return star_player
