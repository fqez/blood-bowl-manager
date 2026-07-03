import pytest

from exceptions.exceptions import InvalidOperationException
from models.base.advancement import (
    AdvancementCostRow,
    AdvancementRules,
    AdvancementValueIncrease,
)
from models.base.roster import BasePlayer, BaseRoster, BaseStats
from models.league.league import League, LeagueTeam
from models.team.perk import Perk
from models.user_team.team import PlayerStats, UserPlayer, UserTeam
from schemas.user_team import (
    ApplyPlayerAdvancementRequest,
    HirePlayerRequest,
    UpdateTeamRequest,
)
from services.user_team_service import UserTeamService


@pytest.mark.anyio
async def test_commissioner_can_read_team_detail_in_league_context(monkeypatch):
    team = UserTeam.model_construct(
        id="team-1",
        user_id="coach-1",
        base_roster_id="human",
        name="The Smashers",
        players=[],
    )
    league = League.model_construct(
        id="league-1",
        name="Liga",
        owner_id="owner-1",
        commissioner_ids=["commissioner"],
        teams=[
            LeagueTeam(
                team_id="team-1",
                team_name="The Smashers",
                user_id="coach-1",
                username="Coach",
                base_roster_id="human",
            )
        ],
    )

    async def fake_get_team(team_id):
        assert team_id == "team-1"
        return team

    async def fake_get_league(league_id):
        assert league_id == "league-1"
        return league

    async def fake_to_detail(current_team, *, hide_notes=False):
        assert current_team is team
        assert hide_notes is False
        return {"id": current_team.id, "name": current_team.name}

    monkeypatch.setattr(UserTeam, "get", fake_get_team)
    monkeypatch.setattr(League, "get", fake_get_league)
    monkeypatch.setattr(UserTeamService, "_team_to_detail", fake_to_detail)

    detail = await UserTeamService.get_team_detail(
        "team-1",
        viewer_id="commissioner",
        league_id="league-1",
    )

    assert detail == {"id": "team-1", "name": "The Smashers"}


@pytest.mark.anyio
async def test_commissioner_edit_sets_exact_values_without_cost_adjustments(
    monkeypatch,
):
    team = UserTeam.model_construct(
        id="team-1",
        user_id="coach-1",
        base_roster_id="human",
        name="The Smashers",
        treasury=50000,
        rerolls=1,
        cheerleaders=0,
        assistant_coaches=0,
        apothecary=False,
        fan_factor=1,
        dedicated_fans=1,
        players=[],
    )
    league = League.model_construct(
        id="league-1",
        name="Liga",
        owner_id="owner-1",
        commissioner_ids=["commissioner"],
        teams=[
            LeagueTeam(
                team_id="team-1",
                team_name="The Smashers",
                user_id="coach-1",
                username="Coach",
                base_roster_id="human",
            )
        ],
    )
    roster = BaseRoster.model_construct(
        id="human",
        name="Human",
        reroll_cost=50000,
        apothecary_allowed=True,
        tier=1,
        players=[],
    )

    async def fake_get_team(team_id):
        assert team_id == "team-1"
        return team

    async def fake_get_league(league_id):
        assert league_id == "league-1"
        return league

    async def fake_find_roster(*_args, **_kwargs):
        return roster

    async def fake_team_value(*_args, **_kwargs):
        return 123456

    async def fake_is_in_league(*_args, **_kwargs):
        return True

    async def fake_save():
        return None

    monkeypatch.setattr(UserTeam, "get", fake_get_team)
    monkeypatch.setattr(League, "get", fake_get_league)
    monkeypatch.setattr(BaseRoster, "id", "id", raising=False)
    monkeypatch.setattr(BaseRoster, "find_one", fake_find_roster)
    monkeypatch.setattr(UserTeamService, "_is_in_league", fake_is_in_league)
    monkeypatch.setattr(UserTeamService, "_calculate_team_value", fake_team_value)
    object.__setattr__(team, "save", fake_save)

    updated = await UserTeamService.update_team(
        "team-1",
        "commissioner",
        UpdateTeamRequest(
            league_id="league-1",
            commissioner_edit=True,
            treasury=120000,
            rerolls=4,
            fan_factor=3,
            dedicated_fans=5,
            cheerleaders=2,
            assistant_coaches=1,
            apothecary=True,
        ),
    )

    assert updated.treasury == 120000
    assert updated.rerolls == 4
    assert updated.fan_factor == 3
    assert updated.dedicated_fans == 5
    assert updated.cheerleaders == 2
    assert updated.assistant_coaches == 1
    assert updated.apothecary is True
    assert updated.team_value == 123456


