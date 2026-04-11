"""Database collection references.

Note: This module is kept for backwards compatibility.
Prefer using dependency injection via database_dependencies.py
"""

from typing import Type

from models.team.character import Character
from models.team.perk import Perk
from models.team.team import Team
from models.user.admin import Admin

admin_collection: Type[Admin] = Admin
perk_collection: Type[Perk] = Perk
team_collection: Type[Team] = Team
character_collection: Type[Character] = Character
