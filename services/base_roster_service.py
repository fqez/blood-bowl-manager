"""Service for base roster operations (read-only catalog)."""

import logging
from typing import Optional

from models.base.roster import BasePlayer, BaseRoster
from schemas.base_roster import (
    BasePerkResponse,
    BasePlayerResponse,
    BaseRosterDetail,
    BaseRosterSummary,
    BaseStatsResponse,
)

logger = logging.getLogger(__name__)


class BaseRosterService:
    """Service for querying base roster catalog."""

    @staticmethod
    async def get_all_rosters() -> list[BaseRosterSummary]:
        """Get summary of all available rosters."""
        rosters = await BaseRoster.find_all().to_list()

        return [
            BaseRosterSummary(
                id=r.id,
                name=r.name,
                tier=r.tier,
                apothecary_allowed=r.apothecary_allowed,
                reroll_cost=r.reroll_cost,
                icon=r.icon,
            )
            for r in rosters
        ]

    @staticmethod
    async def get_roster_by_id(roster_id: str) -> Optional[BaseRosterDetail]:
        """Get full roster detail with all player types."""
        roster = await BaseRoster.find_one(BaseRoster.id == roster_id)

        if not roster:
            return None

        players = [
            BasePlayerResponse(
                type=p.type,
                name=p.name,
                position=p.position,
                max=p.max,
                cost=p.cost,
                stats=BaseStatsResponse.from_stats(
                    ma=p.stats.MA,
                    st=p.stats.ST,
                    ag=p.stats.AG,
                    pa=p.stats.PA,
                    av=p.stats.AV,
                ),
                perks=[
                    BasePerkResponse(id=pk.id, name=pk.name, category=pk.category)
                    for pk in p.perks
                ],
                primary_access=p.primary_access,
                secondary_access=p.secondary_access,
                image=p.image,
            )
            for p in roster.players
        ]

        return BaseRosterDetail(
            id=roster.id,
            name=roster.name,
            tier=roster.tier,
            reroll_cost=roster.reroll_cost,
            apothecary_allowed=roster.apothecary_allowed,
            special_rules=roster.special_rules,
            players=players,
            icon=roster.icon,
            wallpaper=roster.wallpaper,
        )

    @staticmethod
    async def get_player_type(roster_id: str, player_type: str) -> Optional[BasePlayer]:
        """Get a specific player type from a roster."""
        roster = await BaseRoster.find_one(BaseRoster.id == roster_id)

        if not roster:
            return None

        for player in roster.players:
            if player.type == player_type:
                return player

        return None
