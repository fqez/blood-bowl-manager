"""Post-game Dedicated Fans rules catalog."""

from beanie import Document
from pydantic import Field

from models.base.expensive_mistake import LocalizedText


class DedicatedFansRules(Document):
    """Database-backed post-game Dedicated Fans update rules."""

    id: str = Field(default="dedicated_fans")
    min_value: int = Field(default=1, ge=0)
    max_value: int = Field(default=7, ge=1)
    win_roll_operator: str = Field(default=">=")
    loss_roll_operator: str = Field(default="<")
    description: LocalizedText

    class Settings:
        name = "rules_catalog"
