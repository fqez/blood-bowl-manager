from datetime import datetime

import pytest

from models.league.league import League, Match, MatchTeamInfo
from services import league_service
from services.league_service import LeagueService


class _LeagueFindResult:
    def __init__(self, leagues):
        self._leagues = leagues

    async def to_list(self):
        return self._leagues


@pytest.mark.anyio
async def test_get_leagues_by_user_includes_additional_commissioners(monkeypatch):
    league = League.model_construct(
        id="league-1",
        name="Liga",
        owner_id="owner-1",
        commissioner_ids=["commissioner-2"],
        status="draft",
        format="round_robin",
        max_teams=8,
        season=1,
        teams=[],
        created_at=datetime.utcnow(),
        invite_code="ABCD1234",
        matches=[],
    )

    captured_query = {}

    def fake_find(query):
        captured_query.update(query)
        return _LeagueFindResult([league])

    async def fake_get_user(user_id):
        return type("UserRef", (), {"username": f"user-{user_id}"})()

    monkeypatch.setattr(League, "find", fake_find)
    monkeypatch.setattr(league_service.User, "get", fake_get_user)

    results = await LeagueService.get_leagues_by_user("commissioner-2")

    assert {"commissioner_ids": "commissioner-2"} in captured_query["$or"]
    assert len(results) == 1
    assert results[0].is_owner is False
    assert results[0].is_commissioner is True
    assert "user-owner-1" in results[0].commissioner_usernames


@pytest.mark.anyio
async def test_get_match_detail_does_not_recover_mng_on_read(monkeypatch):
    match = Match(
        id="match-1",
        round=1,
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
            base_roster_id="orc",
        ),
    )
    league = League.model_construct(
        id="league-1",
        name="Liga",
        owner_id="owner-1",
        commissioner_ids=[],
        status="active",
        format="round_robin",
        max_teams=8,
        season=1,
        teams=[],
        created_at=datetime.utcnow(),
        invite_code="ABCD1234",
        matches=[match],
    )

    async def fake_get_league(league_id):
        assert league_id == "league-1"
        return league

    async def fail_recover_players(*args, **kwargs):
        raise AssertionError("match detail GET should not mutate team state")

    monkeypatch.setattr(league_service, "_get_league", fake_get_league)
    monkeypatch.setattr(
        LeagueService,
        "_recover_players_who_served_mng",
        fail_recover_players,
    )

    detail = await LeagueService.get_match_detail("league-1", "match-1")

    assert detail is not None
    assert detail.id == "match-1"
    assert detail.home.team_id == "home-team"
    assert detail.away.team_id == "away-team"
