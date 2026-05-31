"""Service for league operations."""

import logging
import uuid
from datetime import datetime
from itertools import combinations
from typing import Optional

from bson import ObjectId

from exceptions.exceptions import (
    InvalidOperationException,
    LeagueNotFoundException,
    TeamNotFoundException,
)
from models.base.dedicated_fans import DedicatedFansRules
from models.base.expensive_mistake import ExpensiveMistakesRules
from models.base.injury import InjuryRules
from models.base.roster import BaseRoster
from models.base.spp import SppRewardsRules
from models.base.winnings import WinningsRules
from models.league.league import (
    League,
    LeagueRules,
    LeagueStanding,
    LeagueStatus,
    LeagueTeam,
    Match,
    MatchEvent,
    MatchStatus,
    MatchTeamInfo,
)
from models.user.user import User
from models.user_team.team import PlayerInjuryRecord, PlayerStatus, UserTeam
from schemas.league import (
    AddMatchEventRequest,
    AftermatchTemporaryPlayerDecision,
    ApplyAftermatchSppRequest,
    CreateLeagueMatchRequest,
    CreateLeagueRequest,
    LeagueByCodePreview,
    LeagueDetail,
    LeagueRulesRequest,
    LeagueStandingResponse,
    LeagueSummary,
    LeagueTeamResponse,
    MatchDetail,
    MatchEventRequest,
    MatchEventResponse,
    MatchSummary,
    MatchTeamResponse,
    RecordMatchResultRequest,
    UpdateLeagueMatchRequest,
    UpdateLeagueRequest,
    UpdateMatchStateRequest,
)
from services.user_team_service import UserTeamService

logger = logging.getLogger(__name__)


async def _get_league(league_id: str) -> Optional[League]:
    """Helper to get league by ID, handling ObjectId conversion."""
    try:
        # Try as ObjectId first
        return await League.get(ObjectId(league_id))
    except Exception:
        return None


