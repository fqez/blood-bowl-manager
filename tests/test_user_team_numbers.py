from models.base.roster import BasePlayer, BaseStats
from models.user_team.team import PlayerStats, PlayerStatus, UserPlayer, UserTeam
from services.user_team_service import UserTeamService


def _player(
    player_id: str,
    number: int,
    *,
    status: str = PlayerStatus.HEALTHY.value,
) -> UserPlayer:
    return UserPlayer(
        id=player_id,
        base_type="lineman",
        name=f"Player {number}",
        number=number,
        current_value=50000,
        stats=PlayerStats(MA=6, ST=3, AG=3, PA=4, AV=9),
        status=status,
    )


def _base_player() -> BasePlayer:
    return BasePlayer(
        type="lineman",
        name="Lineman",
        position="Lineman",
        max=16,
        cost=50000,
        stats=BaseStats(MA=6, ST=3, AG=3, PA=4, AV=9),
    )


def test_next_available_number_ignores_dead_players():
    team = UserTeam.model_construct(
        user_id="coach",
        base_roster_id="human",
        name="Humans",
        players=[
            _player("dead-1", 1, status=PlayerStatus.DEAD.value),
            _player("alive-2", 2),
        ],
    )

    assert UserTeamService._next_available_number(team) == 1


def test_build_user_player_allows_reusing_dead_players_number():
    team = UserTeam.model_construct(
        user_id="coach",
        base_roster_id="human",
        name="Humans",
        players=[
            _player("dead-1", 1, status=PlayerStatus.DEAD.value),
            _player("alive-2", 2),
        ],
    )

    new_player = UserTeamService._build_user_player(
        team=team,
        base_player=_base_player(),
        base_type="lineman",
        name=None,
        number=1,
    )

    assert new_player.number == 1
