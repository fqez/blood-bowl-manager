"""Inducement rules catalog."""

from typing import Optional

from beanie import Document
from pydantic import BaseModel, Field

from models.base.expensive_mistake import LocalizedText


class InducementCostOption(BaseModel):
    """A cost that can vary by team rule or roster."""

    label: LocalizedText
    cost: int = Field(..., ge=0)
    applies_to: str = Field(default="any")
    max_per_team: Optional[int] = Field(default=None, ge=1)


class InducementRule(BaseModel):
    """A purchasable inducement entry."""

    id: str
    name: LocalizedText
    category: str
    max_per_team: int = Field(..., ge=1)
    cost: Optional[int] = Field(default=None, ge=0)
    cost_options: list[InducementCostOption] = Field(default_factory=list)
    availability: str = Field(default="any")
    required_special_rules: list[str] = Field(default_factory=list)
    duration: str = Field(default="game")
    description: LocalizedText
    notes: list[LocalizedText] = Field(default_factory=list)


class PrayerToNuffleResult(BaseModel):
    """A D16 Prayers to Nuffle table result."""

    roll: int = Field(..., ge=1, le=16)
    code: str
    description: LocalizedText


class InducementBudgetRules(BaseModel):
    """League play petty cash rules for inducements."""

    petty_cash_top_up_limit: int = Field(default=50_000, ge=0)
    lower_ctv_receives_difference: bool = True
    lower_ctv_receives_opponent_treasury_spend: bool = True
    unspent_petty_cash_lost: bool = True
    equal_ctv_treasury_spend_allowed: bool = False
    description: LocalizedText


class InducementRules(Document):
    """Database-backed inducement catalog and pre-game budget rules."""

    id: str = Field(default="inducements")
    budget: InducementBudgetRules
    inducements: list[InducementRule] = Field(default_factory=list)
    prayers_to_nuffle: list[PrayerToNuffleResult] = Field(default_factory=list)

    class Settings:
        name = "rules_catalog"
