"""Post-game league points rules catalog."""

from beanie import Document
from pydantic import Field

from models.base.expensive_mistake import LocalizedText


class LeaguePointsRules(Document):
    """Database-backed league points and bonus points rules."""

    id: str = Field(default="league_points")
    win_points: int = Field(default=3, ge=0)
    draw_points: int = Field(default=1, ge=0)
    loss_points: int = Field(default=0, ge=0)
    touchdown_bonus_threshold: int = Field(default=3, ge=0)
    touchdown_bonus_points: int = Field(default=1, ge=0)
    shutout_bonus_points: int = Field(default=1, ge=0)
    casualty_bonus_threshold: int = Field(default=3, ge=0)
    casualty_bonus_points: int = Field(default=1, ge=0)
    casualty_bonus_requires_spp: bool = Field(default=True)
    description: LocalizedText

    class Settings:
        name = "rules_catalog"
