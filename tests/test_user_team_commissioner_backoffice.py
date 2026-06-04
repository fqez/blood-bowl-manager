import pytest

from exceptions.exceptions import InvalidOperationException
from models.base.roster import BaseRoster
from models.league.league import League, LeagueTeam
from models.user_team.team import UserTeam
from schemas.user_team import UpdateTeamRequest
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

    async def fake_save():
        return None

    monkeypatch.setattr(UserTeam, "get", fake_get_team)
    monkeypatch.setattr(League, "get", fake_get_league)
    monkeypatch.setattr(BaseRoster, "id", "id", raising=False)
    monkeypatch.setattr(BaseRoster, "find_one", fake_find_roster)
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
