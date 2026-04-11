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
    CreateLeagueRequest,
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
                    created_at=league.created_at,
                )
            )

        return results

    @staticmethod
    async def get_leagues_by_user(user_id: str) -> list[LeagueSummary]:
        """Get leagues where user has a team."""
        leagues = await League.find({"teams.user_id": user_id}).to_list()

        results = []
        for league in leagues:
            owner = None
            try:
                owner = await User.get(league.owner_id)
            except Exception:
                pass
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
                    created_at=league.created_at,
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
                    username=m.home.username,
                ),
                away=MatchTeamResponse(
                    team_id=m.away.team_id,
                    team_name=m.away.team_name,
                    username=m.away.username,
                ),
                status=m.status,
                score_home=m.score_home,
                score_away=m.score_away,
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
    async def join_league(league_id: str, user_id: str, team_id: str) -> League:
        """Join a league with a team."""
        league = await League.get(league_id)
        if not league:
            raise LeagueNotFoundException(league_id)

        team = await UserTeam.get(team_id)
        if not team:
            raise TeamNotFoundException(team_id)

        if team.user_id != user_id:
            raise InvalidOperationException("Cannot join with another user's team")

        can_join, reason = league.can_join(team_id)
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
                ),
                away=MatchTeamInfo(
                    team_id=t2.team_id,
                    team_name=t2.team_name,
                    user_id=t2.user_id,
                    username=t2.username,
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
                        username=m.home.username,
                    ),
                    away=MatchTeamResponse(
                        team_id=m.away.team_id,
                        team_name=m.away.team_name,
                        username=m.away.username,
                    ),
                    status=m.status,
                    score_home=m.score_home,
                    score_away=m.score_away,
                    weather=m.weather,
                    events=[
                        MatchEventResponse(
                            id=e.id,
                            type=e.type,
                            team=e.team,
                            player_name=e.player_name,
                            victim_name=e.victim_name,
                            injury=e.injury,
                            half=e.half,
                            turn=e.turn,
                        )
                        for e in m.events
                    ],
                    mvp_home=m.mvp_home,
                    mvp_away=m.mvp_away,
                    gate=m.gate,
                    scheduled_at=m.scheduled_at,
                    played_at=m.played_at,
                )

        return None
