import pytest

from models.base.roster import BasePlayer, BaseRoster, BaseStats
from models.user_team.team import PlayerStats, PlayerStatus, UserPlayer, UserTeam
from services.user_team_service import (
    UserTeamService,
    _MatchInducementBudgetSnapshot,
    _TemporaryMatchTreasurySettlement,
)


def _player(
    player_id: str,
    number: int,
    value: int,
    status: str = "healthy",
    base_type: str = "lineman",
) -> UserPlayer:
    return UserPlayer(
        id=player_id,
        base_type=base_type,
        name=f"Player {number}",
        number=number,
        current_value=value,
        stats=PlayerStats(MA=6, ST=3, AG=3, PA=4, AV=9),
        status=status,
    )


def test_team_value_excludes_dead_players_from_base_value():
    team = UserTeam.model_construct(
        user_id="coach",
        base_roster_id="human",
        name="Humans",
        players=[
            _player("healthy", 1, 50000, PlayerStatus.HEALTHY.value),
            _player("mng", 2, 70000, PlayerStatus.MISSING_NEXT_GAME.value),
            _player("dead", 3, 90000, PlayerStatus.DEAD.value),
        ],
        rerolls=0,
        assistant_coaches=0,
        cheerleaders=0,
        apothecary=False,
    )

    breakdown = team.calculate_team_value_breakdown(reroll_cost=50000)

    assert breakdown.player_value == 120000
    assert breakdown.unavailable_player_value == 70000
    assert breakdown.team_value == 120000
    assert breakdown.current_team_value == 50000


def test_match_inducement_team_value_excludes_current_match_temporary_players():
    team = UserTeam.model_construct(
        user_id="coach",
        base_roster_id="human",
        name="Humans",
        players=[
            _player("lineman-1", 1, 50000, PlayerStatus.HEALTHY.value),
            _player("lineman-2", 2, 70000, PlayerStatus.HEALTHY.value),
            UserPlayer(
                id="star-1",
                base_type="star_griff",
                name="Griff",
                number=16,
                current_value=280000,
                stats=PlayerStats(MA=7, ST=4, AG=2, PA=3, AV=9),
                status=PlayerStatus.HEALTHY.value,
                temporary_for_match=True,
                temporary_match_id="match-1",
            ),
        ],
        rerolls=1,
        assistant_coaches=0,
        cheerleaders=0,
        apothecary=False,
    )
    roster = BaseRoster.model_construct(
        id="human",
        name="Humans",
        reroll_cost=50000,
        apothecary_allowed=True,
        tier=2,
        special_rules=[],
        players=[],
    )

    ctv = UserTeamService._match_inducement_team_value(team, roster, "match-1")

    assert ctv == 170000


@pytest.mark.anyio
async def test_temporary_match_treasury_contribution_uses_legacy_live_charge_credit(
    monkeypatch,
):
    team = UserTeam.model_construct(
        id="team-1",
        user_id="coach",
        base_roster_id="human",
        name="Humans",
        treasury=0,
        players=[
            UserPlayer(
                id="star-1",
                base_type="star_griff",
                name="Griff",
                number=16,
                current_value=40000,
                stats=PlayerStats(MA=7, ST=4, AG=2, PA=3, AV=9),
                status=PlayerStatus.HEALTHY.value,
                temporary_for_match=True,
                temporary_match_id="match-1",
            )
        ],
    )

    async def fake_budget(*_args, **_kwargs):
        return _MatchInducementBudgetSnapshot(
            petty_cash=0,
            treasury_allowance=40000,
            total_available=40000,
            spent=40000,
            treasury_contribution=40000,
            remaining=0,
            is_favorite=True,
            is_tied=False,
        )

    monkeypatch.setattr(
        UserTeamService,
        "_match_inducement_budget_for_team",
        fake_budget,
    )

    contribution = await UserTeamService._temporary_match_treasury_contribution(
        team,
        league_id="league-1",
        match_id="match-1",
    )

    assert contribution == 0


