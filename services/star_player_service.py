"""Service for star player operations (read-only catalog)."""

import logging
import re
from typing import Optional

from models.base.star_player import StarPlayer
from models.team.perk import Perk
from schemas.star_player import (
    SpecialAbilityResponse,
    StarPlayerDetail,
    StarPlayerStatsResponse,
    StarPlayerSummary,
)
from utils.team_special_rules import star_player_available_for_roster

logger = logging.getLogger(__name__)


class StarPlayerService:
    """Service for querying star player catalog."""

    @staticmethod
    def _strip_skill_parameter(value: str) -> str:
        return re.sub(r"\s*\([^)]*\)", "", value or "").strip()

    @staticmethod
    def _extract_skill_parameter(value: str) -> str | None:
        match = re.search(r"\(([^)]+)\)", value or "")
        if not match:
            return None
        return match.group(1).strip() or None

    @staticmethod
    def _canonical_skill_id(value: str) -> str:
        stripped = StarPlayerService._strip_skill_parameter(value)
        raw = stripped.strip().lower().removeprefix("perk-")
        if re.fullmatch(r"[a-z0-9_]+", raw):
            normalized = raw
        else:
            normalized = re.sub(
                r"_+", "_", re.sub(r"[^a-z0-9]+", "_", raw).strip("_")
            )

        aliases = {
            "plague_ridden": "infected",
        }
        return aliases.get(normalized, normalized)

    @staticmethod
    def _localized_name(name: dict | None, fallback: str) -> str:
        if not name:
            return fallback
        return name.get("es") or name.get("en") or fallback

    @staticmethod
    async def _skill_display_lookup(star_players: list[StarPlayer]) -> dict[str, str]:
        raw_skills = {skill for sp in star_players for skill in sp.skills}
        canonical_ids = {
            StarPlayerService._canonical_skill_id(skill)
            for skill in raw_skills
            if skill
        }
        perks = (
            await Perk.find({"_id": {"$in": list(canonical_ids)}}).to_list()
            if canonical_ids
            else []
        )
        perk_by_id = {str(perk.id): perk for perk in perks}
        display_lookup: dict[str, str] = {}

        for raw_skill in raw_skills:
            perk = perk_by_id.get(StarPlayerService._canonical_skill_id(raw_skill))
            if not perk:
                display_lookup[raw_skill] = raw_skill
                continue

            display_name = StarPlayerService._localized_name(
                perk.name,
                StarPlayerService._strip_skill_parameter(raw_skill),
            )
            parameter = StarPlayerService._extract_skill_parameter(raw_skill)
            display_lookup[raw_skill] = (
                f"{display_name} ({parameter})" if parameter else display_name
            )

        return display_lookup

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
    async def get_all_star_players_detail() -> list[StarPlayerDetail]:
        """Get full detail for all star players in a single query."""
        star_players = await StarPlayer.find_all().to_list()
        skill_lookup = await StarPlayerService._skill_display_lookup(star_players)
        results = []
        for sp in star_players:
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
            results.append(
                StarPlayerDetail(
                    id=sp.id,
                    name=sp.name,
                    cost=sp.cost,
                    stats=stats,
                    player_types=sp.player_types,
                    skills=[skill_lookup.get(skill, skill) for skill in sp.skills],
                    special_ability=special_ability,
                    plays_for=sp.plays_for,
                    image=sp.image,
                )
            )
        return results

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

        skill_lookup = await StarPlayerService._skill_display_lookup([sp])

        return StarPlayerDetail(
            id=sp.id,
            name=sp.name,
            cost=sp.cost,
            stats=stats,
            player_types=sp.player_types,
            skills=[skill_lookup.get(skill, skill) for skill in sp.skills],
            special_ability=special_ability,
            plays_for=sp.plays_for,
            image=sp.image,
        )

    @staticmethod
    async def get_star_players_for_team(
        team_id: str, favoured_of: Optional[str] = None
    ) -> list[StarPlayerSummary]:
        """Get all star players available for a specific team."""
        star_players = await StarPlayer.find({"plays_for": team_id}).to_list()
        star_players = [
            sp
            for sp in star_players
            if star_player_available_for_roster(
                star_player_id=sp.id,
                plays_for=sp.plays_for,
                roster_id=team_id,
                favoured_of=favoured_of,
            )
        ]

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
