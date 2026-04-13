"""Routes for user team endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status

from auth.jwt_bearer import get_current_user
from exceptions.exceptions import (
    InvalidOperationException,
    PlayerNotFoundException,
    TeamNotFoundException,
)
from schemas.user_team import (
    AddPerkRequest,
    CreateTeamRequest,
    HirePlayerRequest,
    HirePlayerResponse,
    HireStarPlayerRequest,
    UpdatePlayerRequest,
    UpdateTeamRequest,
    UserTeamDetail,
    UserTeamSummary,
)
from services.user_team_service import UserTeamService

router = APIRouter(prefix="/user-teams", tags=["User Teams"])


# ============== Team Endpoints ==============


@router.post("/", response_model=UserTeamDetail, status_code=status.HTTP_201_CREATED)
async def create_team(
    request: CreateTeamRequest,
    user_id: str = Depends(get_current_user),
):
    """Create a new team for the current user."""
    try:
        team = await UserTeamService.create_team(user_id, request)
        return await UserTeamService.get_team_detail(str(team.id))
    except InvalidOperationException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/", response_model=list[UserTeamSummary])
async def get_my_teams(user_id: str = Depends(get_current_user)):
    """Get all teams owned by the current user."""
    return await UserTeamService.get_teams_by_user(user_id)


@router.get("/{team_id}", response_model=UserTeamDetail)
async def get_team(team_id: str):
    """Get full team detail with all players."""
    detail = await UserTeamService.get_team_detail(team_id)

    if not detail:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Team '{team_id}' not found",
        )

    return detail


@router.patch("/{team_id}", response_model=UserTeamDetail)
async def update_team(team_id: str, request: UpdateTeamRequest):
    """Update team settings."""
    try:
        await UserTeamService.update_team(team_id, request)
        return await UserTeamService.get_team_detail(team_id)
    except TeamNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Team '{team_id}' not found",
        )


@router.delete("/{team_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_team(team_id: str, user_id: str = Depends(get_current_user)):
    """Delete a team."""
    try:
        deleted = await UserTeamService.delete_team(team_id, user_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Team '{team_id}' not found",
            )
    except InvalidOperationException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


# ============== Player Endpoints ==============


@router.post(
    "/{team_id}/players",
    response_model=HirePlayerResponse,
    status_code=status.HTTP_201_CREATED,
)
async def hire_player(team_id: str, request: HirePlayerRequest):
    """
    Hire a new player for a team.

    The player type must be available in the team's base roster,
    and the team must have enough treasury and roster space.
    """
    try:
        return await UserTeamService.hire_player(team_id, request)
    except TeamNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Team '{team_id}' not found",
        )
    except InvalidOperationException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post(
    "/{team_id}/players/star",
    response_model=HirePlayerResponse,
    status_code=status.HTTP_201_CREATED,
)
async def hire_star_player(team_id: str, request: HireStarPlayerRequest):
    """
    Hire a star player for a team.

    The star player must be available for this team's roster,
    and the team must have enough treasury and roster space.
    """
    try:
        return await UserTeamService.hire_star_player(team_id, request)
    except TeamNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Team '{team_id}' not found",
        )
    except InvalidOperationException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{team_id}/players/{player_id}", status_code=status.HTTP_204_NO_CONTENT)
async def fire_player(team_id: str, player_id: str):
    """
    Fire a player from a team.

    The player is removed and their cost is NOT refunded.
    """
    try:
        await UserTeamService.fire_player(team_id, player_id)
    except TeamNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Team '{team_id}' not found",
        )
    except PlayerNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Player '{player_id}' not found",
        )


@router.patch("/{team_id}/players/{player_id}", response_model=UserTeamDetail)
async def update_player(team_id: str, player_id: str, request: UpdatePlayerRequest):
    """Update a player's name and/or jersey number."""
    try:
        await UserTeamService.update_player(team_id, player_id, request)
        return await UserTeamService.get_team_detail(team_id)
    except TeamNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Team '{team_id}' not found",
        )
    except PlayerNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Player '{player_id}' not found",
        )
    except InvalidOperationException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/{team_id}/players/{player_id}/perks", response_model=UserTeamDetail)
async def add_perk_to_player(team_id: str, player_id: str, request: AddPerkRequest):
    """Add a skill/perk to a player."""
    try:
        await UserTeamService.add_perk_to_player(
            team_id, player_id, request.perk_id, request.perk_name, request.category
        )
        return await UserTeamService.get_team_detail(team_id)
    except TeamNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Team '{team_id}' not found",
        )
    except PlayerNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Player '{player_id}' not found",
        )
    except InvalidOperationException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
