"""Schemas for star player endpoints."""

from typing import Optional

from pydantic import BaseModel


class StarPlayerStatsResponse(BaseModel):
    """Stats display format for star players."""

    MA: int
    ST: int
    AG: str  # "4+" format for display
    PA: Optional[str]  # "6+" or "-" if can't pass
    AV: str  # "8+" format

    @classmethod
    def from_stats(
        cls, ma: int, st: int, ag: int, pa: Optional[int], av: int
    ) -> "StarPlayerStatsResponse":
        return cls(MA=ma, ST=st, AG=f"{ag}+", PA=f"{pa}+" if pa else "-", AV=f"{av}+")


class SpecialAbilityResponse(BaseModel):
    """Special ability info for display."""

    name: str
    description: str


class StarPlayerSummary(BaseModel):
    """Summary for star player list."""

    id: str
    name: str
    cost: int
    player_types: list[str]
    plays_for_count: int  # Number of teams that can hire


class StarPlayerDetail(BaseModel):
    """Full star player detail."""

    id: str
    name: str
    cost: int
    stats: StarPlayerStatsResponse
    player_types: list[str]
    skills: list[str]
    special_ability: Optional[SpecialAbilityResponse] = None
    plays_for: list[str]
    image: Optional[str] = None
