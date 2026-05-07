# Legacy models (kept for backwards compatibility)
# New models for restructured data
from models.base.dedicated_fans import DedicatedFansRules
from models.base.advancement import AdvancementRules
from models.base.expensive_mistake import ExpensiveMistakesRules
from models.base.inducement import InducementRules
from models.base.injury import InjuryRules
from models.base.pre_match import KickoffEventRules, WeatherRules
from models.base.roster import BaseRoster
from models.base.skill_family import SkillFamily
from models.base.spp import SppRewardsRules
from models.base.star_player import StarPlayer
from models.base.winnings import WinningsRules
from models.league.league import League
from models.quick_match.quick_match import QuickMatch
from models.tactic.tactic import Tactic
from models.team.character import Character
from models.team.perk import Perk
from models.team.team import Team
from models.user.admin import Admin
from models.user.user import User
from models.user_team.team import UserTeam

__all__ = [
    # Legacy
    Admin,
    Perk,
    Team,
    Character,
    # New
    BaseRoster,
    UserTeam,
    League,
    QuickMatch,
    User,
    StarPlayer,
    SkillFamily,
    Tactic,
    AdvancementRules,
    DedicatedFansRules,
    ExpensiveMistakesRules,
    InducementRules,
    InjuryRules,
    KickoffEventRules,
    SppRewardsRules,
    WeatherRules,
    WinningsRules,
]
