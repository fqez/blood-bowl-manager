from beanie import Document
from character import Character


class Team(Document):
    team_id: str
    team_name: str
    players: list[Character]

    class Config:
        json_schema_extra = {
            "example": {
                "team_id": "teamId1",
                "team_name": "Team One",
            }
        }

    class Settings:
        name = "team"


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
        name = "teamprojection"
