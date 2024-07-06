from enum import Enum

from beanie import Document
from perk import Perk
from stats import Stats


class Status(Enum):
    HEALTHY = "Healthy"
    INJURED = "Injured"
    DEAD = "Dead"


class Character(Document):
    character_id: str
    character_name: str
    character_status: Status
    character_perks: list[Perk]
    character_stats: Stats

    class Config:
        json_schema_extra = {
            "example": {
                "team_id": "teamId1",
                "team_name": "Team One",
            }
        }

    class Settings:
        name = "student"


class TeamProjection(Document):
    team_id: str
    team_name: str

    class Config:
        json_schema_extra = {
            "example": {
                "team_id": "teamId1",
                "team_name": "Team One",
            }
        }

    class Settings:
        name = "student"
