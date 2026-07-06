"""Characterization tests for legacy league aftermatch behavior."""

from types import SimpleNamespace

import pytest

from exceptions.exceptions import InvalidOperationException
from models.base.expensive_mistake import (
    ExpensiveMistakeBand,
    ExpensiveMistakeEffect,
    ExpensiveMistakesRules,
    LocalizedText,
)
from models.base.injury import CasualtyTableEntry, InjuryRules
from models.base.roster import BasePlayer, BaseRoster, BaseStats
from models.base.spp import SppEventReward, SppRewardsRules, ThrowTeammateReward
from models.base.winnings import WinningsRules
from models.league.league import League, Match, MatchStatus, MatchTeamInfo
from models.user_team.team import PlayerStats, UserPlayer, UserTeam
from schemas.league import (
    AftermatchExpensiveMistakesRequest,
    AftermatchPlayerPurchaseRequest,
    AftermatchTeamPurchasesRequest,
    AftermatchTemporaryPlayerDecision,
    AftermatchWinningsRequest,
    ApplyAftermatchSppRequest,
    MatchEventRequest,
)
from services import league_service
from services.league_service import LeagueService
from services.user_team_service import (
    UserTeamService,
    _TemporaryMatchTreasurySettlement,
)


def _text(value: str) -> LocalizedText:
    return LocalizedText(en=value, es=value)


def _spp_rules() -> SppRewardsRules:
    return SppRewardsRules.model_construct(
        id="spp_rewards",
        event_rewards=[
            SppEventReward(
                event_type="completion",
                spp=1,
                career_stat="completions",
                description=_text("completion"),
            ),
            SppEventReward(
                event_type="touchdown",
                spp=3,
                career_stat="touchdowns",
                description=_text("touchdown"),
            ),
            SppEventReward(
                event_type="casualty",
                spp=2,
                career_stat="casualties",
                description=_text("casualty"),
            ),
            SppEventReward(
                event_type="interception",
                spp=2,
                career_stat="interceptions",
                description=_text("interception"),
            ),
        ],
        mvp_spp=4,
        throw_teammate=ThrowTeammateReward(description=_text("throw teammate")),
    )


def _injury_rules() -> InjuryRules:
    return InjuryRules.model_construct(
        id="injury_rules",
        injury_table=[],
        stunty_injury_table=[],
        casualty_table=[
            CasualtyTableEntry(
                min_roll=1,
                max_roll=16,
                code="badly_hurt",
                label=_text("Badly Hurt"),
                description=_text("Badly Hurt"),
                player_status="badly_hurt",
                injury_codes=[],
                requires_lasting_injury_roll=False,
            )
        ],
        lasting_injury_table=[],
    )


def _winnings_rules() -> WinningsRules:
    return WinningsRules.model_construct(
        id="winnings",
        fan_attendance_divisor=2,
        no_stalling_bonus=1,
        gold_multiplier=10_000,
        description=_text("winnings"),
    )


def _expensive_mistakes_rules() -> ExpensiveMistakesRules:
    return ExpensiveMistakesRules.model_construct(
        id="expensive_mistakes",
        min_treasury=100_000,
        bands=[
            ExpensiveMistakeBand(
                min_treasury=100_000,
                max_treasury=None,
                results=["minor_incident"] * 6,
            )
        ],
        effects=[
            ExpensiveMistakeEffect(
                code="minor_incident",
                label=_text("Minor Incident"),
                description=_text("Lose D3 x 10,000"),
                calculation="lose_d3_x_10000",
                required_dice=["d3"],
            )
        ],
    )


def _base_roster() -> BaseRoster:
    return BaseRoster.model_construct(
        id="human",
        name="Human",
        reroll_cost=50_000,
        apothecary_allowed=True,
        tier=1,
        players=[
            BasePlayer(
                type="lineman",
                name="Lineman",
                position="Lineman",
                max=16,
                cost=50_000,
                stats=BaseStats(MA=6, ST=3, AG=3, PA=4, AV=9),
            )
        ],
    )


