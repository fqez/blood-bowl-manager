"""Service for base roster operations (read-only catalog)."""

import json
import logging
import re
from functools import lru_cache
from pathlib import Path
from typing import Optional

from models.base.roster import BasePlayer, BaseRoster
from schemas.base_roster import (
    BasePerkResponse,
    BasePlayerResponse,
    BaseRosterDetail,
    BaseRosterHatredKeywordsResponse,
    BaseRosterSummary,
    BaseStatsResponse,
)

logger = logging.getLogger(__name__)

_BASE_TEAMS_PATH = Path(__file__).resolve().parent.parent / "config" / "base_teams.json"
_EXCLUDED_HATRED_KEYWORDS = {
    "big guy",
    "blitzer",
    "blutzer",
    "bloqueador",
    "blocker",
    "catcher",
    "corredor",
    "defender",
    "defensor",
    "especial",
    "grandullon",
    "lanzador",
    "line",
    "linea",
    "lineman",
    "linewoman",
    "posicional",
    "positional",
    "receptor",
    "receptora",
    "runner",
    "special",
    "thrower",
    "tipo grande",
}


def _english_text(value: object) -> str:
    return str(value or "").split(" / ", 1)[0].strip()


def _normalize_ascii_text(value: str) -> str:
    replacements = str.maketrans(
        {
            "á": "a",
            "à": "a",
            "ä": "a",
            "â": "a",
            "Á": "a",
            "À": "a",
            "Ä": "a",
            "Â": "a",
            "é": "e",
            "è": "e",
            "ë": "e",
            "ê": "e",
            "É": "e",
            "È": "e",
            "Ë": "e",
            "Ê": "e",
            "í": "i",
            "ì": "i",
            "ï": "i",
            "î": "i",
            "Í": "i",
            "Ì": "i",
            "Ï": "i",
            "Î": "i",
            "ó": "o",
            "ò": "o",
            "ö": "o",
            "ô": "o",
            "Ó": "o",
            "Ò": "o",
            "Ö": "o",
            "Ô": "o",
            "ú": "u",
            "ù": "u",
            "ü": "u",
            "û": "u",
            "Ú": "u",
            "Ù": "u",
            "Ü": "u",
            "Û": "u",
            "ñ": "n",
            "Ñ": "n",
        }
    )
    return value.translate(replacements).lower()


def _normalize_rule_keyword(value: str) -> str:
    normalized = _normalize_ascii_text(value)
    normalized = re.sub(r"[^a-z0-9]+", " ", normalized)
    return re.sub(r"\s+", " ", normalized).strip()


def _normalize_roster_key(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", _normalize_ascii_text(value))


def _extract_hatred_keywords(position_labels: list[str]) -> list[str]:
    keywords: list[str] = []
    seen: set[str] = set()

    for position_label in position_labels:
        english_label = _english_text(position_label)
        if not english_label:
            continue

        for match in re.finditer(r"\(([^)]*)\)", english_label):
            values = match.group(1)
            if not values:
                continue

            for raw_keyword in values.split(","):
                keyword = raw_keyword.strip()
                if not keyword:
                    continue

                normalized_keyword = _normalize_rule_keyword(keyword)
                if (
                    not normalized_keyword
                    or normalized_keyword in _EXCLUDED_HATRED_KEYWORDS
                    or normalized_keyword in seen
                ):
                    continue

                seen.add(normalized_keyword)
                keywords.append(keyword)

    return keywords


@lru_cache(maxsize=1)
def _hatred_keywords_by_roster() -> dict[str, list[str]]:
    with _BASE_TEAMS_PATH.open(encoding="utf-8-sig") as handle:
        catalog = json.load(handle)

    keywords_by_roster: dict[str, list[str]] = {}
    for raw_team in catalog:
        if not isinstance(raw_team, dict):
            continue

        roster_name = _normalize_roster_key(str(raw_team.get("name", "")))
        roster_entries = raw_team.get("roster")
        if not roster_name or not isinstance(roster_entries, list):
            continue

        keywords_by_roster[roster_name] = _extract_hatred_keywords(
            [
                str(raw_position.get("position", ""))
                for raw_position in roster_entries
                if isinstance(raw_position, dict)
            ]
        )

    return keywords_by_roster


@lru_cache(maxsize=1)
def _all_hatred_keywords() -> list[str]:
    keywords: list[str] = []
    seen: set[str] = set()

    for roster_keywords in _hatred_keywords_by_roster().values():
        for keyword in roster_keywords:
            normalized_keyword = _normalize_rule_keyword(keyword)
            if not normalized_keyword or normalized_keyword in seen:
                continue

            seen.add(normalized_keyword)
            keywords.append(keyword)

    return keywords


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
                    BasePerkResponse(
                        id=pk.id,
                        name=pk.name,
                        parameter=pk.parameter,
                        category=pk.category,
                    )
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
    async def get_hatred_keywords(
        roster_id: str,
    ) -> Optional[BaseRosterHatredKeywordsResponse]:
        """Get valid Hatred(X) keywords from the canonical roster catalog."""
        roster = await BaseRoster.find_one(BaseRoster.id == roster_id)

        if not roster:
            return None

        return BaseRosterHatredKeywordsResponse(
            roster_id=roster.id,
            keywords=_hatred_keywords_by_roster().get(
                _normalize_roster_key(roster.id),
                [],
            ),
        )

    @staticmethod
    async def get_all_hatred_keywords() -> BaseRosterHatredKeywordsResponse:
        """Get all valid Hatred(X) keywords across every canonical base roster."""
        return BaseRosterHatredKeywordsResponse(
            roster_id="all",
            keywords=_all_hatred_keywords(),
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
