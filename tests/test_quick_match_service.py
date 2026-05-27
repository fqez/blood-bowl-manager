"""Tests for quick match business rules."""

import pytest

from exceptions.exceptions import InvalidOperationException
from models.league.league import League, LeagueTeam
from models.user.user import User
from models.user_team.team import UserTeam
from services.quick_match_service import QuickMatchService


@pytest.mark.anyio
async def test_create_quick_match_rejects_teams_registered_in_leagues(client_test):
    home_user = await User(
        username="homecoach",
        email="homecoach@example.com",
        password_hash="secret",
    ).insert()
    away_user = await User(
        username="awaycoach",
        email="awaycoach@example.com",
        password_hash="secret",
    ).insert()
    home_team = await UserTeam(
        user_id=str(home_user.id),
        base_roster_id="human",
        name="Home Team",
    ).insert()
    away_team = await UserTeam(
        user_id=str(away_user.id),
        base_roster_id="orc",
        name="Away Team",
    ).insert()

    await League(
        name="League",
        owner_id=str(home_user.id),
        teams=[
            LeagueTeam(
                team_id=str(home_team.id),
                team_name=home_team.name,
                user_id=str(home_user.id),
                username=home_user.username,
                base_roster_id=home_team.base_roster_id,
            )
        ],
    ).insert()

    with pytest.raises(InvalidOperationException, match="registered in a league"):
        await QuickMatchService.create_quick_match(
            str(home_user.id), str(home_team.id), str(away_team.id)
        )
