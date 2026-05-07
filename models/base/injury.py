"""Injury and casualty rules catalog."""

from beanie import Document
from pydantic import BaseModel, Field

from models.base.expensive_mistake import LocalizedText


class DiceTableEntry(BaseModel):
    """Result for a dice range in an official rules table."""

    min_roll: int = Field(..., ge=1)
    max_roll: int = Field(..., ge=1)
    code: str
    label: LocalizedText
    description: LocalizedText


class CasualtyTableEntry(DiceTableEntry):
    """Casualty table result and required backend effect."""

    player_status: str
    injury_codes: list[str] = Field(default_factory=list)
    requires_lasting_injury_roll: bool = False


class LastingInjuryTableEntry(DiceTableEntry):
    """Lasting injury table result and stat reduction."""

    stat: str = Field(..., pattern="^(MA|ST|AG|PA|AV)$")
    reduction_label: str


class InjuryRules(Document):
    """Database-backed injury, casualty and lasting injury rules."""

    id: str = Field(default="injury_rules")
    injury_table: list[DiceTableEntry]
    stunty_injury_table: list[DiceTableEntry]
    casualty_table: list[CasualtyTableEntry]
    lasting_injury_table: list[LastingInjuryTableEntry]

    class Settings:
        name = "rules_catalog"