@pytest.mark.anyio
async def test_commissioner_can_fire_player_in_league_context(monkeypatch):
    player = type("Player", (), {"id": "player-1", "name": "Lineman"})()
    team = UserTeam.model_construct(
        id="team-1",
        user_id="coach-1",
        base_roster_id="human",
        name="The Smashers",
        players=[player],
    )
    league = League.model_construct(
        id="league-1",
        name="Liga",
        owner_id="owner-1",
        commissioner_ids=["commissioner"],
        teams=[
            LeagueTeam(
                team_id="team-1",
                team_name="The Smashers",
                user_id="coach-1",
                username="Coach",
                base_roster_id="human",
            )
        ],
    )

    async def fake_get_team(team_id):
        assert team_id == "team-1"
        return team

    async def fake_get_league(league_id):
        assert league_id == "league-1"
        return league

    async def fake_team_value(*_args, **_kwargs):
        return 90000

    async def fake_save():
        return None

    monkeypatch.setattr(UserTeam, "get", fake_get_team)
    monkeypatch.setattr(League, "get", fake_get_league)
    monkeypatch.setattr(UserTeamService, "_calculate_team_value", fake_team_value)
    object.__setattr__(team, "save", fake_save)

    updated = await UserTeamService.fire_player(
        "team-1",
        "commissioner",
        "player-1",
        league_id="league-1",
    )

    assert updated.players == []
    assert updated.team_value == 90000


@pytest.mark.anyio
async def test_commissioner_edit_requires_league_context():
    with pytest.raises(InvalidOperationException):
        await UserTeamService.update_team(
            "team-1",
            "commissioner",
            UpdateTeamRequest(commissioner_edit=True, treasury=100000),
        )


@pytest.mark.anyio
async def test_commissioner_can_hire_player_in_league_context(monkeypatch):
    team = UserTeam.model_construct(
        id="team-1",
        user_id="coach-1",
        base_roster_id="human",
        name="The Smashers",
        treasury=120000,
        players=[],
    )
    league = League.model_construct(
        id="league-1",
        name="Liga",
        owner_id="owner-1",
        commissioner_ids=["commissioner"],
        teams=[
            LeagueTeam(
                team_id="team-1",
                team_name="The Smashers",
                user_id="coach-1",
                username="Coach",
                base_roster_id="human",
            )
        ],
    )
    roster = BaseRoster.model_construct(
        id="human",
        name="Human",
        reroll_cost=50000,
        apothecary_allowed=True,
        tier=1,
        players=[
            BasePlayer(
                type="lineman",
                name="Lineman",
                position="Lineman",
                max=12,
                cost=50000,
                stats=BaseStats(MA=6, ST=3, AG=3, PA=4, AV=9),
                primary_access=["G"],
                secondary_access=["A"],
            )
        ],
    )

    async def fake_get_team(team_id):
        assert team_id == "team-1"
        return team

    async def fake_get_league(league_id):
        assert league_id == "league-1"
        return league

    async def fake_find_roster(*_args, **_kwargs):
        return roster

    async def fake_team_value(*_args, **_kwargs):
        return 105000

    async def fake_save():
        return None

    monkeypatch.setattr(UserTeam, "get", fake_get_team)
    monkeypatch.setattr(League, "get", fake_get_league)
    monkeypatch.setattr(BaseRoster, "id", "id", raising=False)
    monkeypatch.setattr(BaseRoster, "find_one", fake_find_roster)
    monkeypatch.setattr(UserTeamService, "_calculate_team_value", fake_team_value)
    object.__setattr__(team, "save", fake_save)

    result = await UserTeamService.hire_player(
        "team-1",
        "commissioner",
        HirePlayerRequest(base_type="lineman", league_id="league-1"),
    )

    assert len(team.players) == 1
    assert team.players[0].base_type == "lineman"
    assert team.treasury == 70000
    assert team.team_value == 105000
    assert result.treasury_remaining == 70000


