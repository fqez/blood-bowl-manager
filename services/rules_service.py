"""Services for rules catalog endpoints."""

from typing import Any

from models.base.advancement import AdvancementRules
from models.base.dedicated_fans import DedicatedFansRules
from models.base.expensive_mistake import ExpensiveMistakesRules
from models.base.inducement import InducementRules
from models.base.injury import InjuryRules
from models.base.pre_match import KickoffEventRules, WeatherRules
from models.base.spp import SppRewardsRules
from models.base.winnings import WinningsRules


class RulesService:
    """Rules catalog service."""

    RULE_CATALOGUE: list[dict[str, Any]] = [
        {
            "id": "expensive_mistakes",
            "name": {"en": "Expensive Mistakes", "es": "Errores costosos"},
            "category": "post_match",
            "endpoint": "/rules/expensive-mistakes",
            "dice": ["D6", "D3", "2D6"],
            "table_fields": ["bands", "effects"],
        },
        {
            "id": "spp_rewards",
            "name": {"en": "SPP Rewards", "es": "Recompensas de SPP"},
            "category": "post_match",
            "endpoint": "/rules/spp-rewards",
            "dice": [],
            "table_fields": ["event_rewards", "throw_teammate"],
        },
        {
            "id": "advancement_rules",
            "name": {"en": "Player Advancements", "es": "Mejoras de jugador"},
            "category": "team_management",
            "endpoint": "/rules/advancements",
            "dice": ["2D6", "D8"],
            "table_fields": [
                "cost_table",
                "characteristic_table",
                "value_increases",
                "skill_categories",
            ],
        },
        {
            "id": "injury_rules",
            "name": {"en": "Injuries and Casualties", "es": "Heridas y lesiones"},
            "category": "post_match",
            "endpoint": "/rules/injuries",
            "dice": ["2D6", "D16", "D6"],
            "table_fields": [
                "injury_table",
                "stunty_injury_table",
                "casualty_table",
                "lasting_injury_table",
            ],
        },
        {
            "id": "winnings",
            "name": {"en": "Winnings", "es": "Ganancias"},
            "category": "post_match",
            "endpoint": "/rules/winnings",
            "dice": [],
            "table_fields": [],
        },
        {
            "id": "dedicated_fans",
            "name": {"en": "Dedicated Fans", "es": "Aficionados dedicados"},
            "category": "post_match",
            "endpoint": "/rules/dedicated-fans",
            "dice": ["D6"],
            "table_fields": [],
        },
        {
            "id": "inducements",
            "name": {"en": "Inducements", "es": "Incentivos"},
            "category": "pre_match",
            "endpoint": "/rules/inducements",
            "dice": ["D16"],
            "table_fields": ["inducements", "prayers_to_nuffle"],
        },
        {
            "id": "weather",
            "name": {"en": "Weather", "es": "Clima"},
            "category": "pre_match",
            "endpoint": "/rules/weather",
            "dice": ["2D6", "D3"],
            "table_fields": ["table"],
        },
        {
            "id": "kickoff_events",
            "name": {"en": "Kick-off Events", "es": "Eventos de saque inicial"},
            "category": "drive",
            "endpoint": "/rules/kickoff-events",
            "dice": ["2D6", "D3", "D6"],
            "table_fields": ["table"],
        },
    ]

    @staticmethod
    def _rules_catalog_collection():
        return InducementRules.get_motor_collection()

    @staticmethod
    def _catalogue_ids() -> list[str]:
        return [entry["id"] for entry in RulesService.RULE_CATALOGUE]

    @staticmethod
    def _normalize_catalog_document(document: dict[str, Any]) -> dict[str, Any]:
        normalized = dict(document)
        normalized["id"] = str(normalized.pop("_id"))
        return normalized

    @staticmethod
    async def get_rules_catalogue() -> dict[str, Any]:
        """Return an index of all known backend-owned rule documents."""
        collection = RulesService._rules_catalog_collection()
        documents = await collection.find(
            {"_id": {"$in": RulesService._catalogue_ids()}},
            {"_id": 1, "description": 1},
        ).to_list(length=None)
        documents_by_id = {str(document["_id"]): document for document in documents}

        rules = []
        for metadata in RulesService.RULE_CATALOGUE:
            document = documents_by_id.get(metadata["id"])
            entry = dict(metadata)
            entry["available"] = document is not None
            if document and isinstance(document.get("description"), dict):
                entry["description"] = document["description"]
            rules.append(entry)

        return {"id": "rules_catalog", "rules": rules}

    @staticmethod
    async def get_catalogue_document(rule_id: str) -> dict[str, Any] | None:
        """Return one raw rules document from the generic catalogue."""
        if rule_id not in RulesService._catalogue_ids():
            return None

        document = await RulesService._rules_catalog_collection().find_one(
            {"_id": rule_id}
        )
        if not document:
            return None

        normalized = RulesService._normalize_catalog_document(document)
        return {"id": normalized["id"], "document": normalized}

    @staticmethod
    async def get_expensive_mistakes_rules() -> ExpensiveMistakesRules | None:
        """Return the expensive mistakes rules document."""
        return await ExpensiveMistakesRules.get("expensive_mistakes")

    @staticmethod
    async def get_spp_rewards_rules() -> SppRewardsRules | None:
        """Return the SPP reward rules document."""
        return await SppRewardsRules.get("spp_rewards")

    @staticmethod
    async def get_advancement_rules() -> AdvancementRules | None:
        """Return the player advancement rules document."""
        return await AdvancementRules.get("advancement_rules")

    @staticmethod
    async def get_injury_rules() -> InjuryRules | None:
        """Return the injury rules document."""
        return await InjuryRules.get("injury_rules")

    @staticmethod
    async def get_winnings_rules() -> WinningsRules | None:
        """Return the post-game winnings rules document."""
        return await WinningsRules.get("winnings")

    @staticmethod
    async def get_dedicated_fans_rules() -> DedicatedFansRules | None:
        """Return the post-game Dedicated Fans rules document."""
        return await DedicatedFansRules.get("dedicated_fans")

    @staticmethod
    async def get_inducement_rules() -> InducementRules | None:
        """Return the inducement catalog and petty cash rules."""
        return await InducementRules.get("inducements")

    @staticmethod
    async def get_weather_rules() -> WeatherRules | None:
        """Return the 2D6 Weather table."""
        return await WeatherRules.get("weather")

    @staticmethod
    async def get_kickoff_event_rules() -> KickoffEventRules | None:
        """Return the 2D6 Kick-off Event table."""
        return await KickoffEventRules.get("kickoff_events")