def _player(
    player_id: str,
    number: int,
    *,
    base_type: str = "lineman",
    current_value: int = 50_000,
    temporary: bool = False,
    match_id: str | None = None,
) -> UserPlayer:
    return UserPlayer(
        id=player_id,
        base_type=base_type,
        name=f"Player {number}",
        number=number,
        current_value=current_value,
        stats=PlayerStats(MA=6, ST=3, AG=3, PA=4, AV=9),
        temporary_for_match=temporary,
        temporary_match_id=match_id,
        journeyman=temporary,
    )


def _aftermatch_fixture():
    match = Match(
        id="match-1",
        round=1,
        status=MatchStatus.COMPLETED,
        score_home=1,
        score_away=0,
        home=MatchTeamInfo(
            team_id="home-team",
            team_name="Home",
            user_id="home-user",
            username="Home Coach",
            base_roster_id="human",
        ),
        away=MatchTeamInfo(
            team_id="away-team",
            team_name="Away",
            user_id="away-user",
            username="Away Coach",
            base_roster_id="human",
        ),
        home_squad=["home-1", "home-2", "home-star"],
        away_squad=["away-1", "away-2"],
    )
    league = League.model_construct(
        name="League",
        owner_id="commissioner",
        status="active",
        matches=[match],
    )
    home = UserTeam.model_construct(
        user_id="home-user",
        base_roster_id="human",
        name="Home",
        treasury=0,
        dedicated_fans=1,
        players=[
            _player("home-1", 1),
            _player("home-2", 2),
            _player("home-star", 16, base_type="star_griff", current_value=280_000),
        ],
    )
    away = UserTeam.model_construct(
        user_id="away-user",
        base_roster_id="human",
        name="Away",
        treasury=0,
        dedicated_fans=1,
        players=[_player("away-1", 3), _player("away-2", 4)],
    )
    return SimpleNamespace(
        league=league,
        match=match,
        home=home,
        away=away,
        roster=_base_roster(),
    )


def _find_player(team: UserTeam, player_id: str) -> UserPlayer:
    return next(player for player in team.players if player.id == player_id)


def _patch_aftermatch_environment(monkeypatch, fixture) -> None:
    async def fake_get_league_and_match(league_id: str, match_id: str):
        assert league_id == "league-1"
        assert match_id == fixture.match.id
        return fixture.league, fixture.match

    async def fake_get_team(team_id: str):
        return {"home-team": fixture.home, "away-team": fixture.away}.get(team_id)

    async def fake_find_roster(_query):
        return fixture.roster

    class FakeBaseRoster:
        id = "id"
        find_one = staticmethod(fake_find_roster)

    async def fake_user_get(user_id: str):
        return SimpleNamespace(username=f"user-{user_id}")

    async def fake_save(self):
        return self

    async def fake_get_match_detail(league_id: str, match_id: str):
        return SimpleNamespace(id=match_id)

    async def fake_spp_get(rule_id: str):
        assert rule_id == "spp_rewards"
        return _spp_rules()

    async def fake_injury_get(rule_id: str):
        assert rule_id == "injury_rules"
        return _injury_rules()

    async def fake_winnings_get(rule_id: str):
        assert rule_id == "winnings"
        return _winnings_rules()

    async def fake_expensive_get(rule_id: str):
        assert rule_id == "expensive_mistakes"
        return _expensive_mistakes_rules()

    async def fake_treasury_settlement(*args, **kwargs):
        return _TemporaryMatchTreasurySettlement(
            expected_contribution=0,
            charged_contribution=0,
            shortfall=0,
            legacy_live_charge=0,
        )

    monkeypatch.setattr(
        LeagueService,
        "_get_league_and_match",
        staticmethod(fake_get_league_and_match),
    )
    monkeypatch.setattr(league_service.UserTeam, "get", staticmethod(fake_get_team))
    monkeypatch.setattr(league_service, "BaseRoster", FakeBaseRoster)
    monkeypatch.setattr(league_service.User, "get", staticmethod(fake_user_get))
    monkeypatch.setattr(UserTeam, "save", fake_save)
    monkeypatch.setattr(League, "save", fake_save)
    monkeypatch.setattr(
        LeagueService,
        "get_match_detail",
        staticmethod(fake_get_match_detail),
    )
    monkeypatch.setattr(
        league_service.SppRewardsRules, "get", staticmethod(fake_spp_get)
    )
    monkeypatch.setattr(
        league_service.InjuryRules, "get", staticmethod(fake_injury_get)
    )
    monkeypatch.setattr(
        league_service.WinningsRules, "get", staticmethod(fake_winnings_get)
    )
    monkeypatch.setattr(
        league_service.ExpensiveMistakesRules,
        "get",
        staticmethod(fake_expensive_get),
    )
    monkeypatch.setattr(
        UserTeamService,
        "_temporary_match_treasury_settlement",
        staticmethod(fake_treasury_settlement),
    )


