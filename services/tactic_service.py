"""Service layer for tactic CRUD operations."""

from datetime import datetime
from typing import Optional

from models.tactic.tactic import PlacedPlayer, Tactic
from schemas.tactic import (
    CreateTacticRequest,
    PlacedPlayerSchema,
    TacticResponse,
    TacticSummary,
    UpdateTacticRequest,
)


class TacticService:

    @staticmethod
    async def create_tactic(
        user_id: str, request: CreateTacticRequest
    ) -> TacticResponse:
        tactic = Tactic(
            user_id=user_id,
            name=request.name,
            base_roster_id=request.base_roster_id,
            mode=request.mode,
            placements=[
                PlacedPlayer(row=p.row, col=p.col, position_id=p.position_id)
                for p in request.placements
            ],
            good_against=request.good_against,
            notes=request.notes,
        )
        await tactic.insert()
        return TacticService._to_response(tactic)

    @staticmethod
    async def get_user_tactics(user_id: str) -> list[TacticSummary]:
        tactics = (
            await Tactic.find(Tactic.user_id == user_id)
            .sort(-Tactic.updated_at)
            .to_list()
        )
        return [TacticService._to_summary(t) for t in tactics]

    @staticmethod
    async def get_tactic(tactic_id: str, user_id: str) -> Optional[TacticResponse]:
        tactic = await Tactic.get(tactic_id)
        if not tactic or tactic.user_id != user_id:
            return None
        return TacticService._to_response(tactic)

    @staticmethod
    async def update_tactic(
        tactic_id: str, user_id: str, request: UpdateTacticRequest
    ) -> Optional[TacticResponse]:
        tactic = await Tactic.get(tactic_id)
        if not tactic or tactic.user_id != user_id:
            return None

        if request.name is not None:
            tactic.name = request.name
        if request.mode is not None:
            tactic.mode = request.mode
        if request.placements is not None:
            tactic.placements = [
                PlacedPlayer(row=p.row, col=p.col, position_id=p.position_id)
                for p in request.placements
            ]
        if request.good_against is not None:
            tactic.good_against = request.good_against
        if request.notes is not None:
            tactic.notes = request.notes

        tactic.updated_at = datetime.utcnow()
        await tactic.save()
        return TacticService._to_response(tactic)

    @staticmethod
    async def delete_tactic(tactic_id: str, user_id: str) -> bool:
        tactic = await Tactic.get(tactic_id)
        if not tactic or tactic.user_id != user_id:
            return False
        await tactic.delete()
        return True

    @staticmethod
    def _to_response(tactic: Tactic) -> TacticResponse:
        return TacticResponse(
            id=str(tactic.id),
            user_id=tactic.user_id,
            name=tactic.name,
            base_roster_id=tactic.base_roster_id,
            mode=tactic.mode,
            placements=[
                PlacedPlayerSchema(row=p.row, col=p.col, position_id=p.position_id)
                for p in tactic.placements
            ],
            good_against=list(tactic.good_against),
            notes=tactic.notes or "",
            created_at=tactic.created_at,
            updated_at=tactic.updated_at,
        )

    @staticmethod
    def _to_summary(tactic: Tactic) -> TacticSummary:
        return TacticSummary(
            id=str(tactic.id),
            name=tactic.name,
            base_roster_id=tactic.base_roster_id,
            mode=tactic.mode,
            player_count=len(tactic.placements),
            good_against_count=len(tactic.good_against),
            created_at=tactic.created_at,
            updated_at=tactic.updated_at,
        )