@pytest.mark.anyio
async def test_temporary_match_treasury_settlement_allows_shortfall_when_requested(
    monkeypatch,
):
    team = UserTeam.model_construct(
        id="team-1",
        user_id="coach",
        base_roster_id="human",
        name="Humans",
        treasury=0,
        players=[],
    )

    async def fake_budget(*_args, **_kwargs):
        return _MatchInducementBudgetSnapshot(
            petty_cash=0,
            treasury_allowance=40000,
            total_available=40000,
            spent=40000,
            treasury_contribution=40000,
            remaining=0,
            is_favorite=True,
            is_tied=False,
        )

    monkeypatch.setattr(
        UserTeamService,
        "_match_inducement_budget_for_team",
        fake_budget,
    )

    settlement = await UserTeamService._temporary_match_treasury_settlement(
        team,
        league_id="league-1",
        match_id="match-1",
        allow_shortfall=True,
    )

    assert settlement == _TemporaryMatchTreasurySettlement(
        expected_contribution=40000,
        charged_contribution=0,
        shortfall=40000,
        legacy_live_charge=0,
    )


@pytest.mark.anyio
async def test_temporary_match_treasury_settlement_returns_object_when_no_contribution(
    monkeypatch,
):
    team = UserTeam.model_construct(
        id="team-1",
        user_id="coach",
        base_roster_id="human",
        name="Humans",
        treasury=12345,
        players=[],
    )

    async def fake_budget(*_args, **_kwargs):
        return _MatchInducementBudgetSnapshot(
            petty_cash=0,
            treasury_allowance=0,
            total_available=0,
            spent=0,
            treasury_contribution=0,
            remaining=0,
            is_favorite=False,
            is_tied=True,
        )

    monkeypatch.setattr(
        UserTeamService,
        "_match_inducement_budget_for_team",
        fake_budget,
    )

    settlement = await UserTeamService._temporary_match_treasury_settlement(
        team,
        league_id="league-1",
        match_id="match-1",
        allow_shortfall=True,
    )

    assert settlement == _TemporaryMatchTreasurySettlement(
        expected_contribution=0,
        charged_contribution=0,
        shortfall=0,
        legacy_live_charge=0,
    )


@pytest.mark.anyio
async def test_temporary_match_treasury_contribution_still_raises_without_legacy_credit(
    monkeypatch,
):
    team = UserTeam.model_construct(
        id="team-1",
        user_id="coach",
        base_roster_id="human",
        name="Humans",
        treasury=0,
        players=[],
    )

    async def fake_budget(*_args, **_kwargs):
        return _MatchInducementBudgetSnapshot(
            petty_cash=0,
            treasury_allowance=40000,
            total_available=40000,
            spent=40000,
            treasury_contribution=40000,
            remaining=0,
            is_favorite=True,
            is_tied=False,
        )

    monkeypatch.setattr(
        UserTeamService,
        "_match_inducement_budget_for_team",
        fake_budget,
    )

    with pytest.raises(
        Exception,
        match=(
            r"Insufficient treasury "
            r"\[source=user_team_service\.temporary_match_treasury_contribution\] "
            r"\(0 < 40000; match_id=match-1; legacy_live_charge=0\)"
        ),
    ):
        await UserTeamService._temporary_match_treasury_contribution(
            team,
            league_id="league-1",
            match_id="match-1",
        )


@pytest.mark.anyio
async def test_team_value_excludes_low_cost_linemen_from_ve_and_vae():
    team = UserTeam.model_construct(
        user_id="coach",
        base_roster_id="goblins",
        name="Goblins",
        players=[
            _player("lineman-healthy", 1, 40000, PlayerStatus.HEALTHY.value),
            _player("lineman-mng", 2, 50000, PlayerStatus.MISSING_NEXT_GAME.value),
            _player(
                "blitzer",
                3,
                90000,
                PlayerStatus.HEALTHY.value,
                base_type="blitzer",
            ),
        ],
        rerolls=0,
        assistant_coaches=0,
        cheerleaders=0,
        apothecary=False,
    )
    roster = BaseRoster.model_construct(
        id="goblins",
        name="Goblins",
        reroll_cost=60000,
        apothecary_allowed=True,
        tier=3,
        special_rules=["Bribery and Corruption", "Low Cost Linemen"],
        players=[
            BasePlayer(
                type="lineman",
                name="Lineman",
                position="Lineman",
                max=16,
                cost=40000,
                stats=BaseStats(MA=6, ST=3, AG=3, PA=4, AV=9),
            ),
            BasePlayer(
                type="blitzer",
                name="Blitzer",
                position="Blitzer",
                max=2,
                cost=90000,
                stats=BaseStats(MA=6, ST=3, AG=3, PA=4, AV=9),
            ),
        ],
    )

    breakdown = await UserTeamService._calculate_team_value_breakdown(team, roster)

    assert breakdown.player_value == 90000
    assert breakdown.unavailable_player_value == 0
    assert breakdown.team_value == 90000
    assert breakdown.current_team_value == 90000
