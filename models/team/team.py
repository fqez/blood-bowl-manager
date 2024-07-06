import uuid
from typing import Optional

from beanie import Document
from pydantic import BaseModel

from models.team.character import Character


class Team(Document):
    id: str = uuid.uuid4().hex
    name: str
    base_team_id: str
    roster: list[Character]
    reroll_cost: str
    rerolls: int = 0
    cheerleaders: int = 0
    assistant_coaches: int = 0
    apothecary: bool = False
    fan_factor: int = 0
    treasury: int = 1_000_000
    wallpaper: Optional[str]
    icon: Optional[str]

    class Config:
        json_schema_extra = {
            "example": {
                "id": "user-shambling-n",
                "name": "Shambling Undead",
                "roster": [
                    {
                        "name": "Skeleton Lineman",
                        "number": "10",
                        "character_type": "skeleton-lineman",
                        "base_team_id": "shambling-undead",
                        "value": "40,000",
                        "stats": {
                            "MA": "5",
                            "ST": "3",
                            "AG": "4+",
                            "PA": "6+",
                            "AV": "8+",
                        },
                        "perks": ["perk-regeneration", "perk-thick-skull"],
                        "image": "shambling/skeleton.png",
                        "tag_image": "shambling/skeleton_tag.png",
                    },
                    {
                        "name": "Zombie Lineman",
                        "max": 12,
                        "qty": 0,
                        "cost": "40,000",
                        "stats": {
                            "MA": "4",
                            "ST": "3",
                            "AG": "4+",
                            "PA": "-",
                            "AV": "9+",
                        },
                        "perks": ["perk-regeneration"],
                        "image": "shambling/zombie.png",
                        "tag_image": "shambling/zombie_tag.png",
                    },
                    {
                        "name": "Ghoul Runner",
                        "max": 4,
                        "qty": 0,
                        "cost": "75,000",
                        "stats": {
                            "MA": "7",
                            "ST": "3",
                            "AG": "3+",
                            "PA": "4+",
                            "AV": "8+",
                        },
                        "perks": ["perk-dodge"],
                        "image": "shambling/ghoul.png",
                        "tag_image": "shambling/ghoul_tag.png",
                    },
                    {
                        "name": "Wight Blitzer",
                        "max": 2,
                        "qty": 0,
                        "cost": "90,000",
                        "stats": {
                            "MA": "6",
                            "ST": "3",
                            "AG": "3+",
                            "PA": "4+",
                            "AV": "9+",
                        },
                        "perks": ["perk-regeneration", "perk-block"],
                        "image": "shambling/wight.png",
                        "tag_image": "shambling/wight_tag.png",
                    },
                    {
                        "name": "Mummy",
                        "max": 2,
                        "qty": 0,
                        "cost": "125,000",
                        "stats": {
                            "MA": "3",
                            "ST": "5",
                            "AG": "5+",
                            "PA": "-",
                            "AV": "10+",
                        },
                        "perks": ["perk-regeneration", "perk-mighty-blow:1"],
                        "image": "shambling/mummy.png",
                        "tag_image": "shambling/mummy_tag.png",
                    },
                ],
                "reroll_cost": "70,000",
                "wallpaper": "shambling/wallpaper.jpg",
                "icon": "shambling/icon.png",
            }
        }

    class Settings:
        name = "team"


class TeamProjection(BaseModel):
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
