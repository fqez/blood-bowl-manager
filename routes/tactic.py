"""Routes for tactic endpoints (JWT-protected)."""

from fastapi import APIRouter, Depends, HTTPException, status

from auth.jwt_bearer import get_current_user
from schemas.tactic import (
    CreateTacticRequest,
    TacticResponse,
    TacticSummary,
    UpdateTacticRequest,
)
from services.tactic_service import TacticService

router = APIRouter(prefix="/tactics", tags=["Tactics"])


@router.post("/", response_model=TacticResponse, status_code=status.HTTP_201_CREATED)
async def create_tactic(
    request: CreateTacticRequest,
    user_id: str = Depends(get_current_user),
):
    return await TacticService.create_tactic(user_id, request)


@router.get("/", response_model=list[TacticSummary])
async def get_my_tactics(
    user_id: str = Depends(get_current_user),
):
    return await TacticService.get_user_tactics(user_id)


@router.get("/{tactic_id}", response_model=TacticResponse)
async def get_tactic(
    tactic_id: str,
    user_id: str = Depends(get_current_user),
):
    tactic = await TacticService.get_tactic(tactic_id, user_id)
    if not tactic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tactic not found",
        )
    return tactic


@router.patch("/{tactic_id}", response_model=TacticResponse)
async def update_tactic(
    tactic_id: str,
    request: UpdateTacticRequest,
    user_id: str = Depends(get_current_user),
):
    tactic = await TacticService.update_tactic(tactic_id, user_id, request)
    if not tactic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tactic not found",
        )
    return tactic


@router.delete("/{tactic_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tactic(
    tactic_id: str,
    user_id: str = Depends(get_current_user),
):
    deleted = await TacticService.delete_tactic(tactic_id, user_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tactic not found",
        )
