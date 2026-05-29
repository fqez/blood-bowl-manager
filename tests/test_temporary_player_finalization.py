"""Temporary player finalization rules."""

import pytest

from models.base.roster import BasePlayer, BaseRoster, BaseStats
from models.league.league import Match, MatchTeamInfo
from models.user_team.team import PlayerStats, UserPlayer, UserTeam
from services.league_service import LeagueService


def _base_roster() -> BaseRoster:
    return BaseRoster(
        id="human",
        name="Human",
        reroll_cost=50000,
        tier=1,
        players=[
            BasePlayer(
                type="lineman",
                name="Lineman",
                position="Lineman",
                max=16,
                cost=50000,
                stats=BaseStats(MA=6, ST=3, AG=3, PA=4, AV=9),
            )
        ],
    )


def _player(
    player_id: str,
    number: int,
    *,
    temporary: bool,
    temporary_match_id: str | None = None,
) -> UserPlayer:
    return UserPlayer(
        id=player_id,
        base_type="lineman",
        name=f"Player {number}",
        number=number,
        current_value=50000,
        stats=PlayerStats(MA=6, ST=3, AG=3, PA=4, AV=9),
        temporary_for_match=temporary,
        temporary_match_id=temporary_match_id,
        journeyman=temporary,
    )


@pytest.mark.anyio
async def test_finalize_temporary_players_sweeps_roster_and_keeps_only_keep_decisions(
    client_test,
):
    match = Match(
        id="match-1",
        round=1,
        home=MatchTeamInfo(
            team_id="home-team",
            team_name="Home",
            user_id="coach",
            username="Coach",
            base_roster_id="human",
        ),
        away=MatchTeamInfo(
            team_id="away-team",
            team_name="Away",
            user_id="coach-2",
            username="Coach 2",
            base_roster_id="human",
        ),
    )
    home = UserTeam(
        user_id="coach",
        base_roster_id="human",
        name="Home",
        treasury=100000,
        players=[
            _player("permanent", 1, temporary=False),
            _player("rookie-1", 2, temporary=True, temporary_match_id="old-id"),
            _player("rookie-2", 3, temporary=True, temporary_match_id="old-id"),
            _player("rookie-3", 4, temporary=True, temporary_match_id="old-id"),
        ],
    )
    away = UserTeam(
        user_id="coach-2",
        base_roster_id="human",
        name="Away",
        players=[],
    )

    LeagueService._finalize_temporary_players(
        match,
        {"home": home, "away": away},
        {"home": _base_roster(), "away": _base_roster()},
        {("home", "rookie-2"): "keep"},
        "coach",
        "Coach",
    )

    assert [player.id for player in home.players] == ["permanent", "rookie-2"]
    kept = home.players[1]
    assert kept.temporary_for_match is False
    assert kept.temporary_match_id is None
    assert kept.journeyman is False
    assert home.treasury == 50000
    assert [event.type for event in match.events].count("temporary_player_keep") == 1
    assert [event.type for event in match.events].count("temporary_player_release") == 2
