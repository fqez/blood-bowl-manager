from datetime import datetime

import pytest

from models.league.league import League
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