@pytest.mark.anyio
async def test_commissioner_can_apply_player_advancement_in_league_context(
    monkeypatch,
):
    player = UserPlayer(
        id="player-1",
        base_type="lineman",
        name="Lineman",
        number=1,
        current_value=50000,
        spp=6,
        stats=PlayerStats(MA=6, ST=3, AG=3, PA=4, AV=9),
    )
    team = UserTeam.model_construct(
        id="team-1",
        user_id="coach-1",
        base_roster_id="human",
        name="The Smashers",
        players=[player],
    )
    league = League.model_construct(
        id="league-1",
        name="Liga",
        owner_id="owner-1",
        commissioner_ids=["commissioner"],
        teams=[
            LeagueTeam(
                team_id="team-1",
                team_name="The Smashers",
                user_id="coach-1",
                username="Coach",
                base_roster_id="human",
            )
        ],
    )
    roster = BaseRoster.model_construct(
        id="human",
        name="Human",
        reroll_cost=50000,
        apothecary_allowed=True,
        tier=1,
        players=[
            BasePlayer(
                type="lineman",
                name="Lineman",
                position="Lineman",
                max=12,
                cost=50000,
                stats=BaseStats(MA=6, ST=3, AG=3, PA=4, AV=9),
                primary_access=["G"],
                secondary_access=["A"],
            )
        ],
    )
    rules = AdvancementRules.model_construct(
        id="advancement_rules",
        max_advancements=6,
        max_characteristic_improvements_per_stat=2,
        cost_table=[
            AdvancementCostRow(
                advancement_number=1,
                level_name={"es": "Primera", "en": "First"},
                random_primary_skill=3,
                choose_primary_skill=6,
                choose_secondary_skill=12,
                characteristic_improvement=18,
            )
        ],
        characteristic_table=[],
        value_increases=[
            AdvancementValueIncrease(
                advancement_type="primary_skill",
                value=20000,
            )
        ],
        skill_categories=[],
        random_primary_skill_table=[],
        random_skill_rolls=2,
        random_skill_dice="2D6",
        description={"es": "test", "en": "test"},
    )
    perk = Perk.model_construct(
        id="block",
        name={"es": "Placar", "en": "Block"},
        family="general",
        kind="skill",
        elite=False,
    )

    async def fake_get_team(team_id):
        assert team_id == "team-1"
        return team

    async def fake_get_league(league_id):
        assert league_id == "league-1"
        return league

    async def fake_find_roster(*_args, **_kwargs):
        return roster

    async def fake_get_rules(rule_id):
        assert rule_id == "advancement_rules"
        return rules

    async def fake_find_perk(*_args, **_kwargs):
        return perk

    async def fake_team_value(*_args, **_kwargs):
        return 120000

    async def fake_save():
        return None

    monkeypatch.setattr(UserTeam, "get", fake_get_team)
    monkeypatch.setattr(League, "get", fake_get_league)
    monkeypatch.setattr(BaseRoster, "id", "id", raising=False)
    monkeypatch.setattr(BaseRoster, "find_one", fake_find_roster)
    monkeypatch.setattr(AdvancementRules, "get", fake_get_rules)
    monkeypatch.setattr(UserTeamService, "_find_advancement_perk", fake_find_perk)
    monkeypatch.setattr(UserTeamService, "_calculate_team_value", fake_team_value)
    object.__setattr__(team, "save", fake_save)

    updated = await UserTeamService.apply_player_advancement(
        "team-1",
        "commissioner",
        "player-1",
        ApplyPlayerAdvancementRequest(
            advancement_type="choose_primary_skill",
            perk_id="block",
            league_id="league-1",
        ),
    )

    assert updated.players[0].spp == 0
    assert updated.players[0].advancements == 1
    assert updated.players[0].current_value == 70000
    assert any(perk.id == "block" for perk in updated.players[0].perks)
    assert updated.team_value == 120000


@pytest.mark.anyio
async def test_commissioner_coach_mode_charges_treasury_for_apothecary(monkeypatch):
    team = UserTeam.model_construct(
        id="team-1",
        user_id="coach-1",
        base_roster_id="human",
        name="The Smashers",
        treasury=120000,
        rerolls=1,
        cheerleaders=0,
        assistant_coaches=0,
        apothecary=False,
        fan_factor=1,
        dedicated_fans=1,
        players=[],
    )
    league = League.model_construct(
        id="league-1",
        name="Liga",
        owner_id="owner-1",
        commissioner_ids=["commissioner"],
        teams=[
            LeagueTeam(
                team_id="team-1",
                team_name="The Smashers",
                user_id="coach-1",
                username="Coach",
                base_roster_id="human",
            )
        ],
    )
    roster = BaseRoster.model_construct(
        id="human",
        name="Human",
        reroll_cost=50000,
        apothecary_allowed=True,
        tier=1,
        players=[],
    )

    async def fake_get_team(team_id):
        assert team_id == "team-1"
        return team

    async def fake_get_league(league_id):
        assert league_id == "league-1"
        return league

    async def fake_find_roster(*_args, **_kwargs):
        return roster

    async def fake_team_value(*_args, **_kwargs):
        return 123456

    async def fake_is_in_league(*_args, **_kwargs):
        return True

    async def fake_save():
        return None

    monkeypatch.setattr(UserTeam, "get", fake_get_team)
    monkeypatch.setattr(League, "get", fake_get_league)
    monkeypatch.setattr(BaseRoster, "id", "id", raising=False)
    monkeypatch.setattr(BaseRoster, "find_one", fake_find_roster)
    monkeypatch.setattr(UserTeamService, "_is_in_league", fake_is_in_league)
    monkeypatch.setattr(UserTeamService, "_calculate_team_value", fake_team_value)
    object.__setattr__(team, "save", fake_save)

    updated = await UserTeamService.update_team(
        "team-1",
        "commissioner",
        UpdateTeamRequest(
            league_id="league-1",
            apothecary=True,
        ),
    )

    assert updated.apothecary is True
    assert updated.treasury == 70000
    assert updated.team_value == 123456


