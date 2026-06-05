import pytest

from models.base.advancement import AdvancementRules, AdvancementValueIncrease
from models.base.roster import BasePlayer, BaseStats
from models.team.perk import Perk
from models.user_team.team import PlayerStats, UserPlayer
from schemas.user_team import ApplyPlayerAdvancementRequest
from services.user_team_service import UserTeamService


def _advancement_rules() -> AdvancementRules:
    return AdvancementRules.model_construct(
        id="advancement_rules",
        value_increases=[
            AdvancementValueIncrease(advancement_type="primary_skill", value=20_000),
            AdvancementValueIncrease(
                advancement_type="secondary_skill",
                value=40_000,
            ),
        ],
        skill_categories=[],
        random_primary_skill_table=[],
        cost_table=[],
        characteristic_table=[],
        max_advancements=6,
        max_characteristic_improvements_per_stat=2,
        random_skill_rolls=2,
        random_skill_dice="2D6",
        description={"es": "test"},
    )


def _base_player() -> BasePlayer:
    return BasePlayer(
        type="blitzer",
        name="Blitzer",
        position="Blitzer",
        max=4,
        cost=90_000,
        stats=BaseStats(MA=6, ST=3, AG=3, PA=4, AV=10),
        primary_access=["G"],
        secondary_access=["A"],
    )


def _user_player() -> UserPlayer:
    return UserPlayer(
        id="player-1",
        base_type="blitzer",
        name="Blitzer",
        number=1,
        current_value=90_000,
        stats=PlayerStats(MA=6, ST=3, AG=3, PA=4, AV=10),
    )


async def _fake_find_advancement_perk(*_args, **_kwargs) -> Perk:
    return Perk.model_construct(
        id="elite-skill",
        name={"es": "Habilidad elite"},
        family="general",
        kind="skill",
        elite=True,
    )


async def _fake_find_standard_perk(*_args, **_kwargs) -> Perk:
    return Perk.model_construct(
        id="normal-skill",
        name={"es": "Habilidad normal"},
        family="general",
        kind="skill",
        elite=False,
    )


@pytest.mark.anyio
async def test_apply_skill_advancement_adds_elite_bonus(monkeypatch):
    monkeypatch.setattr(
        UserTeamService,
        "_find_advancement_perk",
        _fake_find_advancement_perk,
    )

    value_increase = await UserTeamService._apply_skill_advancement(
        _user_player(),
        _base_player(),
        ApplyPlayerAdvancementRequest(
            advancement_type="choose_primary_skill",
            perk_id="elite-skill",
        ),
        _advancement_rules(),
    )

    assert value_increase == 30_000


@pytest.mark.anyio
async def test_apply_skill_advancement_keeps_standard_value_for_non_elite(monkeypatch):
    monkeypatch.setattr(
        UserTeamService,
        "_find_advancement_perk",
        _fake_find_standard_perk,
    )

    value_increase = await UserTeamService._apply_skill_advancement(
        _user_player(),
        _base_player(),
        ApplyPlayerAdvancementRequest(
            advancement_type="choose_primary_skill",
            perk_id="normal-skill",
        ),
        _advancement_rules(),
    )

    assert value_increase == 20_000
