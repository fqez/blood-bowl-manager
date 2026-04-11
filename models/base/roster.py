"""Base roster models - Immutable catalog data for Blood Bowl teams."""

from typing import Optional

from beanie import Document
from pydantic import BaseModel, Field


class BaseStats(BaseModel):
    """Base statistics for a player type."""

    MA: int = Field(..., ge=1, le=10, description="Movement Allowance")
    ST: int = Field(..., ge=1, le=8, description="Strength")
    AG: int = Field(..., ge=1, le=6, description="Agility (roll needed)")
    PA: Optional[int] = Field(
        None, ge=1, le=6, description="Passing (roll needed), None if can't pass"
    )
    AV: int = Field(..., ge=3, le=12, description="Armor Value")


class BasePerk(BaseModel):
    """Embedded perk in a player type."""

    id: str = Field(..., description="Perk identifier")
    name: str = Field(..., description="Display name")
    category: str = Field(
        ...,
        pattern="^[GASPMDT]$",
        description="G=General, A=Agility, S=Strength, P=Passing, M=Mutation, D=Devious, T=Trait",
    )


class BasePlayer(BaseModel):
    """A player type available in a roster (e.g., 'Skeleton Lineman')."""

    type: str = Field(..., description="Unique type identifier within the roster")
    name: str = Field(..., description="Display name")
    position: str = Field(
        ..., description="Position category: Lineman, Blitzer, Thrower, etc."
    )
    max: int = Field(..., ge=1, le=16, description="Maximum allowed in a team")
    cost: int = Field(..., ge=0, description="Hiring cost in gold")
    stats: BaseStats
    perks: list[BasePerk] = Field(default_factory=list, description="Starting skills")
    primary_access: list[str] = Field(
        default_factory=list, description="Primary skill categories"
    )
    secondary_access: list[str] = Field(
        default_factory=list, description="Secondary skill categories"
    )
    image: Optional[str] = None
    tag_image: Optional[str] = None


class BaseRoster(Document):
    """
    Immutable roster definition for a Blood Bowl race.

    Contains all player types available for hiring when creating a team
    of this race. This data comes from the official rules and should
    not be modified during normal app usage.
    """

    id: str = Field(..., description="Roster identifier (e.g., 'shambling-undead')")
    name: str = Field(..., description="Display name (e.g., 'Shambling Undead')")
    reroll_cost: int = Field(..., ge=0, description="Cost per team reroll")
    apothecary_allowed: bool = Field(
        default=True, description="Whether team can hire an apothecary"
    )
    tier: int = Field(..., ge=1, le=3, description="Tier rating (1=top, 3=lowest)")
    special_rules: list[str] = Field(
        default_factory=list, description="Team special rules"
    )
    players: list[BasePlayer] = Field(
        ..., min_length=1, description="Available player types"
    )
    icon: Optional[str] = None
    wallpaper: Optional[str] = None

    class Settings:
        name = "base_rosters"

    class Config:
        json_schema_extra = {
            "example": {
                "id": "shambling-undead",
                "name": "Shambling Undead",
                "reroll_cost": 70000,
                "apothecary_allowed": False,
                "tier": 2,
                "special_rules": ["Sylvanian Spotlight", "Masters of Undeath"],
                "players": [
                    {
                        "type": "skeleton-lineman",
                        "name": "Skeleton Lineman",
                        "position": "Lineman",
                        "max": 12,
                        "cost": 40000,
                        "stats": {"MA": 5, "ST": 3, "AG": 4, "PA": 6, "AV": 8},
                        "perks": [
                            {
                                "id": "regeneration",
                                "name": "Regeneration",
                                "category": "M",
                            },
                            {
                                "id": "thick-skull",
                                "name": "Thick Skull",
                                "category": "S",
                            },
                        ],
                        "primary_access": ["G"],
                        "secondary_access": ["A", "S"],
                    }
                ],
            }
        }
