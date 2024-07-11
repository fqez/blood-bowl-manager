from typing import Type

from models.student import Student
from models.team.character import Character
from models.team.perk import Perk
from models.team.team import Team
from models.user.admin import Admin

admin_collection: Type[Admin] = Admin
student_collection: Type[Student] = Student
perk_collection: Type[Perk] = Perk
team_collection: Type[Team] = Team
character_collection: Type[Character] = Character
