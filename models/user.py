from beanie import Document
from pydantic import EmailStr

from models.team import TeamProjection


class User(Document):
    fullname: str
    username: str
    email: EmailStr
    teams: list[TeamProjection]

    class Config:
        json_schema_extra = {
            "example": {
                "fullname": "Skull Crusher",
                "username": "skull99",
                "email": "skull@crusher.com",
                "teams": [
                    {"team_id": "teamId1", "team_name": "Team One"},
                    {"team_id": "teamId2", "team_name": "Team Two"},
                ],
            }
        }

    class Settings:
        name = "user"
