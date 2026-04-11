from typing import Optional

from beanie import Document
from pydantic import Field


class Team(Document):
    """Team document model for Blood Bowl teams."""

    id: str
    name: str
    base_team_id: str
    roster: list[str] = Field(default_factory=list, description="List of character IDs")
    reroll_cost: int = Field(..., gt=0, description="Cost per reroll in gold")
    rerolls: int = Field(default=0, ge=0)
    cheerleaders: int = Field(default=0, ge=0)
    assistant_coaches: int = Field(default=0, ge=0)
    apothecary: bool = False
    fan_factor: int = Field(default=0, ge=0)
    treasury: int = Field(default=1_000_000, ge=0)
    wallpaper: Optional[str] = None
    icon: Optional[str] = None

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
        name = "teams"