class LeagueService:
    """Service for managing leagues."""

    @staticmethod
    def _player_status_value(player) -> str:
        status = player.status
        return status.value if isinstance(status, PlayerStatus) else str(status)

    @staticmethod
    def _current_round(league: League) -> Optional[int]:
        if not league.matches:
            return None
        pending_rounds = [
            m.round for m in league.matches if m.status != MatchStatus.COMPLETED
        ]
        if pending_rounds:
            return min(pending_rounds)
        return max(m.round for m in league.matches)

    @staticmethod
    def _is_player_available_for_match(player) -> bool:
        return LeagueService._player_status_value(player) == PlayerStatus.HEALTHY.value

    @staticmethod
    def _player_by_id(team: UserTeam, player_id: str):
        return next((player for player in team.players if player.id == player_id), None)

    @staticmethod
    def _event_detail_has_flag(detail: Optional[str], flag: str) -> bool:
        normalized = (detail or "").lower().replace(" ", "")
        return f"{flag.lower()}=true" in normalized

    @staticmethod
    def _is_accidental_casualty_event(event_type: str, detail: Optional[str]) -> bool:
        return event_type == "casualty" and LeagueService._event_detail_has_flag(
            detail, "accidental"
        )

    @staticmethod
    def _validate_match_squad(team: UserTeam, squad: list[str], label: str) -> None:
        if len(squad) != len(set(squad)):
            raise InvalidOperationException(f"{label} squad contains duplicate players")

        for player_id in squad:
            player = LeagueService._player_by_id(team, player_id)
            if not player:
                raise InvalidOperationException(
                    f"Player '{player_id}' not found in {label} team"
                )
            if not LeagueService._is_player_available_for_match(player):
                raise InvalidOperationException(
                    f"Player '{player.name}' is not available for this match"
                )

    @staticmethod
    def _sanitize_match_squad(
        team: UserTeam, squad: list[str], match_id: str
    ) -> list[str]:
        clean: list[str] = []
        seen: set[str] = set()
        for player_id in squad:
            if player_id in seen:
                continue
            player = LeagueService._player_by_id(team, player_id)
            if not player:
                continue
            if not LeagueService._is_player_available_for_match(player):
                continue
            if player.temporary_for_match and player.temporary_match_id != match_id:
                continue
            seen.add(player_id)
            clean.append(player_id)
        for player in team.players:
            if player.id in seen:
                continue
            if not LeagueService._is_player_available_for_match(player):
                continue
            if player.temporary_for_match and player.temporary_match_id == match_id:
                seen.add(player.id)
                clean.append(player.id)
        return clean

    @staticmethod
    def _is_current_match_temporary_player(player, match_id: str) -> bool:
        return bool(
            player
            and player.temporary_for_match
            and player.temporary_match_id == match_id
        )

    @staticmethod
    def _temporary_player_decisions(
        match: Match, temporary_players: list[AftermatchTemporaryPlayerDecision]
    ) -> dict[tuple[str, str], str]:
        decisions: dict[tuple[str, str], str] = {}
        for event in match.events:
            if event.type != "temporary_player_decision" or not event.player_id:
                continue
            detail = (event.detail or "").lower()
            if "decision=keep" in detail:
                decisions[(event.team, event.player_id)] = "keep"
            elif "decision=release" in detail:
                decisions[(event.team, event.player_id)] = "release"
        for temp_request in temporary_players:
            decisions[(temp_request.team, temp_request.player_id)] = (
                temp_request.decision
            )
        return decisions

    @staticmethod
    def _finalize_temporary_players(
        match: Match,
        teams_by_side: dict[str, UserTeam],
        rosters_by_side: dict[str, BaseRoster],
        decisions: dict[tuple[str, str], str],
        user_id: str,
        username: str,
    ) -> None:
        def _release_temporary_player(team_side: str, player) -> None:
            match.events.append(
                MatchEvent(
                    id=str(uuid.uuid4()),
                    type="temporary_player_release",
                    team=team_side,
                    player_id=player.id,
                    player_name=player.name,
                    detail=f"Temporary player released: {player.name}",
                    half=0,
                    turn=0,
                    timestamp=datetime.utcnow(),
                    created_by=user_id,
                    created_by_name=username,
                )
            )

        def _base_player_has_loner(team_side: str, player) -> bool:
            roster = rosters_by_side[team_side]
            base_player = next(
                (p for p in roster.players if p.type == player.base_type), None
            )
            if not base_player:
                return False
            return any(
                UserTeamService._is_loner_perk(perk) for perk in base_player.perks
            )

        for team_side, team in teams_by_side.items():
            next_players = []
            for player in list(team.players):
                if not player.temporary_for_match:
                    next_players.append(player)
                    continue

                if decisions.get((team_side, player.id)) != "keep":
                    _release_temporary_player(team_side, player)
                    continue

                permanent_count = sum(
                    1
                    for team_player in next_players
                    if not team_player.temporary_for_match
                )
                if permanent_count >= 16:
                    raise InvalidOperationException(
                        f"Cannot keep '{player.name}': roster is full (max 16 players)"
                    )
                if team.treasury < player.current_value:
                    raise InvalidOperationException(
                        f"Cannot keep '{player.name}': insufficient treasury ({team.treasury} < {player.current_value})"
                    )

                team.treasury -= player.current_value
                player.temporary_for_match = False
                player.temporary_match_id = None
                if player.journeyman and not _base_player_has_loner(team_side, player):
                    player.perks = [
                        perk
                        for perk in player.perks
                        if not UserTeamService._is_journeyman_loner_perk(perk)
                    ]
                player.journeyman = False
                next_players.append(player)
                match.events.append(
                    MatchEvent(
                        id=str(uuid.uuid4()),
                        type="temporary_player_keep",
                        team=team_side,
                        player_id=player.id,
                        player_name=player.name,
                        detail=(
                            f"Temporary player kept: {player.name}; cost: {player.current_value}; "
                            f"treasury: {team.treasury}"
                        ),
                        half=0,
                        turn=0,
                        timestamp=datetime.utcnow(),
                        created_by=user_id,
                        created_by_name=username,
                    )
                )
            team.players = next_players

    @staticmethod
    def _validate_match_player_reference(
        team: UserTeam, player_id: str | None, field_name: str
    ) -> None:
        if not player_id:
            return
        player = LeagueService._player_by_id(team, player_id)
        if not player:
            raise InvalidOperationException(
                f"{field_name} player '{player_id}' not found"
            )
        if not LeagueService._is_player_available_for_match(player):
            raise InvalidOperationException(
                f"{field_name} player '{player.name}' is not available for this match"
            )

    @staticmethod
    async def _clear_match_sent_off_statuses(match: Match) -> None:
        for team_id, squad in (
            (match.home.team_id, set(match.home_squad)),
            (match.away.team_id, set(match.away_squad)),
        ):
            team = await UserTeam.get(team_id)
            if not team:
                continue
            changed = False
            for player in team.players:
                if squad and player.id not in squad:
                    continue
                if (
                    LeagueService._player_status_value(player)
                    == PlayerStatus.SENT_OFF.value
                ):
                    player.status = PlayerStatus.HEALTHY.value
                    changed = True
            if changed:
                team.updated_at = datetime.utcnow()
                await team.save()

    # ============== League CRUD ==============

    @staticmethod
    async def create_league(owner_id: str, request: CreateLeagueRequest) -> League:
        """Create a new league."""
        rules = LeagueRules()
        if request.rules:
            rules = LeagueRules(
                starting_budget=request.rules.starting_budget,
                resurrection=request.rules.resurrection,
                inducements=request.rules.inducements,
                spiraling_expenses=request.rules.spiraling_expenses,
                max_team_value=request.rules.max_team_value,
            )

        league = League(
            name=request.name,
            description=request.description,
            owner_id=owner_id,
            status=LeagueStatus.DRAFT,
            format=request.format,
            max_teams=request.max_teams,
            rules=rules,
        )

        await league.insert()
        logger.info(f"Created league '{league.name}' by user {owner_id}")

        return league

    @staticmethod
    async def get_league_by_id(league_id: str) -> Optional[League]:
        """Get a league by ID."""
        return await _get_league(league_id)

    @staticmethod
    async def get_all_leagues(status: Optional[str] = None) -> list[LeagueSummary]:
        """Get all leagues, optionally filtered by status."""
        query = {}
        if status:
            query["status"] = status

        leagues = await League.find(query).to_list()

        results = []
        for league in leagues:
            owner = None
            try:
                owner = await User.get(league.owner_id)
            except Exception:
                pass  # Invalid ObjectId or user not found
            results.append(
                LeagueSummary(
                    id=str(league.id),
                    name=league.name,
                    owner_username=owner.username if owner else "Unknown",
                    status=league.status,
                    format=league.format,
                    team_count=len(league.teams),
                    max_teams=league.max_teams,
                    season=league.season,
                    invite_code=league.invite_code,
                    created_at=league.created_at,
                )
            )

        return results

    @staticmethod
    async def get_leagues_by_user(user_id: str) -> list[LeagueSummary]:
        """Get leagues where user is the owner or has a team."""
        leagues = await League.find(
            {"$or": [{"owner_id": user_id}, {"teams.user_id": user_id}]}
        ).to_list()

        results = []
        for league in leagues:
            owner = None
            try:
                owner = await User.get(league.owner_id)
            except Exception:
                pass

            # Find user's team in this league
            user_team_name = None
            for team in league.teams:
                if team.user_id == user_id:
                    user_team_name = team.team_name
                    break

            # Check if user is the owner
            is_owner = league.owner_id == user_id

            results.append(
                LeagueSummary(
                    id=str(league.id),
                    name=league.name,
                    owner_username=owner.username if owner else "Unknown",
                    status=league.status,
                    format=league.format,
                    team_count=len(league.teams),
                    max_teams=league.max_teams,
                    season=league.season,
                    invite_code=league.invite_code,
                    created_at=league.created_at,
                    is_owner=is_owner,
                    user_team_name=user_team_name,
                    current_round=LeagueService._current_round(league),
                )
            )

        return results

    @staticmethod
    def _user_can_view_league(league: League, user_id: str) -> bool:
        """Check if user is the owner or has a team in the league."""
        if league.owner_id == user_id:
            return True
        return any(team.user_id == user_id for team in league.teams)

    @staticmethod
    async def get_league_detail(
        league_id: str, *, viewer_id: Optional[str] = None
    ) -> Optional[LeagueDetail]:
        """Get full league detail."""
        from bson import ObjectId

        # Try to convert to ObjectId if it's a valid MongoDB id
        try:
            league = await League.get(ObjectId(league_id))
        except Exception:
            # If not a valid ObjectId, try finding by custom id field
            league = (
                await League.find_one(League.id == league_id)
                if hasattr(League, "id")
                else None
            )

        if not league:
            return None

        if viewer_id is not None and not LeagueService._user_can_view_league(
            league, viewer_id
        ):
            raise InvalidOperationException("You do not have access to this league")

        owner = None
        try:
            owner = await User.get(league.owner_id)
        except Exception:
            pass

        teams = [
            LeagueTeamResponse(
                team_id=t.team_id,
                team_name=t.team_name,
                user_id=t.user_id,
                username=t.username,
                base_roster_id=t.base_roster_id,
                icon=t.icon,
                joined_at=t.joined_at,
            )
            for t in league.teams
        ]

        standings = [
            LeagueStandingResponse(
                team_id=s.team_id,
                team_name=s.team_name,
                wins=s.wins,
                draws=s.draws,
                losses=s.losses,
                points=s.points,
                touchdowns_for=s.touchdowns_for,
                touchdowns_against=s.touchdowns_against,
                touchdown_diff=s.touchdown_diff,
                casualties_for=s.casualties_for,
                casualties_against=s.casualties_against,
                games_played=s.games_played,
            )
            for s in league.get_sorted_standings()
        ]

        matches = [
            MatchSummary(
                id=m.id,
                round=m.round,
                home=MatchTeamResponse(
                    team_id=m.home.team_id,
                    team_name=m.home.team_name,
                    user_id=m.home.user_id,
                    username=m.home.username,
                    base_roster_id=m.home.base_roster_id,
                ),
                away=MatchTeamResponse(
                    team_id=m.away.team_id,
                    team_name=m.away.team_name,
                    user_id=m.away.user_id,
                    username=m.away.username,
                    base_roster_id=m.away.base_roster_id,
                ),
                status=m.status,
                score_home=m.score_home,
                score_away=m.score_away,
                weather=m.weather,
                kickoff_event=m.kickoff_event,
                current_half=m.current_half,
                current_turn=m.current_turn,
                current_team=m.current_team,
                home_turn=m.home_turn,
                away_turn=m.away_turn,
                turn_started_at=m.turn_started_at,
                home_turn_seconds=m.home_turn_seconds,
                away_turn_seconds=m.away_turn_seconds,
                started_at=m.started_at,
                scheduled_at=m.scheduled_at,
                played_at=m.played_at,
            )
            for m in league.matches
        ]

        return LeagueDetail(
            id=str(league.id),
            name=league.name,
            description=league.description,
            owner_id=league.owner_id,
            owner_username=owner.username if owner else "Unknown",
            invite_code=league.invite_code,
            status=league.status,
            season=league.season,
            current_round=LeagueService._current_round(league),
            format=league.format,
            max_teams=league.max_teams,
            rules=LeagueRulesRequest(
                starting_budget=league.rules.starting_budget,
                resurrection=league.rules.resurrection,
                inducements=league.rules.inducements,
                spiraling_expenses=league.rules.spiraling_expenses,
                max_team_value=league.rules.max_team_value,
            ),
            teams=teams,
            standings=standings,
            matches=matches,
            created_at=league.created_at,
            started_at=league.started_at,
            ended_at=league.ended_at,
        )

    # ============== Team Management ==============

    @staticmethod
    async def join_league(
        league_id: str, user_id: str, team_id: str, invite_code: str
    ) -> League:
        """Join a league with a team (invite code required)."""
        league = await _get_league(league_id)
        if not league:
            raise LeagueNotFoundException(league_id)

        if league.invite_code != invite_code.upper():
            raise InvalidOperationException("Código de invitación incorrecto")

        team = await UserTeam.get(team_id)
        if not team:
            raise TeamNotFoundException(team_id)

        if team.user_id != user_id:
            raise InvalidOperationException("Cannot join with another user's team")

        existing_league = await League.find_one({"teams.team_id": team_id})
        if existing_league and str(existing_league.id) != league_id:
            raise InvalidOperationException("Este equipo ya está inscrito en otra liga")

        can_join, reason = league.can_join(team_id, user_id)
        if not can_join:
            raise InvalidOperationException(reason)

        user = None
        try:
            user = await User.get(user_id)
        except Exception:
            pass

        league_team = LeagueTeam(
            team_id=team_id,
            team_name=team.name,
            user_id=user_id,
            username=user.username if user else "Unknown",
            base_roster_id=team.base_roster_id,
            icon=team.icon,
        )

        league.teams.append(league_team)

        # Add standing entry
        league.standings.append(LeagueStanding(team_id=team_id, team_name=team.name))

        await league.save()
        logger.info(f"Team {team_id} joined league {league_id}")

        return league

    @staticmethod
    async def leave_league(league_id: str, team_id: str, user_id: str) -> League:
        """Leave a league."""
        league = await _get_league(league_id)
        if not league:
            raise LeagueNotFoundException(league_id)

        if league.status != LeagueStatus.DRAFT:
            raise InvalidOperationException("Cannot leave a league that has started")

        # Find and remove team
        team_idx = None
        for i, t in enumerate(league.teams):
            if t.team_id == team_id:
                if t.user_id != user_id:
                    raise InvalidOperationException("Cannot remove another user's team")
                team_idx = i
                break

        if team_idx is None:
            raise InvalidOperationException("Team not in this league")

        league.teams.pop(team_idx)

        # Remove standing
        league.standings = [s for s in league.standings if s.team_id != team_id]

        await league.save()
        logger.info(f"Team {team_id} left league {league_id}")

        return league

    @staticmethod
    async def get_league_by_code(invite_code: str) -> Optional[LeagueByCodePreview]:
        """Look up a league by its invite code."""
        league = await League.find_one({"invite_code": invite_code.upper()})
        if not league:
            return None
        owner = None
        try:
            owner = await User.get(league.owner_id)
        except Exception:
            pass
        return LeagueByCodePreview(
            id=str(league.id),
            name=league.name,
            owner_username=owner.username if owner else "Unknown",
            status=league.status,
            format=league.format,
            team_count=len(league.teams),
            max_teams=league.max_teams,
            season=league.season,
            invite_code=league.invite_code,
        )

    @staticmethod
    async def update_league(
        league_id: str, owner_id: str, request: UpdateLeagueRequest
    ) -> League:
        """Update league settings (owner only)."""
        league = await _get_league(league_id)
        if not league:
            raise LeagueNotFoundException(league_id)
        if league.owner_id != owner_id:
            raise InvalidOperationException(
                "Solo el propietario puede modificar la liga"
            )
        if request.name is not None:
            league.name = request.name
        if request.description is not None:
            league.description = request.description
        if request.max_teams is not None:
            if request.max_teams < len(league.teams):
                raise InvalidOperationException(
                    "No se puede reducir el límite por debajo del número de equipos actuales"
                )
            league.max_teams = request.max_teams
        await league.save()
        logger.info(f"League {league_id} updated by owner {owner_id}")
        return league

    # ============== League Lifecycle ==============

    @staticmethod
    async def start_league(
        league_id: str, owner_id: str, *, schedule_mode: str = "automatic"
    ) -> League:
        """Start the league and generate fixtures."""
        league = await _get_league(league_id)
        if not league:
            raise LeagueNotFoundException(league_id)

        if league.owner_id != owner_id:
            raise InvalidOperationException("Only the owner can start the league")

        if league.status != LeagueStatus.DRAFT:
            raise InvalidOperationException("League has already started")

        if len(league.teams) < 2:
            raise InvalidOperationException("Need at least 2 teams to start")

        if schedule_mode == "manual":
            league.matches = []
        elif league.format == "round_robin":
            league.matches = LeagueService._generate_round_robin(league.teams)
        else:
            # Default to round robin for now
            league.matches = LeagueService._generate_round_robin(league.teams)

        league.status = LeagueStatus.ACTIVE
        league.started_at = datetime.utcnow()
        await league.save()

        logger.info(f"League {league_id} started with {len(league.matches)} matches")
        return league

    @staticmethod
    def _generate_round_robin(teams: list[LeagueTeam]) -> list[Match]:
        """Generate round-robin fixtures."""
        matches = []
        round_num = 1

        team_pairs = list(combinations(teams, 2))

        for t1, t2 in team_pairs:
            match = Match(
                id=uuid.uuid4().hex,
                round=round_num,
                home=MatchTeamInfo(
                    team_id=t1.team_id,
                    team_name=t1.team_name,
                    user_id=t1.user_id,
                    username=t1.username,
                    base_roster_id=t1.base_roster_id,
                ),
                away=MatchTeamInfo(
                    team_id=t2.team_id,
                    team_name=t2.team_name,
                    user_id=t2.user_id,
                    username=t2.username,
                    base_roster_id=t2.base_roster_id,
                ),
            )
            matches.append(match)

            # Simple round assignment (could be improved)
            if len(matches) % (len(teams) // 2) == 0:
                round_num += 1

        return matches

    @staticmethod
    def _league_team_by_id(league: League, team_id: str) -> LeagueTeam:
        for team in league.teams:
            if team.team_id == team_id:
                return team
        raise InvalidOperationException(f"Team '{team_id}' is not in this league")

    @staticmethod
    def _match_team_info(team: LeagueTeam) -> MatchTeamInfo:
        return MatchTeamInfo(
            team_id=team.team_id,
            team_name=team.team_name,
            user_id=team.user_id,
            username=team.username,
            base_roster_id=team.base_roster_id,
        )

    @staticmethod
    def _ensure_owner_can_edit_calendar(league: League, user_id: str) -> None:
        if league.owner_id != user_id:
            raise InvalidOperationException(
                "Solo el propietario puede editar el calendario"
            )
        if league.status != LeagueStatus.ACTIVE:
            raise InvalidOperationException(
                "El calendario solo se puede editar con la liga activa"
            )

    @staticmethod
    def _ensure_match_is_scheduled(match: Match) -> None:
        if match.status != MatchStatus.SCHEDULED:
            raise InvalidOperationException(
                "Solo se pueden editar encuentros pendientes"
            )

    @staticmethod
    async def create_league_match(
        league_id: str, user_id: str, request: CreateLeagueMatchRequest
    ) -> MatchDetail:
        league = await _get_league(league_id)
        if not league:
            raise LeagueNotFoundException(league_id)
        LeagueService._ensure_owner_can_edit_calendar(league, user_id)
        if request.home_team_id == request.away_team_id:
            raise InvalidOperationException("Un equipo no puede jugar contra si mismo")

        home = LeagueService._league_team_by_id(league, request.home_team_id)
        away = LeagueService._league_team_by_id(league, request.away_team_id)
        match = Match(
            id=uuid.uuid4().hex,
            round=request.round,
            home=LeagueService._match_team_info(home),
            away=LeagueService._match_team_info(away),
            scheduled_at=request.scheduled_at,
        )
        league.matches.append(match)
        await league.save()
        return await LeagueService.get_match_detail(league_id, match.id)

    @staticmethod
    async def update_league_match_fixture(
        league_id: str,
        match_id: str,
        user_id: str,
        request: UpdateLeagueMatchRequest,
    ) -> MatchDetail:
        league, match = await LeagueService._get_league_and_match(league_id, match_id)
        LeagueService._ensure_owner_can_edit_calendar(league, user_id)
        LeagueService._ensure_match_is_scheduled(match)

        next_home_id = request.home_team_id or match.home.team_id
        next_away_id = request.away_team_id or match.away.team_id
        if next_home_id == next_away_id:
            raise InvalidOperationException("Un equipo no puede jugar contra si mismo")

        if request.round is not None:
            match.round = request.round
        if request.home_team_id is not None:
            match.home = LeagueService._match_team_info(
                LeagueService._league_team_by_id(league, request.home_team_id)
            )
        if request.away_team_id is not None:
            match.away = LeagueService._match_team_info(
                LeagueService._league_team_by_id(league, request.away_team_id)
            )
        if "scheduled_at" in request.model_fields_set:
            match.scheduled_at = request.scheduled_at

        await league.save()
        return await LeagueService.get_match_detail(league_id, match_id)

    @staticmethod
    async def delete_league_match(league_id: str, match_id: str, user_id: str) -> None:
        league, match = await LeagueService._get_league_and_match(league_id, match_id)
        LeagueService._ensure_owner_can_edit_calendar(league, user_id)
        LeagueService._ensure_match_is_scheduled(match)
        league.matches = [m for m in league.matches if m.id != match_id]
        await league.save()

    # ============== Match Operations ==============

    @staticmethod
    async def record_match_result(
        league_id: str,
        match_id: str,
        user_id: str,
        request: RecordMatchResultRequest,
    ) -> League:
        """Record the result of a match."""
        league, match = await LeagueService._get_league_and_match(league_id, match_id)

        if not LeagueService._user_can_manage_match(league, match, user_id):
            raise InvalidOperationException(
                "Only match participants or the league owner can record the match result"
            )

        if league.status != LeagueStatus.ACTIVE:
            raise InvalidOperationException("League is not active")

        if not match:
            raise InvalidOperationException(f"Match {match_id} not found")

        if match.status == MatchStatus.COMPLETED:
            raise InvalidOperationException("Match already completed")

        # Update match
        match.score_home = request.score_home
        match.score_away = request.score_away
        match.weather = request.weather
        match.mvp_home = request.mvp_home_player_id
        match.mvp_away = request.mvp_away_player_id
        match.gate = request.gate
        match.status = MatchStatus.COMPLETED
        match.played_at = datetime.utcnow()

        # Add events
        for e in request.events:
            match.events.append(
                MatchEvent(
                    type=e.type,
                    team=e.team,
                    player_id=e.player_id,
                    player_name=e.player_name,
                    victim_id=e.victim_id,
                    victim_name=e.victim_name,
                    injury=e.injury,
                    detail=e.detail,
                    half=e.half,
                    turn=e.turn,
                )
            )

        # Update standings
        home_standing = league.get_team_standing(match.home.team_id)
        away_standing = league.get_team_standing(match.away.team_id)

        if home_standing and away_standing:
            # Update TDs
            home_standing.touchdowns_for += request.score_home
            home_standing.touchdowns_against += request.score_away
            away_standing.touchdowns_for += request.score_away
            away_standing.touchdowns_against += request.score_home

            # Update casualties
            home_cas = sum(
                1
                for e in request.events
                if e.type == "casualty"
                and e.team == "home"
                and not LeagueService._is_accidental_casualty_event(e.type, e.detail)
            )
            away_cas = sum(
                1
                for e in request.events
                if e.type == "casualty"
                and e.team == "away"
                and not LeagueService._is_accidental_casualty_event(e.type, e.detail)
            )
            home_standing.casualties_for += home_cas
            home_standing.casualties_against += away_cas
            away_standing.casualties_for += away_cas
            away_standing.casualties_against += home_cas

            # Update W/D/L
            if request.score_home > request.score_away:
                home_standing.wins += 1
                away_standing.losses += 1
            elif request.score_home < request.score_away:
                home_standing.losses += 1
                away_standing.wins += 1
            else:
                home_standing.draws += 1
                away_standing.draws += 1

        await LeagueService._clear_match_sent_off_statuses(match)
        await league.save()
        logger.info(
            f"Recorded result for match {match_id}: {request.score_home}-{request.score_away}"
        )

        return league

    @staticmethod
    async def get_match_detail(
        league_id: str, match_id: str, *, viewer_id: Optional[str] = None
    ) -> Optional[MatchDetail]:
        """Get full match detail."""
        league = await _get_league(league_id)
        if not league:
            return None

        if viewer_id is not None and not LeagueService._user_can_view_league(
            league, viewer_id
        ):
            raise InvalidOperationException("You do not have access to this match")

        for m in league.matches:
            if m.id == match_id:
                return MatchDetail(
                    id=m.id,
                    round=m.round,
                    home=MatchTeamResponse(
                        team_id=m.home.team_id,
                        team_name=m.home.team_name,
                        user_id=m.home.user_id,
                        username=m.home.username,
                        base_roster_id=m.home.base_roster_id,
                    ),
                    away=MatchTeamResponse(
                        team_id=m.away.team_id,
                        team_name=m.away.team_name,
                        user_id=m.away.user_id,
                        username=m.away.username,
                        base_roster_id=m.away.base_roster_id,
                    ),
                    status=m.status,
                    score_home=m.score_home,
                    score_away=m.score_away,
                    weather=m.weather,
                    kickoff_event=m.kickoff_event,
                    current_half=m.current_half,
                    current_turn=m.current_turn,
                    current_team=m.current_team,
                    home_turn=m.home_turn,
                    away_turn=m.away_turn,
                    turn_started_at=m.turn_started_at,
                    home_turn_seconds=m.home_turn_seconds,
                    away_turn_seconds=m.away_turn_seconds,
                    rerolls_used_home=m.rerolls_used_home,
                    rerolls_used_away=m.rerolls_used_away,
                    home_inducement_purchases=m.home_inducement_purchases,
                    away_inducement_purchases=m.away_inducement_purchases,
                    home_inducement_uses=m.home_inducement_uses,
                    away_inducement_uses=m.away_inducement_uses,
                    home_inducement_details=m.home_inducement_details,
                    away_inducement_details=m.away_inducement_details,
                    events=[
                        MatchEventResponse(
                            id=e.id,
                            type=e.type,
                            team=e.team,
                            player_id=e.player_id,
                            player_name=e.player_name,
                            victim_id=e.victim_id,
                            victim_name=e.victim_name,
                            injury=e.injury,
                            detail=e.detail,
                            half=e.half,
                            turn=e.turn,
                            timestamp=e.timestamp,
                            created_by=e.created_by,
                            created_by_name=e.created_by_name,
                        )
                        for e in m.events
                    ],
                    mvp_home=m.mvp_home,
                    mvp_away=m.mvp_away,
                    gate=m.gate,
                    aftermatch_spp_applied_at=m.aftermatch_spp_applied_at,
                    aftermatch_winnings_applied_at=m.aftermatch_winnings_applied_at,
                    started_at=m.started_at,
                    scheduled_at=m.scheduled_at,
                    played_at=m.played_at,
                    home_ready=m.home_ready,
                    away_ready=m.away_ready,
                    home_squad=m.home_squad,
                    away_squad=m.away_squad,
                )

        return None

    @staticmethod
    async def get_match_team_details(league_id: str, match_id: str, user_id: str):
        """Get both match team rosters for participants or the league owner."""
        league, match = await LeagueService._get_league_and_match(league_id, match_id)

        if not LeagueService._user_can_manage_match(league, match, user_id):
            raise InvalidOperationException(
                "Only match participants or the league owner can access match rosters"
            )

        home_detail = await UserTeamService.get_team_detail(
            match.home.team_id,
            hide_notes=True,
        )
        away_detail = await UserTeamService.get_team_detail(
            match.away.team_id,
            hide_notes=True,
        )

        if not home_detail:
            raise TeamNotFoundException(match.home.team_id)
        if not away_detail:
            raise TeamNotFoundException(match.away.team_id)

        return {
            "home": home_detail,
            "away": away_detail,
        }

    # ============== Delete Operations ==============

    @staticmethod
    async def delete_league(league_id: str, user_id: str) -> None:
        """Delete a league (owner only)."""
        league = await _get_league(league_id)
        if not league:
            raise LeagueNotFoundException(league_id)

        if league.owner_id != user_id:
            raise InvalidOperationException("Only the owner can delete the league")

        if league.status == LeagueStatus.ACTIVE:
            raise InvalidOperationException(
                "Cannot delete an active league. Complete or archive it first."
            )

        await league.delete()
        logger.info(f"League {league_id} deleted by user {user_id}")

    @staticmethod
    async def archive_league(league_id: str, user_id: str) -> None:
        """Mark a league as completed/archived (owner only)."""
        league = await _get_league(league_id)
        if not league:
            raise LeagueNotFoundException(league_id)

        if league.owner_id != user_id:
            raise InvalidOperationException(
                "Solo el propietario puede archivar la liga"
            )

        if league.status == LeagueStatus.DRAFT:
            raise InvalidOperationException(
                "No puedes archivar una liga que aún no ha empezado"
            )

        league.status = LeagueStatus.COMPLETED
        await league.save()
        logger.info(f"League {league_id} archived by user {user_id}")

    # ============== Live Match Operations ==============

    @staticmethod
    async def _get_league_and_match(league_id: str, match_id: str):
        """Helper to fetch league and find match by id."""
        league = await _get_league(league_id)
        if not league:
            raise LeagueNotFoundException(league_id)
        match = None
        for m in league.matches:
            if m.id == match_id:
                match = m
                break
        if not match:
            raise InvalidOperationException(f"Match {match_id} not found")
        return league, match

    @staticmethod
    def _user_can_manage_match(league: League, match: Match, user_id: str) -> bool:
        """Check if user is owner, home, or away player."""
        if league.owner_id == user_id:
            return True
        if match.home.user_id == user_id or match.away.user_id == user_id:
            return True
        return False

    @staticmethod
    async def start_match(league_id: str, match_id: str, user_id: str) -> League:
        """Start a match (either contestant or owner)."""
        league, match = await LeagueService._get_league_and_match(league_id, match_id)

        if league.status != LeagueStatus.ACTIVE:
            raise InvalidOperationException("League is not active")

        if not LeagueService._user_can_manage_match(league, match, user_id):
            raise InvalidOperationException(
                "Only match participants or the league owner can start a match"
            )

        if match.status == MatchStatus.COMPLETED:
            raise InvalidOperationException("Match is already completed")

        if match.status == MatchStatus.IN_PROGRESS:
            raise InvalidOperationException("Match is already in progress")

        home_team = await UserTeam.get(match.home.team_id)
        away_team = await UserTeam.get(match.away.team_id)
        if not home_team:
            raise TeamNotFoundException(match.home.team_id)
        if not away_team:
            raise TeamNotFoundException(match.away.team_id)
        match.home_squad = LeagueService._sanitize_match_squad(
            home_team, match.home_squad, match.id
        )
        match.away_squad = LeagueService._sanitize_match_squad(
            away_team, match.away_squad, match.id
        )
        LeagueService._validate_match_squad(home_team, match.home_squad, "home")
        LeagueService._validate_match_squad(away_team, match.away_squad, "away")

        match.status = MatchStatus.IN_PROGRESS
        now = datetime.utcnow()
        match.started_at = now
        match.current_half = 1
        match.current_turn = 1
        match.home_turn = 1
        match.away_turn = 1
        match.turn_started_at = now
        match.home_turn_seconds = []
        match.away_turn_seconds = []

        await league.save()
        logger.info(f"Match {match_id} started by user {user_id}")
        return league

    @staticmethod
    async def add_match_event(
        league_id: str,
        match_id: str,
        user_id: str,
        request: AddMatchEventRequest,
    ) -> MatchDetail:
        """Add an event to a live match with audit trail."""
        league, match = await LeagueService._get_league_and_match(league_id, match_id)

        post_match_decision = (
            match.status == MatchStatus.COMPLETED
            and request.type == "temporary_player_decision"
        )
        if match.status != MatchStatus.IN_PROGRESS and not post_match_decision:
            raise InvalidOperationException("Match is not in progress")

        if not LeagueService._user_can_manage_match(league, match, user_id):
            raise InvalidOperationException(
                "Only match participants or the league owner can add events"
            )

        home_team = await UserTeam.get(match.home.team_id)
        away_team = await UserTeam.get(match.away.team_id)
        if not home_team:
            raise TeamNotFoundException(match.home.team_id)
        if not away_team:
            raise TeamNotFoundException(match.away.team_id)
        teams_by_side = {"home": home_team, "away": away_team}
        squads_by_side = {
            "home": set(match.home_squad),
            "away": set(match.away_squad),
        }

        def _validate_live_player(team_side: str, player_id: str | None) -> None:
            if not player_id:
                return
            team = teams_by_side[team_side]
            player = LeagueService._player_by_id(team, player_id)
            if not player:
                raise InvalidOperationException(
                    f"Player '{player_id}' not found in {team_side} team"
                )
            is_current_match_temporary = (
                LeagueService._is_current_match_temporary_player(player, match.id)
            )
            if (
                request.type == "temporary_player_decision"
                and is_current_match_temporary
            ):
                return
            squad = squads_by_side[team_side]
            if squad and player_id not in squad and not is_current_match_temporary:
                raise InvalidOperationException(
                    f"Player '{player.name}' was not selected for this match"
                )
            if squad:
                return
            if not LeagueService._is_player_available_for_match(player):
                raise InvalidOperationException(
                    f"Player '{player.name}' is not available for this match"
                )

        accidental_casualty = LeagueService._is_accidental_casualty_event(
            request.type, request.detail
        )
        _validate_live_player(request.team, request.player_id)
        victim_side = (
            request.team
            if request.type == "throw_teammate" or accidental_casualty
            else "away" if request.team == "home" else "home"
        )
        _validate_live_player(victim_side, request.victim_id)

        # Resolve username for audit trail
        user = await User.get(user_id)
        username = user.username if user else "unknown"

        event = MatchEvent(
            id=str(uuid.uuid4()),
            type=request.type,
            team=request.team,
            player_id=request.player_id,
            player_name=request.player_name,
            victim_id=request.victim_id,
            victim_name=request.victim_name,
            injury=request.injury,
            detail=request.detail,
            half=request.half,
            turn=request.turn,
            timestamp=datetime.utcnow(),
            created_by=user_id,
            created_by_name=username,
        )
        match.events.append(event)

        # Auto-update score for touchdowns
        if request.type == "touchdown":
            if request.team == "home":
                match.score_home += 1
            else:
                match.score_away += 1

        await league.save()
        logger.info(f"Event '{request.type}' added to match {match_id} by {username}")

        return await LeagueService.get_match_detail(league_id, match_id)

    @staticmethod
    async def delete_match_event(
        league_id: str,
        match_id: str,
        event_id: str,
        user_id: str,
    ) -> MatchDetail:
        """Remove an event from a live match."""
        league, match = await LeagueService._get_league_and_match(league_id, match_id)

        if match.status != MatchStatus.IN_PROGRESS:
            raise InvalidOperationException("Match is not in progress")

        if not LeagueService._user_can_manage_match(league, match, user_id):
            raise InvalidOperationException(
                "Only match participants or the league owner can remove events"
            )

        event_to_remove = None
        for e in match.events:
            if e.id == event_id:
                event_to_remove = e
                break

        if not event_to_remove:
            raise InvalidOperationException(f"Event {event_id} not found")

        # Reverse score impact for touchdowns
        if event_to_remove.type == "touchdown":
            if event_to_remove.team == "home":
                match.score_home = max(0, match.score_home - 1)
            else:
                match.score_away = max(0, match.score_away - 1)

        match.events.remove(event_to_remove)
        await league.save()

        logger.info(f"Event {event_id} removed from match {match_id} by user {user_id}")
        return await LeagueService.get_match_detail(league_id, match_id)

    @staticmethod
    async def apply_aftermatch_spp(
        league_id: str,
        match_id: str,
        user_id: str,
        request: ApplyAftermatchSppRequest,
    ) -> MatchDetail:
        """Apply the complete post-match report from backend-owned rules once."""
        league, match = await LeagueService._get_league_and_match(league_id, match_id)

        if match.status != MatchStatus.COMPLETED:
            raise InvalidOperationException("Match is not completed")

        if not LeagueService._user_can_manage_match(league, match, user_id):
            raise InvalidOperationException(
                "Only match participants or the league owner can submit aftermatch SPP"
            )

        rules = await SppRewardsRules.get("spp_rewards")
        if not rules:
            raise InvalidOperationException("SPP reward rules are not available")
        injury_rules = await InjuryRules.get("injury_rules")
        if not injury_rules:
            raise InvalidOperationException("Injury rules are not available")
        winnings_rules = None
        expensive_rules = None
        if request.winnings:
            winnings_rules = await WinningsRules.get("winnings")
            if not winnings_rules:
                raise InvalidOperationException("Winnings rules are not available")
            expensive_rules = await ExpensiveMistakesRules.get("expensive_mistakes")
            if not expensive_rules:
                raise InvalidOperationException(
                    "Expensive Mistakes rules are not available"
                )
        dedicated_fans_rules = None
        if request.dedicated_fans:
            dedicated_fans_rules = await DedicatedFansRules.get("dedicated_fans")
            if not dedicated_fans_rules:
                raise InvalidOperationException(
                    "Dedicated Fans rules are not available"
                )

        home_team = await UserTeam.get(match.home.team_id)
        away_team = await UserTeam.get(match.away.team_id)
        if not home_team:
            raise TeamNotFoundException(match.home.team_id)
        if not away_team:
            raise TeamNotFoundException(match.away.team_id)

        teams_by_side = {"home": home_team, "away": away_team}
        rosters_by_side = {}
        for team_side, team in teams_by_side.items():
            roster = await BaseRoster.find_one(BaseRoster.id == team.base_roster_id)
            if not roster:
                raise InvalidOperationException(
                    f"Base roster '{team.base_roster_id}' not found for {team_side} team"
                )
            rosters_by_side[team_side] = roster

        user = await User.get(user_id)
        username = user.username if user else "unknown"

        if match.aftermatch_spp_applied_at is not None:
            decisions = LeagueService._temporary_player_decisions(
                match, request.temporary_players
            )
            LeagueService._finalize_temporary_players(
                match,
                teams_by_side,
                rosters_by_side,
                decisions,
                user_id,
                username,
            )
            home_team.team_value = await UserTeamService._calculate_team_value(
                home_team, rosters_by_side["home"]
            )
            away_team.team_value = await UserTeamService._calculate_team_value(
                away_team, rosters_by_side["away"]
            )
            now = datetime.utcnow()
            home_team.updated_at = now
            away_team.updated_at = now
            await home_team.save()
            await away_team.save()
            await league.save()
            return await LeagueService.get_match_detail(league_id, match_id)

        squads_by_side = {
            "home": set(match.home_squad),
            "away": set(match.away_squad),
        }
        event_rewards = {r.event_type: r for r in rules.event_rewards}
        spp_deltas: dict[str, dict[str, dict[str, int | bool]]] = {
            "home": {},
            "away": {},
        }

        def _get_player(team: UserTeam, player_id: str):
            player = next((p for p in team.players if p.id == player_id), None)
            if not player:
                raise InvalidOperationException(
                    f"Player '{player_id}' not found in team '{team.name}'"
                )
            return player

        def _player_generates_spp(team: UserTeam, player_id: str) -> bool:
            player = _get_player(team, player_id)
            return not player.base_type.startswith("star_")

        def _validate_played_player(team_side: str, player_id: str | None) -> None:
            if not player_id:
                return
            player = _get_player(teams_by_side[team_side], player_id)
            squad = squads_by_side[team_side]
            is_current_match_temporary = (
                LeagueService._is_current_match_temporary_player(player, match.id)
            )
            if squad and player_id not in squad and not is_current_match_temporary:
                raise InvalidOperationException(
                    f"Player '{player.name}' was not selected for this match"
                )
            if squad:
                return
            if not LeagueService._is_player_available_for_match(player):
                raise InvalidOperationException(
                    f"Player '{player.name}' was not available for this match"
                )

        def _validate_match_event_reference(event_request: MatchEventRequest) -> None:
            _validate_played_player(event_request.team, event_request.player_id)
            if event_request.victim_id:
                accidental_casualty = LeagueService._is_accidental_casualty_event(
                    event_request.type, event_request.detail
                )
                victim_side = (
                    event_request.team
                    if event_request.type == "throw_teammate" or accidental_casualty
                    else "away" if event_request.team == "home" else "home"
                )
                _validate_played_player(victim_side, event_request.victim_id)

        def _recover_players_who_missed_match() -> None:
            for team_side, team in teams_by_side.items():
                squad = squads_by_side[team_side]
                recovered = []
                for player in team.players:
                    if (
                        LeagueService._player_status_value(player)
                        == PlayerStatus.MISSING_NEXT_GAME.value
                        and player.id not in squad
                    ):
                        player.status = PlayerStatus.HEALTHY
                        recovered.append(player.name)
                if recovered:
                    match.events.append(
                        MatchEvent(
                            id=str(uuid.uuid4()),
                            type="player_recovery",
                            team=team_side,
                            detail=(
                                "Players recovered after missing the fixture: "
                                + ", ".join(recovered)
                            ),
                            half=0,
                            turn=0,
                            timestamp=datetime.utcnow(),
                            created_by=user_id,
                            created_by_name=username,
                        )
                    )

        def _delta(team_side: str, player_id: str) -> dict[str, int | bool]:
            team = teams_by_side[team_side]
            _get_player(team, player_id)
            return spp_deltas[team_side].setdefault(
                player_id,
                {
                    "spp": 0,
                    "completions": 0,
                    "touchdowns": 0,
                    "casualties": 0,
                    "interceptions": 0,
                    "mvp": False,
                },
            )

        def _add_spp(
            team_side: str,
            player_id: str | None,
            amount: int,
            career_stat: str | None = None,
        ) -> None:
            if amount <= 0:
                return
            if not player_id:
                raise InvalidOperationException(
                    f"SPP event for {team_side} is missing credited player"
                )
            if team_side not in teams_by_side:
                raise InvalidOperationException(
                    f"SPP event has invalid team '{team_side}'"
                )
            if not _player_generates_spp(teams_by_side[team_side], player_id):
                return
            delta = _delta(team_side, player_id)
            delta["spp"] = int(delta["spp"]) + amount
            if career_stat:
                delta[career_stat] = int(delta[career_stat]) + 1

        def _detail_has_yes(detail: str | None, label: str) -> bool:
            normalized = (detail or "").lower()
            return (
                f"{label}: sí" in normalized
                or f"{label}: si" in normalized
                or f"{label}=true" in normalized
                or f"{label}=1" in normalized
            )

        def _score_event(event: MatchEvent) -> None:
            if event.type in event_rewards:
                if LeagueService._is_accidental_casualty_event(
                    event.type, event.detail
                ):
                    return
                reward = event_rewards[event.type]
                if reward.requires_player and not event.player_id:
                    raise InvalidOperationException(
                        f"Event '{event.type}' is missing credited player"
                    )
                if event.player_id:
                    _add_spp(
                        event.team, event.player_id, reward.spp, reward.career_stat
                    )
                return

            if event.type == rules.throw_teammate.event_type:
                landed = _detail_has_yes(event.detail, "cae de pie") or _detail_has_yes(
                    event.detail, "landed"
                )
                if not landed:
                    return
                _add_spp(
                    event.team,
                    event.victim_id,
                    rules.throw_teammate.thrown_player_landed_spp,
                )
                superb = _detail_has_yes(event.detail, "soberbio") or _detail_has_yes(
                    event.detail, "superb"
                )
                if superb:
                    _add_spp(
                        event.team,
                        event.player_id,
                        rules.throw_teammate.superb_thrower_spp,
                    )

        if request.mvp_home is not None:
            LeagueService._validate_match_player_reference(
                home_team, request.mvp_home, "MVP"
            )
            player = LeagueService._player_by_id(home_team, request.mvp_home)
            if player and player.base_type.startswith("star_"):
                raise InvalidOperationException("Star Players cannot be MVP")
            match.mvp_home = request.mvp_home
        if request.mvp_away is not None:
            LeagueService._validate_match_player_reference(
                away_team, request.mvp_away, "MVP"
            )
            player = LeagueService._player_by_id(away_team, request.mvp_away)
            if player and player.base_type.startswith("star_"):
                raise InvalidOperationException("Star Players cannot be MVP")
            match.mvp_away = request.mvp_away
        if request.gate is not None:
            match.gate = request.gate

        if not match.mvp_home or not match.mvp_away:
            raise InvalidOperationException(
                "Both MVP selections are required before applying the post-match report"
            )

        post_match_events: list[MatchEvent] = []
        for event_request in request.post_match_events:
            _validate_match_event_reference(event_request)
            event = MatchEvent(
                id=str(uuid.uuid4()),
                type=event_request.type,
                team=event_request.team,
                player_id=event_request.player_id,
                player_name=event_request.player_name,
                victim_id=event_request.victim_id,
                victim_name=event_request.victim_name,
                injury=event_request.injury,
                detail=event_request.detail,
                half=event_request.half,
                turn=event_request.turn,
                timestamp=datetime.utcnow(),
                created_by=user_id,
                created_by_name=username,
            )
            post_match_events.append(event)

        for event in [*match.events, *post_match_events]:
            _score_event(event)

        for team_side, player_id in [
            ("home", match.mvp_home),
            ("away", match.mvp_away),
        ]:
            if player_id:
                _validate_played_player(team_side, player_id)
                if not _player_generates_spp(teams_by_side[team_side], player_id):
                    raise InvalidOperationException("Star Players cannot be MVP")
                delta = _delta(team_side, player_id)
                delta["spp"] = int(delta["spp"]) + rules.mvp_spp
                delta["mvp"] = True

        def _apply_delta(
            team_side: str, player_id: str, delta: dict[str, int | bool]
        ) -> None:
            player = _get_player(teams_by_side[team_side], player_id)
            player.spp += int(delta["spp"])
            player.career.completions += int(delta["completions"])
            player.career.touchdowns += int(delta["touchdowns"])
            player.career.casualties += int(delta["casualties"])
            player.career.interceptions += int(delta["interceptions"])
            if bool(delta["mvp"]):
                player.career.mvp_awards += 1

        for team_side, player_deltas in spp_deltas.items():
            for player_id, delta in player_deltas.items():
                _apply_delta(team_side, player_id, delta)

        def _casualty_result(roll: int):
            for result in injury_rules.casualty_table:
                if result.min_roll <= roll <= result.max_roll:
                    return result
            raise InvalidOperationException(f"Invalid casualty roll '{roll}'")

        def _lasting_injury_result(roll: int):
            for result in injury_rules.lasting_injury_table:
                if result.min_roll <= roll <= result.max_roll:
                    return result
            raise InvalidOperationException(f"Invalid lasting injury roll '{roll}'")

        def _apply_stat_reduction(player, stat: str) -> None:
            if stat == "MA":
                player.stats.MA = max(1, player.stats.MA - 1)
            elif stat == "ST":
                player.stats.ST = max(1, player.stats.ST - 1)
            elif stat == "AV":
                player.stats.AV = max(3, player.stats.AV - 1)
            elif stat == "AG":
                player.stats.AG = min(7, player.stats.AG + 1)
            elif stat == "PA" and player.stats.PA is not None:
                player.stats.PA = min(7, player.stats.PA + 1)

        def _apply_injury(injury_request) -> None:
            team = teams_by_side[injury_request.team]
            player = _get_player(team, injury_request.player_id)
            casualty = _casualty_result(injury_request.casualty_roll)
            lasting = None
            if casualty.requires_lasting_injury_roll:
                if injury_request.lasting_injury_roll is None:
                    raise InvalidOperationException(
                        "Lasting Injury result requires a lasting injury D6 roll"
                    )
                lasting = _lasting_injury_result(injury_request.lasting_injury_roll)
                _apply_stat_reduction(player, lasting.stat)
                player.injuries.append(lasting.code)

            for injury_code in casualty.injury_codes:
                player.injuries.append(injury_code)

            player.status = PlayerStatus(casualty.player_status)
            detail = f"Casualty D16 {injury_request.casualty_roll}: {casualty.code}"
            if lasting:
                detail += (
                    f" · Lasting D6 {injury_request.lasting_injury_roll}: "
                    f"{lasting.code} ({lasting.reduction_label})"
                )
            player.injury_history.append(
                PlayerInjuryRecord(
                    type="lasting_injury" if lasting else casualty.code,
                    label=(lasting.label.es if lasting else casualty.label.es)
                    or (lasting.label.en if lasting else casualty.label.en)
                    or (lasting.code if lasting else casualty.code),
                    notes=detail,
                    roll=injury_request.lasting_injury_roll if lasting else None,
                    stat=lasting.stat if lasting else None,
                    reduction=lasting.reduction_label if lasting else None,
                )
            )
            match.events.append(
                MatchEvent(
                    id=str(uuid.uuid4()),
                    type=casualty.code,
                    team=injury_request.team,
                    player_id=injury_request.player_id,
                    player_name=player.name,
                    injury=lasting.code if lasting else casualty.code,
                    detail=detail,
                    half=0,
                    turn=0,
                    timestamp=datetime.utcnow(),
                    created_by=user_id,
                    created_by_name=username,
                )
            )

        _recover_players_who_missed_match()

        for injury_request in request.injuries:
            _validate_played_player(injury_request.team, injury_request.player_id)
            _apply_injury(injury_request)

        def _record_result(standing, won: bool, lost: bool) -> None:
            if won:
                standing.wins += 1
            elif lost:
                standing.losses += 1
            else:
                standing.draws += 1

        def _remove_recorded_result(standing, won: bool, lost: bool) -> None:
            if won:
                standing.wins = max(0, standing.wins - 1)
            elif lost:
                standing.losses = max(0, standing.losses - 1)
            else:
                standing.draws = max(0, standing.draws - 1)

        def _sync_final_score_from_winnings() -> None:
            if not request.winnings:
                return
            new_home = request.winnings.home_touchdowns
            new_away = request.winnings.away_touchdowns
            if new_home == match.score_home and new_away == match.score_away:
                return

            home_standing = league.get_team_standing(match.home.team_id)
            away_standing = league.get_team_standing(match.away.team_id)
            if home_standing and away_standing:
                old_home = match.score_home
                old_away = match.score_away
                home_standing.touchdowns_for += new_home - old_home
                home_standing.touchdowns_against += new_away - old_away
                away_standing.touchdowns_for += new_away - old_away
                away_standing.touchdowns_against += new_home - old_home

                _remove_recorded_result(
                    home_standing,
                    old_home > old_away,
                    old_home < old_away,
                )
                _remove_recorded_result(
                    away_standing,
                    old_away > old_home,
                    old_away < old_home,
                )
                _record_result(
                    home_standing,
                    new_home > new_away,
                    new_home < new_away,
                )
                _record_result(
                    away_standing,
                    new_away > new_home,
                    new_away < new_home,
                )

            match.score_home = new_home
            match.score_away = new_away

        _sync_final_score_from_winnings()

        def _calculate_winnings(
            team: UserTeam, opponent: UserTeam, touchdowns: int, stalling: bool
        ) -> int:
            fan_attendance = team.dedicated_fans + opponent.dedicated_fans
            fan_base = fan_attendance / winnings_rules.fan_attendance_divisor
            no_stalling_bonus = 0 if stalling else winnings_rules.no_stalling_bonus
            return int(
                (fan_base + touchdowns + no_stalling_bonus)
                * winnings_rules.gold_multiplier
            )

        def _expensive_result_code(treasury: int, roll: int) -> str:
            for band in expensive_rules.bands:
                if treasury >= band.min_treasury and (
                    band.max_treasury is None or treasury <= band.max_treasury
                ):
                    return band.results[roll - 1]
            raise InvalidOperationException(
                f"No Expensive Mistakes band found for treasury '{treasury}'"
            )

        def _apply_expensive_mistakes(treasury: int, dice) -> tuple[int, str | None]:
            if treasury < expensive_rules.min_treasury:
                return treasury, None
            if dice.roll is None:
                raise InvalidOperationException(
                    "Expensive Mistakes D6 roll is required for treasury 100,000+"
                )

            result_code = _expensive_result_code(treasury, dice.roll)
            effect = next(
                (
                    effect
                    for effect in expensive_rules.effects
                    if effect.code == result_code
                ),
                None,
            )
            calculation = effect.calculation if effect else "none"
            if calculation == "lose_d3_x_10000":
                if dice.d3 is None:
                    raise InvalidOperationException(
                        "Minor Incident requires an Expensive Mistakes D3 roll"
                    )
                return max(0, treasury - (dice.d3 * 10_000)), result_code
            if calculation == "lose_half_round_down_5000":
                loss = int((treasury / 2) // 5_000) * 5_000
                return max(0, treasury - loss), result_code
            if calculation == "keep_2d6_x_10000":
                if dice.catastrophe_d6_a is None or dice.catastrophe_d6_b is None:
                    raise InvalidOperationException(
                        "Catastrophe requires two Expensive Mistakes D6 rolls"
                    )
                kept = (dice.catastrophe_d6_a + dice.catastrophe_d6_b) * 10_000
                return min(treasury, kept), result_code
            return treasury, result_code

        def _apply_winnings() -> None:
            if not request.winnings:
                return

            home_winnings = _calculate_winnings(
                home_team,
                away_team,
                request.winnings.home_touchdowns,
                request.winnings.home_stalling,
            )
            away_winnings = _calculate_winnings(
                away_team,
                home_team,
                request.winnings.away_touchdowns,
                request.winnings.away_stalling,
            )

            home_before_expensive = home_team.treasury + home_winnings
            away_before_expensive = away_team.treasury + away_winnings
            home_final, home_expensive = _apply_expensive_mistakes(
                home_before_expensive, request.winnings.home_expensive_mistakes
            )
            away_final, away_expensive = _apply_expensive_mistakes(
                away_before_expensive, request.winnings.away_expensive_mistakes
            )

            home_team.treasury = home_final
            away_team.treasury = away_final
            match.events.extend(
                [
                    MatchEvent(
                        id=str(uuid.uuid4()),
                        type="winnings",
                        team="home",
                        detail=(
                            f"Winnings: {home_winnings}; treasury before Expensive "
                            f"Mistakes: {home_before_expensive}; result: {home_expensive or 'not_required'}; final treasury: {home_final}"
                        ),
                        half=0,
                        turn=0,
                        timestamp=datetime.utcnow(),
                        created_by=user_id,
                        created_by_name=username,
                    ),
                    MatchEvent(
                        id=str(uuid.uuid4()),
                        type="winnings",
                        team="away",
                        detail=(
                            f"Winnings: {away_winnings}; treasury before Expensive "
                            f"Mistakes: {away_before_expensive}; result: {away_expensive or 'not_required'}; final treasury: {away_final}"
                        ),
                        half=0,
                        turn=0,
                        timestamp=datetime.utcnow(),
                        created_by=user_id,
                        created_by_name=username,
                    ),
                ]
            )

        _apply_winnings()

        def _next_dedicated_fans(
            current: int, roll: int | None, won: bool, lost: bool
        ) -> int:
            current = max(
                dedicated_fans_rules.min_value,
                min(dedicated_fans_rules.max_value, current),
            )
            if won:
                if roll is None:
                    raise InvalidOperationException(
                        "Winning team requires a Dedicated Fans D6 roll"
                    )
                if roll >= current:
                    return min(dedicated_fans_rules.max_value, current + 1)
            elif lost:
                if roll is None:
                    raise InvalidOperationException(
                        "Losing team requires a Dedicated Fans D6 roll"
                    )
                if roll < current:
                    return max(dedicated_fans_rules.min_value, current - 1)
            return current

        def _apply_dedicated_fans() -> None:
            if not request.dedicated_fans:
                return

            home_before = home_team.dedicated_fans
            away_before = away_team.dedicated_fans
            home_touchdowns = (
                request.winnings.home_touchdowns
                if request.winnings
                else match.score_home
            )
            away_touchdowns = (
                request.winnings.away_touchdowns
                if request.winnings
                else match.score_away
            )
            home_team.dedicated_fans = _next_dedicated_fans(
                home_before,
                request.dedicated_fans.home_roll,
                home_touchdowns > away_touchdowns,
                home_touchdowns < away_touchdowns,
            )
            away_team.dedicated_fans = _next_dedicated_fans(
                away_before,
                request.dedicated_fans.away_roll,
                away_touchdowns > home_touchdowns,
                away_touchdowns < home_touchdowns,
            )
            match.events.extend(
                [
                    MatchEvent(
                        id=str(uuid.uuid4()),
                        type="dedicated_fans",
                        team="home",
                        detail=(
                            f"Dedicated Fans: {home_before} → {home_team.dedicated_fans}; "
                            f"roll: {request.dedicated_fans.home_roll or 'not_required'}"
                        ),
                        half=0,
                        turn=0,
                        timestamp=datetime.utcnow(),
                        created_by=user_id,
                        created_by_name=username,
                    ),
                    MatchEvent(
                        id=str(uuid.uuid4()),
                        type="dedicated_fans",
                        team="away",
                        detail=(
                            f"Dedicated Fans: {away_before} → {away_team.dedicated_fans}; "
                            f"roll: {request.dedicated_fans.away_roll or 'not_required'}"
                        ),
                        half=0,
                        turn=0,
                        timestamp=datetime.utcnow(),
                        created_by=user_id,
                        created_by_name=username,
                    ),
                ]
            )

        _apply_dedicated_fans()

        def _apply_temporary_players() -> None:
            decisions = LeagueService._temporary_player_decisions(
                match, request.temporary_players
            )
            LeagueService._finalize_temporary_players(
                match,
                teams_by_side,
                rosters_by_side,
                decisions,
                user_id,
                username,
            )

        _apply_temporary_players()

        async def _refresh_team_value(team: UserTeam) -> None:
            roster = next(
                (
                    roster
                    for side, roster in rosters_by_side.items()
                    if teams_by_side[side].id == team.id
                ),
                None,
            )
            team.team_value = await UserTeamService._calculate_team_value(team, roster)

        await _refresh_team_value(home_team)
        await _refresh_team_value(away_team)
        await LeagueService._clear_match_sent_off_statuses(match)

        match.events.extend(post_match_events)

        now = datetime.utcnow()
        home_team.updated_at = now
        away_team.updated_at = now
        match.aftermatch_spp_applied_at = now
        if request.winnings:
            match.aftermatch_winnings_applied_at = now

        await home_team.save()
        await away_team.save()
        await league.save()

        logger.info(f"Aftermatch SPP applied for match {match_id} by user {user_id}")
        return await LeagueService.get_match_detail(league_id, match_id)

    @staticmethod
    async def finalize_aftermatch_rosters(
        league_id: str,
        match_id: str,
        user_id: str,
        temporary_players: list[AftermatchTemporaryPlayerDecision],
    ) -> MatchDetail:
        """Force keep/release resolution for all temporary players in both rosters."""
        league, match = await LeagueService._get_league_and_match(league_id, match_id)

        if not LeagueService._user_can_manage_match(league, match, user_id):
            raise InvalidOperationException(
                "Only match participants or the league owner can finalize rosters"
            )

        home_team = await UserTeam.get(match.home.team_id)
        away_team = await UserTeam.get(match.away.team_id)
        if not home_team:
            raise TeamNotFoundException(match.home.team_id)
        if not away_team:
            raise TeamNotFoundException(match.away.team_id)

        teams_by_side = {"home": home_team, "away": away_team}
        rosters_by_side = {}
        for team_side, team in teams_by_side.items():
            roster = await BaseRoster.find_one(BaseRoster.id == team.base_roster_id)
            if not roster:
                raise InvalidOperationException(
                    f"Base roster '{team.base_roster_id}' not found for {team_side} team"
                )
            rosters_by_side[team_side] = roster

        user = await User.get(user_id)
        username = user.username if user else "unknown"
        decisions = LeagueService._temporary_player_decisions(match, temporary_players)
        LeagueService._finalize_temporary_players(
            match,
            teams_by_side,
            rosters_by_side,
            decisions,
            user_id,
            username,
        )

        home_team.team_value = await UserTeamService._calculate_team_value(
            home_team, rosters_by_side["home"]
        )
        away_team.team_value = await UserTeamService._calculate_team_value(
            away_team, rosters_by_side["away"]
        )
        now = datetime.utcnow()
        home_team.updated_at = now
        away_team.updated_at = now
        await home_team.save()
        await away_team.save()
        await league.save()
        return await LeagueService.get_match_detail(league_id, match_id)

    @staticmethod
    async def update_match_state(
        league_id: str,
        match_id: str,
        user_id: str,
        request: UpdateMatchStateRequest,
    ) -> MatchDetail:
        """Update live match state (score, half, turn, weather, etc.)."""
        league, match = await LeagueService._get_league_and_match(league_id, match_id)

        # Allow ceremony state before match starts.
        _pre_match_only = (
            request.weather is not None
            or request.kickoff_event is not None
            or request.current_team is not None
            or request.home_ready is not None
            or request.away_ready is not None
            or request.home_squad is not None
            or request.away_squad is not None
            or request.home_inducement_purchases is not None
            or request.away_inducement_purchases is not None
            or request.home_inducement_uses is not None
            or request.away_inducement_uses is not None
            or request.home_inducement_details is not None
            or request.away_inducement_details is not None
        ) and all(
            v is None
            for v in [
                request.score_home,
                request.score_away,
                request.current_half,
                request.current_turn,
                request.home_turn,
                request.away_turn,
                request.rerolls_used_home,
                request.rerolls_used_away,
                request.mvp_home,
                request.mvp_away,
                request.gate,
            ]
        )
        # Post-match report is opened after live match completion, but it still
        # needs to persist MVPs and gate. Keep score/turn/event edits protected.
        _post_match_report_only = (
            request.mvp_home is not None
            or request.mvp_away is not None
            or request.gate is not None
        ) and all(
            v is None
            for v in [
                request.score_home,
                request.score_away,
                request.current_half,
                request.current_turn,
                request.current_team,
                request.home_turn,
                request.away_turn,
                request.weather,
                request.kickoff_event,
                request.home_ready,
                request.away_ready,
                request.home_squad,
                request.away_squad,
                request.rerolls_used_home,
                request.rerolls_used_away,
                request.home_inducement_purchases,
                request.away_inducement_purchases,
                request.home_inducement_uses,
                request.away_inducement_uses,
                request.home_inducement_details,
                request.away_inducement_details,
            ]
        )
        if (
            match.status != MatchStatus.IN_PROGRESS
            and not _pre_match_only
            and not (match.status == MatchStatus.COMPLETED and _post_match_report_only)
        ):
            raise InvalidOperationException("Match is not in progress")

        if not LeagueService._user_can_manage_match(league, match, user_id):
            raise InvalidOperationException(
                "Only match participants or the league owner can update match state"
            )

        # Resolve username for audit trail
        user = await User.get(user_id)
        username = user.username if user else "unknown"

        def _make_event(
            event_type: str, detail: str, team: str = "system"
        ) -> MatchEvent:
            return MatchEvent(
                id=str(uuid.uuid4()),
                type=event_type,
                team=team,
                detail=detail,
                half=match.current_half,
                turn=match.current_turn,
                timestamp=datetime.utcnow(),
                created_by=user_id,
                created_by_name=username,
            )

        # Apply only provided fields & log changes as events
        if request.score_home is not None and request.score_home != match.score_home:
            old, new = match.score_home, request.score_home
            match.score_home = new
            match.events.append(
                _make_event("score_change", f"Home score: {old} → {new}", "home")
            )
        if request.score_away is not None and request.score_away != match.score_away:
            old, new = match.score_away, request.score_away
            match.score_away = new
            match.events.append(
                _make_event("score_change", f"Away score: {old} → {new}", "away")
            )
        if (
            request.current_half is not None
            and request.current_half != match.current_half
        ):
            old, new = match.current_half, request.current_half
            match.current_half = new
            match.events.append(_make_event("half_change", f"Half: {old} → {new}"))
        if (
            request.current_turn is not None
            and request.current_turn != match.current_turn
        ):
            old, new = match.current_turn, request.current_turn
            match.current_turn = new
            match.events.append(_make_event("turn_change", f"Turn: {old} → {new}"))
        if (
            request.current_team is not None
            and request.current_team != match.current_team
        ):
            previous_team = match.current_team
            if match.status == MatchStatus.IN_PROGRESS:
                now = datetime.utcnow()
                elapsed = 0
                if match.turn_started_at is not None:
                    elapsed = max(0, int((now - match.turn_started_at).total_seconds()))
                if previous_team == "home":
                    match.home_turn_seconds.append(elapsed)
                else:
                    match.away_turn_seconds.append(elapsed)
                match.current_team = request.current_team
                match.turn_started_at = now
                match.events.append(
                    _make_event(
                        "turn_change",
                        f"{previous_team} turn ended in {elapsed}s; next: {request.current_team}",
                    )
                )
            else:
                match.current_team = request.current_team
                match.events.append(
                    _make_event(
                        "receiving_team_change",
                        f"Receiving team: {previous_team} -> {request.current_team}",
                    )
                )
        if request.home_turn is not None:
            match.home_turn = request.home_turn
        if request.away_turn is not None:
            match.away_turn = request.away_turn
        if request.weather is not None and request.weather != match.weather:
            old = match.weather or "—"
            match.weather = request.weather
            match.events.append(
                _make_event("weather_change", f"Weather: {old} → {request.weather}")
            )
        if (
            request.kickoff_event is not None
            and request.kickoff_event != match.kickoff_event
        ):
            old = match.kickoff_event or "—"
            match.kickoff_event = request.kickoff_event
            match.events.append(
                _make_event(
                    "kickoff_change", f"Kickoff: {old} → {request.kickoff_event}"
                )
            )
        if request.rerolls_used_home is not None:
            if request.rerolls_used_home != match.rerolls_used_home:
                old, new = match.rerolls_used_home, request.rerolls_used_home
                match.rerolls_used_home = new
                match.events.append(
                    _make_event(
                        "reroll_change",
                        f"Home rerolls used: {old} → {new}",
                        "home",
                    )
                )
            else:
                match.rerolls_used_home = request.rerolls_used_home
        if request.rerolls_used_away is not None:
            if request.rerolls_used_away != match.rerolls_used_away:
                old, new = match.rerolls_used_away, request.rerolls_used_away
                match.rerolls_used_away = new
                match.events.append(
                    _make_event(
                        "reroll_change",
                        f"Away rerolls used: {old} → {new}",
                        "away",
                    )
                )
            else:
                match.rerolls_used_away = request.rerolls_used_away
        if request.home_inducement_purchases is not None:
            match.home_inducement_purchases = {
                key: value
                for key, value in request.home_inducement_purchases.items()
                if value > 0
            }
        if request.away_inducement_purchases is not None:
            match.away_inducement_purchases = {
                key: value
                for key, value in request.away_inducement_purchases.items()
                if value > 0
            }
        if request.home_inducement_uses is not None:
            match.home_inducement_uses = {
                key: value
                for key, value in request.home_inducement_uses.items()
                if value > 0
            }
        if request.away_inducement_uses is not None:
            match.away_inducement_uses = {
                key: value
                for key, value in request.away_inducement_uses.items()
                if value > 0
            }
        if request.home_inducement_details is not None:
            match.home_inducement_details = {
                key: [str(item).strip() for item in value if str(item).strip()]
                for key, value in request.home_inducement_details.items()
                if isinstance(value, list)
            }
        if request.away_inducement_details is not None:
            match.away_inducement_details = {
                key: [str(item).strip() for item in value if str(item).strip()]
                for key, value in request.away_inducement_details.items()
                if isinstance(value, list)
            }

        def _sanitize_inducement_uses(
            uses: dict[str, int], purchases: dict[str, int]
        ) -> dict[str, int]:
            sanitized: dict[str, int] = {}
            prayer_count = purchases.get("prayers_to_nuffle", 0)
            for key, value in uses.items():
                if value <= 0:
                    continue
                if key in purchases and purchases[key] > 0:
                    sanitized[key] = min(value, purchases[key])
                    continue
                prefix = "prayers_to_nuffle#"
                if key.startswith(prefix) and prayer_count > 0:
                    try:
                        prayer_index = int(key[len(prefix) :])
                    except ValueError:
                        continue
                    if 0 <= prayer_index < prayer_count:
                        sanitized[key] = min(value, 1)
            return sanitized

        match.home_inducement_uses = _sanitize_inducement_uses(
            match.home_inducement_uses, match.home_inducement_purchases
        )
        match.away_inducement_uses = _sanitize_inducement_uses(
            match.away_inducement_uses, match.away_inducement_purchases
        )
        match.home_inducement_details = {
            key: value[: match.home_inducement_purchases[key]]
            for key, value in match.home_inducement_details.items()
            if key in match.home_inducement_purchases
            and match.home_inducement_purchases[key] > 0
            and value
        }
        match.away_inducement_details = {
            key: value[: match.away_inducement_purchases[key]]
            for key, value in match.away_inducement_details.items()
            if key in match.away_inducement_purchases
            and match.away_inducement_purchases[key] > 0
            and value
        }
        if request.home_ready is not None:
            match.home_ready = request.home_ready
        if request.away_ready is not None:
            match.away_ready = request.away_ready
        if request.home_squad is not None:
            home_team = await UserTeam.get(match.home.team_id)
            if not home_team:
                raise TeamNotFoundException(match.home.team_id)
            LeagueService._validate_match_squad(home_team, request.home_squad, "home")
            match.home_squad = request.home_squad
        if request.away_squad is not None:
            away_team = await UserTeam.get(match.away.team_id)
            if not away_team:
                raise TeamNotFoundException(match.away.team_id)
            LeagueService._validate_match_squad(away_team, request.away_squad, "away")
            match.away_squad = request.away_squad
        if request.mvp_home is not None:
            match.mvp_home = request.mvp_home
        if request.mvp_away is not None:
            match.mvp_away = request.mvp_away
        if request.gate is not None:
            match.gate = request.gate

        await league.save()
        logger.info(f"Match {match_id} state updated by user {user_id}")
        return await LeagueService.get_match_detail(league_id, match_id)

    @staticmethod
    async def complete_match(league_id: str, match_id: str, user_id: str) -> League:
        """Complete a live match and update standings."""
        league, match = await LeagueService._get_league_and_match(league_id, match_id)

        if match.status != MatchStatus.IN_PROGRESS:
            raise InvalidOperationException("Match is not in progress")

        if not LeagueService._user_can_manage_match(league, match, user_id):
            raise InvalidOperationException(
                "Only match participants or the league owner can complete a match"
            )

        match.status = MatchStatus.COMPLETED
        match.played_at = datetime.utcnow()

        # Update standings
        home_standing = league.get_team_standing(match.home.team_id)
        away_standing = league.get_team_standing(match.away.team_id)

        if home_standing and away_standing:
            home_standing.touchdowns_for += match.score_home
            home_standing.touchdowns_against += match.score_away
            away_standing.touchdowns_for += match.score_away
            away_standing.touchdowns_against += match.score_home

            home_cas = sum(
                1 for e in match.events if e.type == "casualty" and e.team == "home"
            )
            away_cas = sum(
                1 for e in match.events if e.type == "casualty" and e.team == "away"
            )
            home_standing.casualties_for += home_cas
            home_standing.casualties_against += away_cas
            away_standing.casualties_for += away_cas
            away_standing.casualties_against += home_cas

            if match.score_home > match.score_away:
                home_standing.wins += 1
                away_standing.losses += 1
            elif match.score_home < match.score_away:
                home_standing.losses += 1
                away_standing.wins += 1
            else:
                home_standing.draws += 1
                away_standing.draws += 1

        await league.save()
        logger.info(
            f"Match {match_id} completed: {match.score_home}-{match.score_away}"
        )
        return league

    @staticmethod
    async def get_active_matches_for_user(user_id: str) -> list:
        """Get all active (in-progress) matches involving a user."""
        leagues = await League.find({"status": LeagueStatus.ACTIVE}).to_list()

        active_matches = []
        for league in leagues:
            for m in league.matches:
                if m.status == MatchStatus.IN_PROGRESS and (
                    m.home.user_id == user_id or m.away.user_id == user_id
                ):
                    active_matches.append(
                        {
                            "league_id": str(league.id),
                            "league_name": league.name,
                            "match": MatchSummary(
                                id=m.id,
                                round=m.round,
                                home=MatchTeamResponse(
                                    team_id=m.home.team_id,
                                    team_name=m.home.team_name,
                                    user_id=m.home.user_id,
                                    username=m.home.username,
                                    base_roster_id=m.home.base_roster_id,
                                ),
                                away=MatchTeamResponse(
                                    team_id=m.away.team_id,
                                    team_name=m.away.team_name,
                                    user_id=m.away.user_id,
                                    username=m.away.username,
                                    base_roster_id=m.away.base_roster_id,
                                ),
                                status=m.status,
                                score_home=m.score_home,
                                score_away=m.score_away,
                                weather=m.weather,
                                kickoff_event=m.kickoff_event,
                                current_half=m.current_half,
                                current_turn=m.current_turn,
                                started_at=m.started_at,
                            ),
                        }
                    )
        return active_matches
