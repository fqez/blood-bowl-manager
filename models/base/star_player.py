"""Star Player models - Legendary players for hire in Blood Bowl."""

from typing import Optional

from beanie import Document
from pydantic import BaseModel, Field


class StarPlayerStats(BaseModel):
    """Statistics for a star player."""

    MA: int = Field(..., ge=1, le=10, description="Movement Allowance")
    ST: int = Field(..., ge=1, le=8, description="Strength")
    AG: int = Field(..., ge=1, le=6, description="Agility (roll needed)")
    PA: Optional[int] = Field(
        None, ge=1, le=6, description="Passing (roll needed), None if can't pass"
    )
    AV: int = Field(..., ge=3, le=12, description="Armor Value")


class SpecialAbility(BaseModel):
    """Special ability unique to a star player."""

    name: str = Field(..., description="Ability name")
    description: str = Field(..., description="Ability description")


class StarPlayer(Document):
    """
    Star Player - Legendary mercenary players available for hire.

    Star Players are famous Blood Bowl players that can be hired by
    compatible teams for a single match. They have unique abilities
    and impressive stats.
    """

    id: str = Field(..., description="Star player identifier (e.g., 'morg_n_thorg')")
    name: str = Field(..., description="Display name (e.g., 'Morg 'n' Thorg')")
    cost: int = Field(..., ge=0, description="Hiring cost in gold")
    stats: StarPlayerStats
    player_types: list[str] = Field(
        default_factory=list, description="Player type/position tags"
    )
    skills: list[str] = Field(default_factory=list, description="List of skill names")
    special_ability: Optional[SpecialAbility] = Field(
        None, description="Unique special ability"
    )
    plays_for: list[str] = Field(
        ..., min_length=1, description="Team IDs that can hire this star player"
    )
    image: Optional[str] = None

    class Settings:
        name = "star_players"

    class Config:
        json_schema_extra = {
            "example": {
                "id": "morg_n_thorg",
                "name": "Morg 'n' Thorg",
                "cost": 380000,
                "stats": {"MA": 6, "ST": 6, "AG": 4, "PA": 5, "AV": 11},
                "player_types": ["Big Guy"],
                "skills": [
                    "Block",
                    "Loner (4+)",
                    "Mighty Blow",
                    "Thick Skull",
                    "Throw Team-mate",
                ],
                "special_ability": {
                    "name": "The Mightiest Blow",
                    "description": "Once per game, when Morg uses Mighty Blow...",
                },
                "plays_for": ["amazon", "chaos_chosen", "dwarf", "human"],
            }
        }
