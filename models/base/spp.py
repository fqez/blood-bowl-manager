"""SPP reward rules catalog."""

from beanie import Document
from pydantic import BaseModel, Field

from models.base.expensive_mistake import LocalizedText


class SppEventReward(BaseModel):
    """SPP reward attached to a match event type."""

    event_type: str
    spp: int = Field(..., ge=0)
    career_stat: str | None = None
    requires_player: bool = True
    description: LocalizedText


class ThrowTeammateReward(BaseModel):
    """Special SPP rule for Throw Team-Mate."""

    event_type: str = "throw_teammate"
    thrown_player_landed_spp: int = Field(default=1, ge=0)
    superb_thrower_spp: int = Field(default=1, ge=0)
    description: LocalizedText


class SppRewardsRules(Document):
    """Database-backed SPP reward rules."""

    id: str = Field(default="spp_rewards")
    event_rewards: list[SppEventReward]
    mvp_spp: int = Field(default=4, ge=0)
    non_spp_event_types: list[str] = Field(default_factory=list)
    throw_teammate: ThrowTeammateReward

    class Settings:
        name = "rules_catalog"
