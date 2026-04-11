import uuid
from typing import Optional

from pydantic import BaseModel, Field, field_validator

from models.team.character import Character

# Blood Bowl constants
MIN_ROSTER_SIZE = 11
MAX_ROSTER_SIZE = 16
MAX_REROLLS = 8
MAX_FAN_FACTOR = 9
MIN_TREASURY = 0


class CreateTeam(BaseModel):
    """Schema for creating a new team."""

    id: str = Field(default_factory=lambda: uuid.uuid4().hex)
    name: str = Field(..., min_length=1, max_length=50, description="Team name")
    base_team_id: str = Field(..., description="Base team type identifier")
    roster: list[Character] = Field(
        ...,
        min_length=MIN_ROSTER_SIZE,
        max_length=MAX_ROSTER_SIZE,
        description=f"Team roster ({MIN_ROSTER_SIZE}-{MAX_ROSTER_SIZE} players)",
    )
    reroll_cost: int = Field(..., gt=0, description="Cost per reroll in gold")
    rerolls: int = Field(
        default=0, ge=0, le=MAX_REROLLS, description="Number of rerolls"
    )
    cheerleaders: int = Field(
        default=0, ge=0, le=12, description="Number of cheerleaders"
    )
    assistant_coaches: int = Field(
        default=0, ge=0, le=6, description="Number of assistant coaches"
    )
    apothecary: bool = Field(
        default=False, description="Whether team has an apothecary"
    )
    fan_factor: int = Field(
        default=0, ge=0, le=MAX_FAN_FACTOR, description="Fan factor rating"
    )
    treasury: int = Field(
        default=1_000_000, ge=MIN_TREASURY, description="Team treasury in gold"
    )
    wallpaper: Optional[str] = Field(
        default=None, description="Team wallpaper image path"
    )
    icon: Optional[str] = Field(default=None, description="Team icon image path")

    @field_validator("name")
    @classmethod
    def name_must_not_be_empty(cls, v: str) -> str:
        """Validate team name is not just whitespace."""
        if not v.strip():
            raise ValueError("Team name cannot be empty or whitespace")
        return v.strip()


class TeamProjection(BaseModel):
    """Schema for team data returned to clients."""

    id: str
    name: str
    roster: list[Character]
    reroll_cost: int
    rerolls: int
    cheerleaders: int
    assistant_coaches: int
    apothecary: bool
    fan_factor: int
    treasury: int


class UpdateTeam(BaseModel):
    """Schema for updating team data."""

    name: Optional[str] = Field(default=None, min_length=1, max_length=50)
    rerolls: Optional[int] = Field(default=None, ge=0, le=MAX_REROLLS)
    cheerleaders: Optional[int] = Field(default=None, ge=0, le=12)
    assistant_coaches: Optional[int] = Field(default=None, ge=0, le=6)
    apothecary: Optional[bool] = None
    fan_factor: Optional[int] = Field(default=None, ge=0, le=MAX_FAN_FACTOR)
    treasury: Optional[int] = Field(default=None, ge=MIN_TREASURY)

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

    class Collection:
        name = "teams"


# Response class moved to schemas/responses.py as APIResponse
