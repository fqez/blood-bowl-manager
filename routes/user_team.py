"""Routes for user team endpoints."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from auth.jwt_bearer import get_current_user
from exceptions.exceptions import (
    InvalidOperationException,
    PlayerNotFoundException,
    TeamNotFoundException,
)
from schemas.user_team import (
    AddPerkRequest,
    ApplyPlayerAdvancementRequest,
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
        return await UserTeamService.get_team_detail(str(team.id), viewer_id=user_id)
    except InvalidOperationException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/", response_model=list[UserTeamSummary])
async def get_my_teams(user_id: str = Depends(get_current_user)):
    """Get all teams owned by the current user."""
    return await UserTeamService.get_teams_by_user(user_id)


@router.get("/by-code/{share_code}", response_model=UserTeamDetail)
async def get_team_by_share_code(share_code: str):
    """Get public team detail by share code without private notes."""
    detail = await UserTeamService.get_team_detail_by_share_code(share_code)

    if not detail:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Team with code '{share_code}' not found",
        )

    return detail


@router.get("/{team_id}", response_model=UserTeamDetail)
async def get_team(
    team_id: str,
    league_id: Optional[str] = Query(
        None,
        description="League context for commissioner read access",
    ),
    user_id: str = Depends(get_current_user),
):
    """Get full team detail with all players."""
    try:
        detail = await UserTeamService.get_team_detail(
            team_id,
            viewer_id=user_id,
            league_id=league_id,
        )
    except InvalidOperationException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))

    if not detail:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Team '{team_id}' not found",
        )

    return detail


@router.patch("/{team_id}", response_model=UserTeamDetail)
async def update_team(
    team_id: str,
    request: UpdateTeamRequest,
    user_id: str = Depends(get_current_user),
):
    """Update team settings."""
    try:
        await UserTeamService.update_team(team_id, user_id, request)
        return await UserTeamService.get_team_detail(
            team_id,
            viewer_id=user_id,
            league_id=request.league_id,
        )
    except TeamNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Team '{team_id}' not found",
        )
    except InvalidOperationException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


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
async def hire_player(
    team_id: str,
    request: HirePlayerRequest,
    user_id: str = Depends(get_current_user),
):
    """
    Hire a new player for a team.

    The player type must be available in the team's base roster,
    and the team must have enough treasury and roster space.
    """
    try:
        return await UserTeamService.hire_player(team_id, user_id, request)
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
async def hire_star_player(
    team_id: str,
    request: HireStarPlayerRequest,
    user_id: str = Depends(get_current_user),
):
    """
    Hire a star player for a team.

    The star player must be available for this team's roster,
    and the team must have enough treasury and roster space.
    """
    try:
        return await UserTeamService.hire_star_player(team_id, user_id, request)
    except TeamNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Team '{team_id}' not found",
        )
    except InvalidOperationException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{team_id}/players/{player_id}", status_code=status.HTTP_204_NO_CONTENT)
async def fire_player(
    team_id: str,
    player_id: str,
    league_id: Optional[str] = Query(default=None),
    user_id: str = Depends(get_current_user),
):
    """
    Fire a player from a team.

    The player is removed and their cost is NOT refunded.
    """
    try:
        await UserTeamService.fire_player(
            team_id,
            user_id,
            player_id,
            league_id=league_id,
        )
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
async def update_player(
    team_id: str,
    player_id: str,
    request: UpdatePlayerRequest,
    user_id: str = Depends(get_current_user),
):
    """Update a player's name, jersey number, image, status and/or injury history."""
    try:
        await UserTeamService.update_player(team_id, user_id, player_id, request)
        return await UserTeamService.get_team_detail(
            team_id,
            viewer_id=user_id,
            league_id=request.league_id,
            match_id=request.match_id,
            quick_match_id=request.quick_match_id,
        )
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
async def add_perk_to_player(
    team_id: str,
    player_id: str,
    request: AddPerkRequest,
    user_id: str = Depends(get_current_user),
):
    """Add a skill/perk to a player."""
    try:
        await UserTeamService.add_perk_to_player(
            team_id,
            user_id,
            player_id,
            request.perk_id,
            request.perk_name,
            request.parameter,
            request.category,
            request.league_id,
        )
        return await UserTeamService.get_team_detail(
            team_id,
            viewer_id=user_id,
            league_id=request.league_id,
        )
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


@router.post(
    "/{team_id}/players/{player_id}/advancements", response_model=UserTeamDetail
)
async def apply_player_advancement(
    team_id: str,
    player_id: str,
    request: ApplyPlayerAdvancementRequest,
    user_id: str = Depends(get_current_user),
):
    """Spend SPP on an official player advancement."""
    try:
        await UserTeamService.apply_player_advancement(
            team_id, user_id, player_id, request
        )
        return await UserTeamService.get_team_detail(
            team_id,
            viewer_id=user_id,
            league_id=request.league_id,
        )
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
