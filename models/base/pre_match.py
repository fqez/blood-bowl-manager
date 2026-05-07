"""Pre-match Weather and Kick-off Event rules catalog."""

from beanie import Document
from pydantic import BaseModel, Field

from models.base.expensive_mistake import LocalizedText


class DiceRangeTableEntry(BaseModel):
    """A 2D6 table entry with localized effect text."""

    min_roll: int = Field(..., ge=2, le=12)
    max_roll: int = Field(..., ge=2, le=12)
    code: str
    label: LocalizedText
    description: LocalizedText


class WeatherRules(Document):
    """Database-backed 2D6 Weather table."""

    id: str = Field(default="weather")
    roll_dice: str = Field(default="2D6")
    description: LocalizedText
    table: list[DiceRangeTableEntry] = Field(default_factory=list)

    class Settings:
        name = "rules_catalog"


class KickoffEventRules(Document):
    """Database-backed 2D6 Kick-off Event table."""

    id: str = Field(default="kickoff_events")
    roll_dice: str = Field(default="2D6")
    description: LocalizedText
    table: list[DiceRangeTableEntry] = Field(default_factory=list)

    class Settings:
        name = "rules_catalog"
