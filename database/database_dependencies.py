# database/dependencies.py
from typing import Type

from models.team.character import Character
from models.team.perk import Perk
from models.team.team import Team
from models.user.admin import Admin

from .mongo_database import MongoDatabase

admin_collection: Type[Admin] = Admin
perk_collection: Type[Perk] = Perk
team_collection: Type[Team] = Team
character_collection: Type[Character] = Character


def get_team_database():
    return MongoDatabase(collection=team_collection)


def get_character_database():
    return MongoDatabase(collection=character_collection)


def get_perk_database():
    return MongoDatabase(collection=perk_collection)


def get_admin_database():
    return MongoDatabase(collection=admin_collection)
