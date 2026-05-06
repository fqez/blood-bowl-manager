"""Expensive mistakes rules catalog."""

from typing import Optional

from beanie import Document
from pydantic import BaseModel, Field


class LocalizedText(BaseModel):
    """Localized display text."""

    en: str
    es: str


class ExpensiveMistakeBand(BaseModel):
    """Treasury band and D6 lookup results."""

    min_treasury: int = Field(..., ge=0)
    max_treasury: Optional[int] = Field(None, ge=0)
    results: list[str] = Field(..., min_length=6, max_length=6)


class ExpensiveMistakeEffect(BaseModel):
    """Result effect definition."""

    code: str
    label: LocalizedText
    description: LocalizedText
    calculation: str
    required_dice: list[str] = Field(default_factory=list)


class ExpensiveMistakesRules(Document):
    """Database-backed expensive mistakes rule table."""

    id: str = Field(default="expensive_mistakes")
    min_treasury: int = Field(default=100_000, ge=0)
    bands: list[ExpensiveMistakeBand]
    effects: list[ExpensiveMistakeEffect]

    class Settings:
        name = "rules_catalog"
