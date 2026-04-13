"""Service for league operations."""

import logging
import uuid
from datetime import datetime
from itertools import combinations
from typing import Optional

from exceptions.exceptions import (
    InvalidOperationException,
    LeagueNotFoundException,
    TeamNotFoundException,
)
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
from models.user_team.team import UserTeam
from schemas.league import (
    AddMatchEventRequest,
    CreateLeagueRequest,
    LeagueByCodePreview,
    LeagueDetail,
    LeagueRulesRequest,
    LeagueStandingResponse,
    LeagueSummary,
    LeagueTeamResponse,
    MatchDetail,
    MatchEventResponse,
    MatchSummary,
    MatchTeamResponse,
    RecordMatchResultRequest,
    UpdateLeagueRequest,
    UpdateMatchStateRequest,
)

logger = logging.getLogger(__name__)


class LeagueService:
    """Service for managing leagues."""

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
        return await League.get(league_id)

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

            # Calculate current round from matches (lowest round with pending matches)
            current_round = None
            if league.matches:
                pending_rounds = [
                    m.round for m in league.matches if m.status != MatchStatus.COMPLETED
                ]
                if pending_rounds:
                    current_round = min(pending_rounds)
                else:
                    # All matches completed - show the last round
                    current_round = max(m.round for m in league.matches)

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
                    current_round=current_round,
                )
            )

        return results

    @staticmethod
    async def get_league_detail(league_id: str) -> Optional[LeagueDetail]:
        """Get full league detail."""
        league = await League.get(league_id)
        if not league:
            return None

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
        league = await League.get(league_id)
        if not league:
            raise LeagueNotFoundException(league_id)

        if league.invite_code != invite_code.upper():
            raise InvalidOperationException("Código de invitación incorrecto")

        team = await UserTeam.get(team_id)
        if not team:
            raise TeamNotFoundException(team_id)

        if team.user_id != user_id:
            raise InvalidOperationException("Cannot join with another user's team")

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
        league = await League.get(league_id)
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
        league = await League.get(league_id)
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
    async def start_league(league_id: str, owner_id: str) -> League:
        """Start the league and generate fixtures."""
        league = await League.get(league_id)
        if not league:
            raise LeagueNotFoundException(league_id)

        if league.owner_id != owner_id:
            raise InvalidOperationException("Only the owner can start the league")

        if league.status != LeagueStatus.DRAFT:
            raise InvalidOperationException("League has already started")

        if len(league.teams) < 2:
            raise InvalidOperationException("Need at least 2 teams to start")

        # Generate matches based on format
        if league.format == "round_robin":
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

    # ============== Match Operations ==============

    @staticmethod
    async def record_match_result(
        league_id: str, match_id: str, request: RecordMatchResultRequest
    ) -> League:
        """Record the result of a match."""
        league = await League.get(league_id)
        if not league:
            raise LeagueNotFoundException(league_id)

        if league.status != LeagueStatus.ACTIVE:
            raise InvalidOperationException("League is not active")

        # Find match
        match = None
        for m in league.matches:
            if m.id == match_id:
                match = m
                break

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
                1 for e in request.events if e.type == "casualty" and e.team == "home"
            )
            away_cas = sum(
                1 for e in request.events if e.type == "casualty" and e.team == "away"
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

        await league.save()
        logger.info(
            f"Recorded result for match {match_id}: {request.score_home}-{request.score_away}"
        )

        return league

    @staticmethod
    async def get_match_detail(league_id: str, match_id: str) -> Optional[MatchDetail]:
        """Get full match detail."""
        league = await League.get(league_id)
        if not league:
            return None

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
                    rerolls_used_home=m.rerolls_used_home,
                    rerolls_used_away=m.rerolls_used_away,
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
                    started_at=m.started_at,
                    scheduled_at=m.scheduled_at,
                    played_at=m.played_at,
                )

        return None

    # ============== Delete Operations ==============

    @staticmethod
    async def delete_league(league_id: str, user_id: str) -> None:
        """Delete a league (owner only)."""
        league = await League.get(league_id)
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
        league = await League.get(league_id)
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
        league = await League.get(league_id)
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

        match.status = MatchStatus.IN_PROGRESS
        match.started_at = datetime.utcnow()
        match.current_half = 1
        match.current_turn = 1

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

        if match.status != MatchStatus.IN_PROGRESS:
            raise InvalidOperationException("Match is not in progress")

        if not LeagueService._user_can_manage_match(league, match, user_id):
            raise InvalidOperationException(
                "Only match participants or the league owner can add events"
            )

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
    async def update_match_state(
        league_id: str,
        match_id: str,
        user_id: str,
        request: UpdateMatchStateRequest,
    ) -> MatchDetail:
        """Update live match state (score, half, turn, weather, etc.)."""
        league, match = await LeagueService._get_league_and_match(league_id, match_id)

        # Allow weather / kickoff changes before the match starts (pre-match ceremony)
        _pre_match_only = (
            request.weather is not None or request.kickoff_event is not None
        ) and all(
            v is None
            for v in [
                request.score_home,
                request.score_away,
                request.current_half,
                request.current_turn,
                request.rerolls_used_home,
                request.rerolls_used_away,
                request.mvp_home,
                request.mvp_away,
                request.gate,
            ]
        )
        if match.status != MatchStatus.IN_PROGRESS and not _pre_match_only:
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