@pytest.mark.anyio
async def test_commissioner_cannot_spend_reserved_inducement_treasury_on_staff(
    monkeypatch,
):
    team = UserTeam.model_construct(
        id="team-1",
        user_id="coach-1",
        base_roster_id="human",
        name="The Smashers",
        treasury=50000,
        rerolls=1,
        cheerleaders=0,
        assistant_coaches=0,
        apothecary=False,
        fan_factor=1,
        dedicated_fans=1,
        players=[],
    )
    league = League.model_construct(
        id="league-1",
        name="Liga",
        owner_id="owner-1",
        commissioner_ids=["commissioner"],
        teams=[
            LeagueTeam(
                team_id="team-1",
                team_name="The Smashers",
                user_id="coach-1",
                username="Coach",
                base_roster_id="human",
            )
        ],
    )
    roster = BaseRoster.model_construct(
        id="human",
        name="Human",
        reroll_cost=50000,
        apothecary_allowed=True,
        tier=1,
        players=[],
    )

    async def fake_get_team(team_id):
        assert team_id == "team-1"
        return team

    async def fake_get_league(league_id):
        assert league_id == "league-1"
        return league

    async def fake_find_roster(*_args, **_kwargs):
        return roster

    async def fake_reserved(*_args, **_kwargs):
        return 40_000

    async def fake_is_in_league(*_args, **_kwargs):
        return True

    monkeypatch.setattr(UserTeam, "get", fake_get_team)
    monkeypatch.setattr(League, "get", fake_get_league)
    monkeypatch.setattr(BaseRoster, "id", "id", raising=False)
    monkeypatch.setattr(BaseRoster, "find_one", fake_find_roster)
    monkeypatch.setattr(UserTeamService, "_is_in_league", fake_is_in_league)
    monkeypatch.setattr(
        UserTeamService,
        "_pending_match_treasury_reservation",
        fake_reserved,
    )

    with pytest.raises(InvalidOperationException, match="Not enough treasury"):
        await UserTeamService.update_team(
            "team-1",
            "commissioner",
            UpdateTeamRequest(
                league_id="league-1",
                apothecary=True,
            ),
        )


@pytest.mark.anyio
async def test_commissioner_cannot_spend_reserved_inducement_treasury_on_hire(
    monkeypatch,
):
    team = UserTeam.model_construct(
        id="team-1",
        user_id="coach-1",
        base_roster_id="human",
        name="The Smashers",
        treasury=50000,
        players=[],
    )
    league = League.model_construct(
        id="league-1",
        name="Liga",
        owner_id="owner-1",
        commissioner_ids=["commissioner"],
        teams=[
            LeagueTeam(
                team_id="team-1",
                team_name="The Smashers",
                user_id="coach-1",
                username="Coach",
                base_roster_id="human",
            )
        ],
    )
    roster = BaseRoster.model_construct(
        id="human",
        name="Human",
        reroll_cost=50000,
        apothecary_allowed=True,
        tier=1,
        players=[
            BasePlayer(
                type="lineman",
                name="Lineman",
                position="Lineman",
                max=12,
                cost=40_000,
                stats=BaseStats(MA=6, ST=3, AG=3, PA=4, AV=9),
                primary_access=["G"],
                secondary_access=["A"],
            )
        ],
    )

    async def fake_get_team(team_id):
        assert team_id == "team-1"
        return team

    async def fake_get_league(league_id):
        assert league_id == "league-1"
        return league

    async def fake_find_roster(*_args, **_kwargs):
        return roster

    async def fake_reserved(*_args, **_kwargs):
        return 40_000

    monkeypatch.setattr(UserTeam, "get", fake_get_team)
    monkeypatch.setattr(League, "get", fake_get_league)
    monkeypatch.setattr(BaseRoster, "id", "id", raising=False)
    monkeypatch.setattr(BaseRoster, "find_one", fake_find_roster)
    monkeypatch.setattr(
        UserTeamService,
        "_pending_match_treasury_reservation",
        fake_reserved,
    )

    with pytest.raises(
        InvalidOperationException,
        match=r"Insufficient treasury \(10000 < 40000\)",
    ):
        await UserTeamService.hire_player(
            "team-1",
            "commissioner",
            HirePlayerRequest(base_type="lineman", league_id="league-1"),
        )
