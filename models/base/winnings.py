"""Post-game winnings rules catalog."""

from beanie import Document
from pydantic import Field

from models.base.expensive_mistake import LocalizedText


class WinningsRules(Document):
    """Database-backed post-game winnings formula."""

    id: str = Field(default="winnings")
    fan_attendance_divisor: int = Field(default=2, ge=1)
    no_stalling_bonus: int = Field(default=1, ge=0)
    gold_multiplier: int = Field(default=10_000, ge=1)
    description: LocalizedText

    class Settings:
        name = "rules_catalog"
