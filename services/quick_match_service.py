"""Service layer for quick (friendly) matches."""

import uuid
from datetime import datetime

from exceptions.exceptions import InvalidOperationException
from models.league.league import Match, MatchEvent, MatchStatus, MatchTeamInfo
from models.quick_match.quick_match import QuickMatch
from models.user.user import User
from models.user_team.team import UserTeam
from schemas.league import (
    AddMatchEventRequest,
    MatchDetail,
    MatchEventResponse,
    MatchTeamResponse,
    UpdateMatchStateRequest,
)
from schemas.quick_match import QuickMatchSummary
from utils.logging_config import setup_logger

logger = setup_logger(__name__)


class QuickMatchService:
    """Business logic for standalone quick matches."""

    # ── Helpers ────────────────────────────────────────────

    @staticmethod
    async def _get_qm(qm_id: str) -> QuickMatch:
        qm = await QuickMatch.get(qm_id)
        if not qm:
            raise InvalidOperationException(f"Quick match {qm_id} not found")
        return qm

    @staticmethod
    def _to_detail(qm: QuickMatch) -> MatchDetail:
        m = qm.match
        return MatchDetail(
            id=str(qm.id),
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
            home_ready=m.home_ready,
            away_ready=m.away_ready,
            home_squad=m.home_squad,
            away_squad=m.away_squad,
        )

    @staticmethod
    def _to_summary(qm: QuickMatch) -> QuickMatchSummary:
        m = qm.match
        return QuickMatchSummary(
            id=str(qm.id),
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
            created_at=str(qm.created_at) if qm.created_at else None,
            played_at=str(m.played_at) if m.played_at else None,
        )

    # ── CRUD ───────────────────────────────────────────────

    @staticmethod
    async def create_quick_match(
        user_id: str, home_team_id: str, away_team_id: str
    ) -> MatchDetail:
        """Create a new quick match between two user teams."""
        home_team = await UserTeam.get(home_team_id)
        away_team = await UserTeam.get(away_team_id)
        if not home_team:
            raise InvalidOperationException(f"Home team {home_team_id} not found")
        if not away_team:
            raise InvalidOperationException(f"Away team {away_team_id} not found")

        # Resolve usernames
        home_user = await User.get(home_team.user_id)
        away_user = await User.get(away_team.user_id)

        match = Match(
            id=uuid.uuid4().hex,
            round=1,
            home=MatchTeamInfo(
                team_id=str(home_team.id),
                team_name=home_team.name,
                user_id=home_team.user_id,
                username=home_user.username if home_user else "",
                base_roster_id=home_team.base_roster_id,
            ),
            away=MatchTeamInfo(
                team_id=str(away_team.id),
                team_name=away_team.name,
                user_id=away_team.user_id,
                username=away_user.username if away_user else "",
                base_roster_id=away_team.base_roster_id,
            ),
            status=MatchStatus.SCHEDULED,
        )

        qm = QuickMatch(owner_id=user_id, match=match)
        await qm.insert()
        logger.info(f"Quick match {qm.id} created by {user_id}")
        return QuickMatchService._to_detail(qm)

    @staticmethod
    async def list_quick_matches(user_id: str) -> list[QuickMatchSummary]:
        """List quick matches for a user (as owner or participant)."""
        all_qms = await QuickMatch.find({"owner_id": user_id}).to_list()
        return [QuickMatchService._to_summary(qm) for qm in all_qms]

    @staticmethod
    async def get_detail(qm_id: str) -> MatchDetail:
        qm = await QuickMatchService._get_qm(qm_id)
        return QuickMatchService._to_detail(qm)

    # ── Match lifecycle ────────────────────────────────────

    @staticmethod
    async def start_match(qm_id: str, user_id: str) -> MatchDetail:
        qm = await QuickMatchService._get_qm(qm_id)
        m = qm.match

        if m.status == MatchStatus.COMPLETED:
            raise InvalidOperationException("Match is already completed")
        if m.status == MatchStatus.IN_PROGRESS:
            raise InvalidOperationException("Match is already in progress")

        m.status = MatchStatus.IN_PROGRESS
        m.started_at = datetime.utcnow()
        m.current_half = 1
        m.current_turn = 1
        await qm.save()
        logger.info(f"Quick match {qm_id} started by {user_id}")
        return QuickMatchService._to_detail(qm)

    @staticmethod
    async def add_event(
        qm_id: str, user_id: str, request: AddMatchEventRequest
    ) -> MatchDetail:
        qm = await QuickMatchService._get_qm(qm_id)
        m = qm.match

        if m.status != MatchStatus.IN_PROGRESS:
            raise InvalidOperationException("Match is not in progress")

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
        m.events.append(event)

        if request.type == "touchdown":
            if request.team == "home":
                m.score_home += 1
            else:
                m.score_away += 1

        await qm.save()
        logger.info(f"Event '{request.type}' added to quick match {qm_id}")
        return QuickMatchService._to_detail(qm)

    @staticmethod
    async def delete_event(qm_id: str, event_id: str, user_id: str) -> MatchDetail:
        qm = await QuickMatchService._get_qm(qm_id)
        m = qm.match

        if m.status != MatchStatus.IN_PROGRESS:
            raise InvalidOperationException("Match is not in progress")

        event_to_remove = None
        for e in m.events:
            if e.id == event_id:
                event_to_remove = e
                break
        if not event_to_remove:
            raise InvalidOperationException(f"Event {event_id} not found")

        if event_to_remove.type == "touchdown":
            if event_to_remove.team == "home":
                m.score_home = max(0, m.score_home - 1)
            else:
                m.score_away = max(0, m.score_away - 1)

        m.events.remove(event_to_remove)
        await qm.save()
        logger.info(f"Event {event_id} removed from quick match {qm_id}")
        return QuickMatchService._to_detail(qm)

    @staticmethod
    async def update_state(
        qm_id: str, user_id: str, request: UpdateMatchStateRequest
    ) -> MatchDetail:
        qm = await QuickMatchService._get_qm(qm_id)
        m = qm.match

        # Allow weather/kickoff/ready before match starts (pre-match ceremony)
        _pre_match_only = (
            request.weather is not None
            or request.kickoff_event is not None
            or request.home_ready is not None
            or request.away_ready is not None
            or request.home_squad is not None
            or request.away_squad is not None
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
        if m.status != MatchStatus.IN_PROGRESS and not _pre_match_only:
            raise InvalidOperationException("Match is not in progress")

        user = await User.get(user_id)
        username = user.username if user else "unknown"

        def _evt(etype: str, detail: str, team: str = "system") -> MatchEvent:
            return MatchEvent(
                id=str(uuid.uuid4()),
                type=etype,
                team=team,
                detail=detail,
                half=m.current_half,
                turn=m.current_turn,
                timestamp=datetime.utcnow(),
                created_by=user_id,
                created_by_name=username,
            )

        if request.score_home is not None and request.score_home != m.score_home:
            old, new = m.score_home, request.score_home
            m.score_home = new
            m.events.append(_evt("score_change", f"Home score: {old} → {new}", "home"))
        if request.score_away is not None and request.score_away != m.score_away:
            old, new = m.score_away, request.score_away
            m.score_away = new
            m.events.append(_evt("score_change", f"Away score: {old} → {new}", "away"))
        if request.current_half is not None and request.current_half != m.current_half:
            old, new = m.current_half, request.current_half
            m.current_half = new
            m.events.append(_evt("half_change", f"Half: {old} → {new}"))
        if request.current_turn is not None and request.current_turn != m.current_turn:
            old, new = m.current_turn, request.current_turn
            m.current_turn = new
            m.events.append(_evt("turn_change", f"Turn: {old} → {new}"))
        if request.weather is not None and request.weather != m.weather:
            old = m.weather or "—"
            m.weather = request.weather
            m.events.append(
                _evt("weather_change", f"Weather: {old} → {request.weather}")
            )
        if (
            request.kickoff_event is not None
            and request.kickoff_event != m.kickoff_event
        ):
            old = m.kickoff_event or "—"
            m.kickoff_event = request.kickoff_event
            m.events.append(
                _evt("kickoff_change", f"Kickoff: {old} → {request.kickoff_event}")
            )
        if request.rerolls_used_home is not None:
            if request.rerolls_used_home != m.rerolls_used_home:
                old, new = m.rerolls_used_home, request.rerolls_used_home
                m.rerolls_used_home = new
                m.events.append(
                    _evt("reroll_change", f"Home rerolls used: {old} → {new}", "home")
                )
            else:
                m.rerolls_used_home = request.rerolls_used_home
        if request.rerolls_used_away is not None:
            if request.rerolls_used_away != m.rerolls_used_away:
                old, new = m.rerolls_used_away, request.rerolls_used_away
                m.rerolls_used_away = new
                m.events.append(
                    _evt("reroll_change", f"Away rerolls used: {old} → {new}", "away")
                )
            else:
                m.rerolls_used_away = request.rerolls_used_away
        if request.home_ready is not None:
            m.home_ready = request.home_ready
        if request.away_ready is not None:
            m.away_ready = request.away_ready
        if request.home_squad is not None:
            m.home_squad = request.home_squad
        if request.away_squad is not None:
            m.away_squad = request.away_squad
        if request.mvp_home is not None:
            m.mvp_home = request.mvp_home
        if request.mvp_away is not None:
            m.mvp_away = request.mvp_away
        if request.gate is not None:
            m.gate = request.gate

        await qm.save()
        logger.info(f"Quick match {qm_id} state updated by {user_id}")
        return QuickMatchService._to_detail(qm)

    @staticmethod
    async def complete_match(qm_id: str, user_id: str) -> MatchDetail:
        qm = await QuickMatchService._get_qm(qm_id)
        m = qm.match

        if m.status != MatchStatus.IN_PROGRESS:
            raise InvalidOperationException("Match is not in progress")

        m.status = MatchStatus.COMPLETED
        m.played_at = datetime.utcnow()
        await qm.save()
        logger.info(f"Quick match {qm_id} completed: {m.score_home}-{m.score_away}")
        return QuickMatchService._to_detail(qm)

    @staticmethod
    async def delete_quick_match(qm_id: str, user_id: str) -> None:
        qm = await QuickMatchService._get_qm(qm_id)
        if qm.owner_id != user_id:
            raise InvalidOperationException("Only the creator can delete this match")
        await qm.delete()
        logger.info(f"Quick match {qm_id} deleted by {user_id}")
