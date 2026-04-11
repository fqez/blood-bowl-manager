"""Service for star player operations (read-only catalog)."""

import logging
from typing import Optional

from models.base.star_player import StarPlayer
from schemas.star_player import (
    SpecialAbilityResponse,
    StarPlayerDetail,
    StarPlayerStatsResponse,
    StarPlayerSummary,
)

logger = logging.getLogger(__name__)


class StarPlayerService:
    """Service for querying star player catalog."""

    @staticmethod
    async def get_all_star_players() -> list[StarPlayerSummary]:
        """Get summary of all available star players."""
        star_players = await StarPlayer.find_all().to_list()

        return [
            StarPlayerSummary(
                id=sp.id,
                name=sp.name,
                cost=sp.cost,
                player_types=sp.player_types,
                plays_for_count=len(sp.plays_for),
            )
            for sp in star_players
        ]

    @staticmethod
    async def get_star_player_by_id(star_player_id: str) -> Optional[StarPlayerDetail]:
        """Get full star player detail."""
        sp = await StarPlayer.find_one(StarPlayer.id == star_player_id)

        if not sp:
            return None

        stats = StarPlayerStatsResponse.from_stats(
            ma=sp.stats.MA,
            st=sp.stats.ST,
            ag=sp.stats.AG,
            pa=sp.stats.PA,
            av=sp.stats.AV,
        )

        special_ability = None
        if sp.special_ability:
            special_ability = SpecialAbilityResponse(
                name=sp.special_ability.name,
                description=sp.special_ability.description,
            )

        return StarPlayerDetail(
            id=sp.id,
            name=sp.name,
            cost=sp.cost,
            stats=stats,
            player_types=sp.player_types,
            skills=sp.skills,
            special_ability=special_ability,
            plays_for=sp.plays_for,
            image=sp.image,
        )

    @staticmethod
    async def get_star_players_for_team(team_id: str) -> list[StarPlayerSummary]:
        """Get all star players available for a specific team."""
        star_players = await StarPlayer.find({"plays_for": team_id}).to_list()

        return [
            StarPlayerSummary(
                id=sp.id,
                name=sp.name,
                cost=sp.cost,
                player_types=sp.player_types,
                plays_for_count=len(sp.plays_for),
            )
            for sp in star_players
        ]