@pytest.mark.anyio
async def test_aftermatch_requires_both_mvp_selections(monkeypatch):
    fixture = _aftermatch_fixture()
    _patch_aftermatch_environment(monkeypatch, fixture)

    with pytest.raises(InvalidOperationException, match="Both MVP selections"):
        await LeagueService.apply_aftermatch_spp(
            "league-1",
            "match-1",
            "commissioner",
            ApplyAftermatchSppRequest(mvp_home="home-1"),
        )


@pytest.mark.anyio
async def test_aftermatch_rejects_star_player_mvp(monkeypatch):
    fixture = _aftermatch_fixture()
    _patch_aftermatch_environment(monkeypatch, fixture)

    with pytest.raises(InvalidOperationException, match="Star Players cannot be MVP"):
        await LeagueService.apply_aftermatch_spp(
            "league-1",
            "match-1",
            "commissioner",
            ApplyAftermatchSppRequest(mvp_home="home-star", mvp_away="away-1"),
        )


@pytest.mark.anyio
async def test_aftermatch_awards_spp_for_main_events_and_mvp(monkeypatch):
    fixture = _aftermatch_fixture()
    _patch_aftermatch_environment(monkeypatch, fixture)

    await LeagueService.apply_aftermatch_spp(
        "league-1",
        "match-1",
        "commissioner",
        ApplyAftermatchSppRequest(
            mvp_home="home-1",
            mvp_away="away-1",
            post_match_events=[
                MatchEventRequest(type="completion", team="home", player_id="home-1"),
                MatchEventRequest(type="touchdown", team="home", player_id="home-1"),
                MatchEventRequest(type="casualty", team="home", player_id="home-1"),
                MatchEventRequest(type="interception", team="home", player_id="home-1"),
            ],
        ),
    )

    player = _find_player(fixture.home, "home-1")
    assert player.spp == 12
    assert player.career.completions == 1
    assert player.career.touchdowns == 1
    assert player.career.casualties == 1
    assert player.career.interceptions == 1
    assert player.career.mvp_awards == 1


@pytest.mark.anyio
async def test_aftermatch_does_not_award_event_spp_to_star_players(monkeypatch):
    fixture = _aftermatch_fixture()
    _patch_aftermatch_environment(monkeypatch, fixture)

    await LeagueService.apply_aftermatch_spp(
        "league-1",
        "match-1",
        "commissioner",
        ApplyAftermatchSppRequest(
            mvp_home="home-1",
            mvp_away="away-1",
            post_match_events=[
                MatchEventRequest(
                    type="touchdown",
                    team="home",
                    player_id="home-star",
                )
            ],
        ),
    )

    assert _find_player(fixture.home, "home-star").spp == 0
    assert _find_player(fixture.home, "home-1").spp == 4


