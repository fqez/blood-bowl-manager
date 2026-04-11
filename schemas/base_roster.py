"""Schemas for base roster endpoints."""

from typing import Optional

from pydantic import BaseModel


class BaseStatsResponse(BaseModel):
    """Stats display format."""

    MA: int
    ST: int
    AG: str  # "4+" format for display
    PA: Optional[str]  # "6+" or "-" if can't pass
    AV: str  # "8+" format

    @classmethod
    def from_stats(
        cls, ma: int, st: int, ag: int, pa: Optional[int], av: int
    ) -> "BaseStatsResponse":
        return cls(MA=ma, ST=st, AG=f"{ag}+", PA=f"{pa}+" if pa else "-", AV=f"{av}+")


class BasePerkResponse(BaseModel):
    """Perk info for display."""

    id: str
    name: str
    category: str


class BasePlayerResponse(BaseModel):
    """Player type available in a roster."""

    type: str
    name: str
    position: str
    max: int
    cost: int
    stats: BaseStatsResponse
    perks: list[BasePerkResponse]
    primary_access: list[str]
    secondary_access: list[str]
    image: Optional[str] = None


class BaseRosterSummary(BaseModel):
    """Summary for roster list."""

    id: str
    name: str
    tier: int
    apothecary_allowed: bool
    reroll_cost: int
    icon: Optional[str] = None


class BaseRosterDetail(BaseModel):
    """Full roster detail with all player types."""

    id: str
    name: str
    tier: int
    reroll_cost: int
    apothecary_allowed: bool
    special_rules: list[str]
    players: list[BasePlayerResponse]
    icon: Optional[str] = None
    wallpaper: Optional[str] = None
