"""Schemas for tactic endpoints."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class PlacedPlayerSchema(BaseModel):
    row: int = Field(..., ge=0, le=12)
    col: int = Field(..., ge=0, le=14)
    position_id: str


class CreateTacticRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    base_roster_id: str
    mode: str = Field(default="attack", pattern="^(attack|defense)$")
    placements: list[PlacedPlayerSchema] = Field(default_factory=list)
    good_against: list[str] = Field(default_factory=list)
    notes: str = Field(default="", max_length=2000)


class UpdateTacticRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    mode: Optional[str] = Field(None, pattern="^(attack|defense)$")
    placements: Optional[list[PlacedPlayerSchema]] = None
    good_against: Optional[list[str]] = None
    notes: Optional[str] = Field(None, max_length=2000)


class TacticResponse(BaseModel):
    id: str
    user_id: str
    name: str
    base_roster_id: str
    mode: str
    placements: list[PlacedPlayerSchema]
    good_against: list[str]
    notes: str
    created_at: datetime
    updated_at: datetime


class TacticSummary(BaseModel):
    id: str
    name: str
    base_roster_id: str
    mode: str
    player_count: int
    good_against_count: int
    created_at: datetime
    updated_at: datetime
