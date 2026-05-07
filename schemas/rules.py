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


class SppEventRewardResponse(BaseModel):
    """SPP reward attached to a match event type."""

    event_type: str
    spp: int
    career_stat: Optional[str] = None
    requires_player: bool
    description: LocalizedTextResponse


class ThrowTeammateRewardResponse(BaseModel):
    """Special SPP rule for Throw Team-Mate."""

    event_type: str
    thrown_player_landed_spp: int
    superb_thrower_spp: int
    description: LocalizedTextResponse


class SppRewardsRulesResponse(BaseModel):
    """Database-backed SPP reward rules."""

    id: str
    event_rewards: list[SppEventRewardResponse]
    mvp_spp: int
    non_spp_event_types: list[str]
    throw_teammate: ThrowTeammateRewardResponse


class DiceTableEntryResponse(BaseModel):
    """Result for a dice range in an official rules table."""

    min_roll: int
    max_roll: int
    code: str
    label: LocalizedTextResponse
    description: LocalizedTextResponse


class CasualtyTableEntryResponse(DiceTableEntryResponse):
    """Casualty table result and backend effect."""

    player_status: str
    injury_codes: list[str]
    requires_lasting_injury_roll: bool


class LastingInjuryTableEntryResponse(DiceTableEntryResponse):
    """Lasting injury table result and stat reduction."""

    stat: str
    reduction_label: str


class InjuryRulesResponse(BaseModel):
    """Database-backed injury, casualty and lasting injury rules."""

    id: str
    injury_table: list[DiceTableEntryResponse]
    stunty_injury_table: list[DiceTableEntryResponse]
    casualty_table: list[CasualtyTableEntryResponse]
    lasting_injury_table: list[LastingInjuryTableEntryResponse]


class WinningsRulesResponse(BaseModel):
    """Database-backed post-game winnings formula."""

    id: str
    fan_attendance_divisor: int
    no_stalling_bonus: int
    gold_multiplier: int
    description: LocalizedTextResponse


class DedicatedFansRulesResponse(BaseModel):
    """Database-backed post-game Dedicated Fans update rules."""

    id: str
    min_value: int
    max_value: int
    win_roll_operator: str
    loss_roll_operator: str
    description: LocalizedTextResponse


class InducementCostOptionResponse(BaseModel):
    """A cost option for an inducement with variable pricing."""

    label: LocalizedTextResponse
    cost: int
    applies_to: str
    max_per_team: Optional[int] = None


class InducementRuleResponse(BaseModel):
    """Database-backed inducement catalog entry."""

    id: str
    name: LocalizedTextResponse
    category: str
    max_per_team: int
    cost: Optional[int] = None
    cost_options: list[InducementCostOptionResponse]
    availability: str
    required_special_rules: list[str]
    duration: str
    description: LocalizedTextResponse
    notes: list[LocalizedTextResponse]


class PrayerToNuffleResultResponse(BaseModel):
    """A D16 result in the Prayers to Nuffle table."""

    roll: int
    code: str
    description: LocalizedTextResponse


class InducementBudgetRulesResponse(BaseModel):
    """Petty cash rules for buying inducements in league play."""

    petty_cash_top_up_limit: int
    lower_ctv_receives_difference: bool
    lower_ctv_receives_opponent_treasury_spend: bool
    unspent_petty_cash_lost: bool
    equal_ctv_treasury_spend_allowed: bool
    description: LocalizedTextResponse


class InducementRulesResponse(BaseModel):
    """Database-backed inducement catalog and pre-game budget rules."""

    id: str
    budget: InducementBudgetRulesResponse
    inducements: list[InducementRuleResponse]
    prayers_to_nuffle: list[PrayerToNuffleResultResponse]


class DiceRangeTableEntryResponse(BaseModel):
    """2D6 table entry."""

    min_roll: int
    max_roll: int
    code: str
    label: LocalizedTextResponse
    description: LocalizedTextResponse


class WeatherRulesResponse(BaseModel):
    """Database-backed Weather table."""

    id: str
    roll_dice: str
    description: LocalizedTextResponse
    table: list[DiceRangeTableEntryResponse]


class KickoffEventRulesResponse(BaseModel):
    """Database-backed Kick-off Event table."""

    id: str
    roll_dice: str
    description: LocalizedTextResponse
    table: list[DiceRangeTableEntryResponse]
