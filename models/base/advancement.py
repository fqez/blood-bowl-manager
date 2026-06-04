"""Player advancement rules catalog."""

from beanie import Document
from pydantic import BaseModel, Field

from models.base.expensive_mistake import LocalizedText


class AdvancementCostRow(BaseModel):
    """SPP costs for one advancement rank."""

    advancement_number: int = Field(..., ge=1, le=6)
    level_name: LocalizedText
    random_primary_skill: int = Field(..., ge=0)
    choose_primary_skill: int = Field(..., ge=0)
    choose_secondary_skill: int = Field(..., ge=0)
    characteristic_improvement: int = Field(..., ge=0)


class CharacteristicImprovementResult(BaseModel):
    """D8 characteristic improvement result."""

    min_roll: int = Field(..., ge=1, le=8)
    max_roll: int = Field(..., ge=1, le=8)
    choices: list[str]
    description: LocalizedText


class AdvancementValueIncrease(BaseModel):
    """Team value increase for one advancement type."""

    advancement_type: str
    value: int = Field(..., ge=0)


class SkillCategoryRule(BaseModel):
    """Official skill category shorthand."""

    symbol: str
    family: str
    name: LocalizedText


class RandomPrimarySkillTableEntry(BaseModel):
    """One official 2D6 row for random primary skill generation."""

    first_d6_min: int = Field(..., ge=1, le=6)
    first_d6_max: int = Field(..., ge=1, le=6)
    second_d6: int = Field(..., ge=1, le=6)
    perk_ids: list[str] = Field(min_length=6, max_length=6)


class AdvancementRules(Document):
    """Database-backed player advancement rules."""

    id: str = Field(default="advancement_rules")
    max_advancements: int = Field(default=6, ge=1)
    max_characteristic_improvements_per_stat: int = Field(default=2, ge=1)
    cost_table: list[AdvancementCostRow]
    characteristic_table: list[CharacteristicImprovementResult]
    value_increases: list[AdvancementValueIncrease]
    skill_categories: list[SkillCategoryRule]
    random_primary_skill_table: list[RandomPrimarySkillTableEntry]
    random_skill_rolls: int = Field(default=2, ge=1)
    random_skill_dice: str = Field(default="2D6")
    description: LocalizedText

    class Settings:
        name = "rules_catalog"
