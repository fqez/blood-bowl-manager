"""Schemas for rules catalog endpoints."""

from typing import Optional

from pydantic import BaseModel


class LocalizedTextResponse(BaseModel):
    """Localized display text."""

    en: str
    es: str


class ExpensiveMistakeBandResponse(BaseModel):
    """Treasury band and D6 lookup results."""

    min_treasury: int
    max_treasury: Optional[int] = None
    results: list[str]


class ExpensiveMistakeEffectResponse(BaseModel):
    """Result effect definition."""

    code: str
    label: LocalizedTextResponse
    description: LocalizedTextResponse
    calculation: str
    required_dice: list[str]


class ExpensiveMistakesRulesResponse(BaseModel):
    """Database-backed expensive mistakes rule table."""

    id: str
    min_treasury: int
    bands: list[ExpensiveMistakeBandResponse]
    effects: list[ExpensiveMistakeEffectResponse]
