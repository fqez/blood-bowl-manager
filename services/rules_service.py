"""Services for rules catalog endpoints."""

from models.base.dedicated_fans import DedicatedFansRules
from models.base.expensive_mistake import ExpensiveMistakesRules
from models.base.inducement import InducementRules
from models.base.injury import InjuryRules
from models.base.pre_match import KickoffEventRules, WeatherRules
from models.base.spp import SppRewardsRules
from models.base.winnings import WinningsRules


class RulesService:
    """Rules catalog service."""

    @staticmethod
    async def get_expensive_mistakes_rules() -> ExpensiveMistakesRules | None:
        """Return the expensive mistakes rules document."""
        return await ExpensiveMistakesRules.get("expensive_mistakes")

    @staticmethod
    async def get_spp_rewards_rules() -> SppRewardsRules | None:
        """Return the SPP reward rules document."""
        return await SppRewardsRules.get("spp_rewards")

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