@pytest.mark.anyio
async def test_aftermatch_ignores_accidental_and_self_inflicted_casualty_spp(
    monkeypatch,
):
    fixture = _aftermatch_fixture()
    _patch_aftermatch_environment(monkeypatch, fixture)

    await LeagueService.apply_aftermatch_spp(
        "league-1",
        "match-1",
        "commissioner",
        ApplyAftermatchSppRequest(
            mvp_home="home-1",
            mvp_away="away-1",
            post_match_events=[
                MatchEventRequest(
                    type="casualty",
                    team="home",
                    player_id="home-2",
                    detail="accidental: yes",
                ),
                MatchEventRequest(
                    type="casualty",
                    team="home",
                    player_id="home-2",
                    detail="BBM_SELF_INFLICTED:1",
                ),
            ],
        ),
    )

    assert _find_player(fixture.home, "home-2").spp == 0
    assert _find_player(fixture.home, "home-2").career.casualties == 0


@pytest.mark.anyio
async def test_aftermatch_finalizes_temporary_players_without_winnings(monkeypatch):
    fixture = _aftermatch_fixture()
    temporary = _player("home-temp", 5, temporary=True, match_id="match-1")
    fixture.home.players.append(temporary)
    fixture.home.treasury = 50_000
    fixture.match.home_squad.append("home-temp")
    _patch_aftermatch_environment(monkeypatch, fixture)

    await LeagueService.apply_aftermatch_spp(
        "league-1",
        "match-1",
        "commissioner",
        ApplyAftermatchSppRequest(
            mvp_home="home-1",
            mvp_away="away-1",
            temporary_players=[
                AftermatchTemporaryPlayerDecision(
                    team="home",
                    player_id="home-temp",
                    decision="keep",
                )
            ],
        ),
    )

    kept = _find_player(fixture.home, "home-temp")
    assert kept.temporary_for_match is False
    assert kept.temporary_match_id is None
    assert kept.journeyman is False
    assert fixture.home.treasury == 0
    assert [event.type for event in fixture.match.events].count(
        "temporary_player_keep"
    ) == 1


@pytest.mark.anyio
async def test_aftermatch_applies_winnings_purchases_before_expensive_mistakes(
    monkeypatch,
):
    fixture = _aftermatch_fixture()
    fixture.home.treasury = 150_000
    _patch_aftermatch_environment(monkeypatch, fixture)

    await LeagueService.apply_aftermatch_spp(
        "league-1",
        "match-1",
        "commissioner",
        ApplyAftermatchSppRequest(
            mvp_home="home-1",
            mvp_away="away-1",
            winnings=AftermatchWinningsRequest(
                home_touchdowns=1,
                away_touchdowns=0,
                home_purchases=AftermatchTeamPurchasesRequest(
                    players=[
                        AftermatchPlayerPurchaseRequest(
                            base_type="lineman",
                            name="New Lineman",
                            number=11,
                        )
                    ],
                    cheerleaders=1,
                ),
                home_expensive_mistakes=AftermatchExpensiveMistakesRequest(
                    roll=1,
                    d3=2,
                ),
            ),
        ),
    )

    assert fixture.home.treasury == 100_000
    assert fixture.home.cheerleaders == 1
    assert any(player.name == "New Lineman" for player in fixture.home.players)
    assert [event.type for event in fixture.match.events].count(
        "post_match_purchase"
    ) == 2
    winnings_event = next(
        event
        for event in fixture.match.events
        if event.type == "winnings" and event.team == "home"
    )
    assert "Winnings: 30000" in winnings_event.detail
    assert "treasury before Expensive Mistakes: 120000" in winnings_event.detail
    assert "result: minor_incident" in winnings_event.detail


@pytest.mark.skip(
    reason=(
        "Pending characterization: Masters of Undeath free Raise the Dead needs a "
        "dedicated fixture with undead roster special rules and casualty-death input."
    )
)
def test_aftermatch_masters_of_undeath_free_raise_dead_pending():
    pass
