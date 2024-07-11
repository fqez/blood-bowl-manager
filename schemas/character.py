from typing import Any, Optional

from pydantic import BaseModel

from models.team.character import Status
from models.team.perk import Perk
from models.team.stats import Stats


class CreateCharacter(BaseModel):
    team_id: str
    name: str
    number: str
    character_type: str
    status: Status = Status.HEALTHY
    value: str
    stats: Stats
    perks: list[str]


class CharacterProjection(BaseModel):
    id: str
    team_id: str
    name: str
    number: str
    character_type: str
    status: str
    value: str
    stats: dict
    perks: list[Perk]


class UpdateCharacter(BaseModel):
    name: Optional[str] = None
    number: Optional[str] = None
    character_type: Optional[str] = None
    status: Optional[str] = None
    value: Optional[str] = None
    stats: Optional[dict] = None
    perks: Optional[list[str]] = None

    class Config:
        json_schema_extra = {
            "example": {
                "id": "user-shambling-n",
                "name": "Shambling Undead",
                "squad": [
                    {
                        "name": "Skeleton Lineman",
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
                        "perks": [
                            "perk-dodge",
                        ],
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
        name = "teams"


class Response(BaseModel):
    status_code: int
    response_type: str
    description: str
    data: Optional[Any]

    class Config:
        json_schema_extra = {
            "example": {
                "status_code": 200,
                "response_type": "success",
                "description": "Operation successful",
                "data": "Sample data",
            }
        }
