# Legacy models (kept for backwards compatibility)
# New models for restructured data
from models.base.roster import BaseRoster
from models.base.skill_family import SkillFamily
from models.base.star_player import StarPlayer
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
]
