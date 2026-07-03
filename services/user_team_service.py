"""Service for user team operations."""

import logging
import random
import re
import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from exceptions.exceptions import (
    InvalidOperationException,
    PlayerNotFoundException,
    TeamNotFoundException,
)
from models.base.advancement import AdvancementRules
from models.base.inducement import InducementRules
from models.base.injury import InjuryRules
from models.base.roster import BasePlayer, BaseRoster
from models.base.star_player import StarPlayer
from models.league.league import League, LeagueStatus, Match, MatchStatus
from models.quick_match.quick_match import QuickMatch
from models.team.perk import Perk
from models.user.user import User
from models.user_team.team import (
    PlayerInjuryRecord,
    PlayerPerk,
    PlayerStats,
    PlayerStatus,
    TeamValueBreakdown,
    UserPlayer,
    UserTeam,
)
from schemas.user_team import (
    ApplyPlayerAdvancementRequest,
    CreateTeamRequest,
    HirePlayerRequest,
    HirePlayerResponse,
    HireStarPlayerRequest,
    PlayerCareerResponse,
    PlayerInjuryRecordResponse,
    PlayerPerkResponse,
    PlayerStatsResponse,
    TeamLeagueMembership,
    TeamValueBreakdownResponse,
    UpdatePlayerRequest,
    UpdateTeamRequest,
    UserPlayerResponse,
    UserTeamDetail,
    UserTeamSummary,
)
from utils.team_special_rules import (
    CHAOS_FAVOURED_LABELS,
    effective_special_rules,
    is_favoured_choice_valid,
    normalize_favoured_of,
    star_player_available_for_roster,
)

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class _MatchInducementBudgetSnapshot:
    petty_cash: int
    treasury_allowance: int
    total_available: int
    spent: int
    treasury_contribution: int
    remaining: int
    is_favorite: bool
    is_tied: bool


@dataclass(frozen=True)
class _TemporaryMatchTreasurySettlement:
    expected_contribution: int
    charged_contribution: int
    shortfall: int
    legacy_live_charge: int


class UserTeamService:
    """Service for managing user teams."""

    JOURNEYMAN_LONER_ID = "loner"
    JOURNEYMAN_LONER_PARAMETER = "4+"
    ELITE_SKILL_VALUE_BONUS = 10_000

    FAMILY_TO_SYMBOL = {
        "agility": "A",
        "devious": "D",
        "general": "G",
        "mutation": "M",
        "passing": "P",
        "strength": "S",
    }

    # ============== Team Operations ==============

    @staticmethod
    async def _is_in_active_league(team_id: str) -> bool:
        league = await League.find_one(
            {"status": LeagueStatus.ACTIVE.value, "teams.team_id": team_id}
        )
        return league is not None

    @staticmethod
    async def _is_in_league(team_id: str) -> bool:
        league = await League.find_one({"teams.team_id": team_id})
        return league is not None

    @staticmethod
    def _is_league_commissioner(league: League, user_id: str) -> bool:
        return user_id == league.owner_id or user_id in (league.commissioner_ids or [])

    @staticmethod
    async def _calculate_team_value(
        team: UserTeam, roster: Optional[BaseRoster] = None
    ) -> int:
        return (
            await UserTeamService._calculate_team_value_breakdown(team, roster)
        ).team_value

    @staticmethod
    async def _calculate_team_value_breakdown(
        team: UserTeam, roster: Optional[BaseRoster] = None
    ) -> TeamValueBreakdown:
        if roster is None:
            roster = await BaseRoster.find_one(BaseRoster.id == team.base_roster_id)

        reroll_cost = roster.reroll_cost if roster else 0
        ignored_player_types = {
            player.type
            for player in (roster.players if roster else [])
            if any("low cost linemen" in rule.lower() for rule in roster.special_rules)
            and player.position.lower() == "lineman"
        }
        return team.calculate_team_value_breakdown(
            reroll_cost=reroll_cost,
            ignored_player_types=ignored_player_types,
        )

    @staticmethod
    def _normalize_inducement_rule(value: str) -> str:
        return " ".join(
            re.sub(r"[^a-z0-9]+", " ", value.lower().replace("&", "and")).split()
        )

    @staticmethod
    def _team_has_inducement_rule(
        roster: BaseRoster, team: UserTeam, rule: str
    ) -> bool:
        required = UserTeamService._normalize_inducement_rule(rule)
        special_rules = effective_special_rules(
            roster.special_rules,
            team.base_roster_id,
            team.favoured_of,
        )
        for current_rule in special_rules:
            normalized = UserTeamService._normalize_inducement_rule(current_rule)
            if (
                normalized == required
                or normalized in required
                or required in normalized
            ):
                return True
        return False

    @staticmethod
    def _inducement_cost_option_specificity(applies_to: str) -> int:
        if applies_to == "any":
            return 0
        if applies_to.startswith("roster:") or applies_to.startswith("special_rule:"):
            return 2
        return 1

    @staticmethod
    def _inducement_cost_option_applies(
        option, team: UserTeam, roster: BaseRoster
    ) -> bool:
        applies_to = option.applies_to
        if applies_to == "any":
            return True
        if applies_to.startswith("special_rule:"):
            return UserTeamService._team_has_inducement_rule(
                roster,
                team,
                applies_to.removeprefix("special_rule:"),
            )
        if applies_to.startswith("roster:"):
            roster_id = UserTeamService._normalize_inducement_rule(
                applies_to.removeprefix("roster:")
            )
            return (
                UserTeamService._normalize_inducement_rule(team.base_roster_id)
                == roster_id
                or UserTeamService._normalize_inducement_rule(roster.id) == roster_id
            )
        return False

    @staticmethod
    def _resolve_inducement_cost(
        rule, team: UserTeam, roster: BaseRoster
    ) -> Optional[int]:
        if not rule.cost_options:
            return rule.cost

        applicable = [
            option
            for option in rule.cost_options
            if UserTeamService._inducement_cost_option_applies(option, team, roster)
        ]
        if not applicable:
            return rule.cost

        applicable.sort(
            key=lambda option: (
                -UserTeamService._inducement_cost_option_specificity(option.applies_to),
                option.cost,
            )
        )
        return applicable[0].cost

    @staticmethod
    def _temporary_match_hire_spend(team: UserTeam, match_id: str) -> int:
        total = 0
        for player in team.players:
            if not player.temporary_for_match or player.temporary_match_id != match_id:
                continue
            if player.base_type.startswith("star_") or not player.journeyman:
                total += player.current_value
        return total

    @staticmethod
    def _match_inducement_team_value(
        team: UserTeam,
        roster: BaseRoster,
        match_id: str,
    ) -> int:
        ignored_player_types = {
            player.type
            for player in roster.players
            if any("low cost linemen" in rule.lower() for rule in roster.special_rules)
            and player.position.lower() == "lineman"
        }
        player_value = 0
        unavailable_player_value = 0
        for player in team.players:
            status = (
                player.status.value
                if hasattr(player.status, "value")
                else player.status
            )
            if status == PlayerStatus.DEAD.value:
                continue
            if player.temporary_for_match and player.temporary_match_id == match_id:
                continue
            if player.base_type in ignored_player_types:
                continue
            player_value += player.current_value
            if status != PlayerStatus.HEALTHY.value:
                unavailable_player_value += player.current_value

        reroll_value = team.rerolls * roster.reroll_cost
        assistant_coach_value = team.assistant_coaches * 10_000
        cheerleader_value = team.cheerleaders * 10_000
        apothecary_value = 50_000 if team.apothecary else 0
        team_value = (
            player_value
            + reroll_value
            + assistant_coach_value
            + cheerleader_value
            + apothecary_value
        )
        return max(0, team_value - unavailable_player_value)

    @staticmethod
    def _inducement_purchase_spend(
        team: UserTeam,
        roster: BaseRoster,
        purchases: dict[str, int],
        rules: Optional[InducementRules],
    ) -> int:
        if not rules or not purchases:
            return 0

        total = 0
        rule_by_id = {rule.id: rule for rule in rules.inducements}
        for rule_id, count in purchases.items():
            if count <= 0:
                continue
            rule = rule_by_id.get(rule_id)
            if not rule:
                continue
            cost = UserTeamService._resolve_inducement_cost(rule, team, roster)
            if cost is not None:
                total += cost * count
        return total

    @staticmethod
    def _treasury_contribution_for_match_spend(
        spent: int,
        petty_cash: int,
        treasury_allowance: int,
        *,
        is_favorite: bool,
    ) -> int:
        if spent <= 0:
            return 0
        if is_favorite:
            return spent
        excess = spent - petty_cash
        if excess <= 0:
            return 0
        return excess if excess <= treasury_allowance else treasury_allowance

    @staticmethod
    async def _match_inducement_budget_for_team(
        team: UserTeam,
        *,
        league_id: str,
        match_id: str,
    ) -> _MatchInducementBudgetSnapshot:
        team_id = str(team.id)
        league = await League.get(league_id)
        if not league:
            raise InvalidOperationException(f"League '{league_id}' not found")

        match = next((item for item in league.matches if item.id == match_id), None)
        if not match:
            raise InvalidOperationException(f"Match '{match_id}' not found")

        if team_id not in {match.home.team_id, match.away.team_id}:
            raise InvalidOperationException("Team is not part of the specified match")

        home_team = await UserTeam.get(match.home.team_id)
        if not home_team:
            raise TeamNotFoundException(match.home.team_id)
        away_team = await UserTeam.get(match.away.team_id)
        if not away_team:
            raise TeamNotFoundException(match.away.team_id)

        home_roster = await BaseRoster.find_one(
            BaseRoster.id == home_team.base_roster_id
        )
        if not home_roster:
            raise InvalidOperationException("Home team roster not found")
        away_roster = await BaseRoster.find_one(
            BaseRoster.id == away_team.base_roster_id
        )
        if not away_roster:
            raise InvalidOperationException("Away team roster not found")

        rules = await InducementRules.get("inducements")
        return UserTeamService._match_inducement_budget_for_state(
            team_id=team_id,
            league=league,
            match=match,
            home_team=home_team,
            away_team=away_team,
            home_roster=home_roster,
            away_roster=away_roster,
            rules=rules,
        )

    @staticmethod
    def _match_inducement_budget_for_state(
        *,
        team_id: str,
        league: League,
        match: Match,
        home_team: UserTeam,
        away_team: UserTeam,
        home_roster: BaseRoster,
        away_roster: BaseRoster,
        rules: Optional[InducementRules],
    ) -> _MatchInducementBudgetSnapshot:
        home_ctv = UserTeamService._match_inducement_team_value(
            home_team,
            home_roster,
            match.id,
        )
        away_ctv = UserTeamService._match_inducement_team_value(
            away_team,
            away_roster,
            match.id,
        )
        home_spent = UserTeamService._temporary_match_hire_spend(
            home_team,
            match.id,
        ) + UserTeamService._inducement_purchase_spend(
            home_team,
            home_roster,
            match.home_inducement_purchases,
            rules,
        )
        away_spent = UserTeamService._temporary_match_hire_spend(
            away_team,
            match.id,
        ) + UserTeamService._inducement_purchase_spend(
            away_team,
            away_roster,
            match.away_inducement_purchases,
            rules,
        )

        selected_is_home = team_id == match.home.team_id
        selected_team = home_team if selected_is_home else away_team
        selected_ctv = home_ctv if selected_is_home else away_ctv
        opponent_ctv = away_ctv if selected_is_home else home_ctv
        selected_spent = home_spent if selected_is_home else away_spent
        inducements_allowed = league.rules.inducements if league.rules else True

        if not inducements_allowed or home_ctv == away_ctv:
            return _MatchInducementBudgetSnapshot(
                petty_cash=0,
                treasury_allowance=0,
                total_available=0,
                spent=selected_spent,
                treasury_contribution=0,
                remaining=0,
                is_favorite=False,
                is_tied=True,
            )

        home_is_favorite = home_ctv > away_ctv
        selected_is_favorite = selected_is_home == home_is_favorite

        if selected_is_favorite:
            total_available = selected_team.treasury
            remaining = total_available - selected_spent
            return _MatchInducementBudgetSnapshot(
                petty_cash=0,
                treasury_allowance=total_available,
                total_available=total_available,
                spent=selected_spent,
                treasury_contribution=selected_spent,
                remaining=remaining if remaining > 0 else 0,
                is_favorite=True,
                is_tied=False,
            )

        ctv_difference = abs(home_ctv - away_ctv)
        favorite_spent = home_spent if home_is_favorite else away_spent
        petty_cash = ctv_difference + favorite_spent
        treasury_allowance = (
            min(selected_team.treasury, 50_000) if selected_team.treasury > 0 else 0
        )
        treasury_contribution = UserTeamService._treasury_contribution_for_match_spend(
            selected_spent,
            petty_cash,
            treasury_allowance,
            is_favorite=False,
        )
        total_available = petty_cash + treasury_allowance
        remaining = total_available - selected_spent
        return _MatchInducementBudgetSnapshot(
            petty_cash=petty_cash,
            treasury_allowance=treasury_allowance,
            total_available=total_available,
            spent=selected_spent,
            treasury_contribution=treasury_contribution,
            remaining=remaining if remaining > 0 else 0,
            is_favorite=False,
            is_tied=False,
        )

    @staticmethod
    async def _temporary_match_treasury_charge(
        team: UserTeam,
        *,
        league_id: Optional[str],
        match_id: Optional[str],
        cost: int,
    ) -> int:
        if cost <= 0:
            return 0
        if not league_id or not match_id:
            if team.treasury < cost:
                raise InvalidOperationException(
                    "Insufficient treasury "
                    "[source=user_team_service.temporary_match_treasury_charge.direct] "
                    f"({team.treasury} < {cost})"
                )
            return cost

        budget = await UserTeamService._match_inducement_budget_for_team(
            team,
            league_id=league_id,
            match_id=match_id,
        )
        if budget.remaining < cost:
            raise InvalidOperationException(
                f"Insufficient inducement funds ({budget.remaining} < {cost})"
            )

        return 0

    @staticmethod
    async def _temporary_match_treasury_contribution(
        team: UserTeam,
        *,
        league_id: str,
        match_id: str,
    ) -> int:
        settlement = await UserTeamService._temporary_match_treasury_settlement(
            team,
            league_id=league_id,
            match_id=match_id,
            allow_shortfall=False,
        )
        return settlement.charged_contribution

    @staticmethod
    async def _temporary_match_treasury_settlement(
        team: UserTeam,
        *,
        league_id: str,
        match_id: str,
        allow_shortfall: bool,
    ) -> _TemporaryMatchTreasurySettlement:
        budget = await UserTeamService._match_inducement_budget_for_team(
            team,
            league_id=league_id,
            match_id=match_id,
        )
        contribution = budget.treasury_contribution
        if contribution <= 0:
            return 0
        legacy_live_charge = UserTeamService._temporary_match_hire_spend(
            team,
            match_id,
        )
        if legacy_live_charge > 0:
            contribution = max(contribution - legacy_live_charge, 0)
        if contribution <= 0:
            return _TemporaryMatchTreasurySettlement(
                expected_contribution=0,
                charged_contribution=0,
                shortfall=0,
                legacy_live_charge=legacy_live_charge,
            )
        if allow_shortfall:
            charged = min(team.treasury, contribution)
            return _TemporaryMatchTreasurySettlement(
                expected_contribution=contribution,
                charged_contribution=charged,
                shortfall=contribution - charged,
                legacy_live_charge=legacy_live_charge,
            )
        if team.treasury < contribution:
            raise InvalidOperationException(
                "Insufficient treasury "
                "[source=user_team_service.temporary_match_treasury_contribution] "
                f"({team.treasury} < {contribution}; match_id={match_id}; "
                f"legacy_live_charge={legacy_live_charge})"
            )
        return _TemporaryMatchTreasurySettlement(
            expected_contribution=contribution,
            charged_contribution=contribution,
            shortfall=0,
            legacy_live_charge=legacy_live_charge,
        )

    @staticmethod
    async def _pending_match_treasury_reservation(
        team: UserTeam,
        *,
        league_id: Optional[str],
    ) -> int:
        if not league_id:
            return 0

        league = await League.get(league_id)
        if not league:
            return 0

        team_id = str(team.id)
        reservation = 0
        for match in league.matches:
            if team_id not in {match.home.team_id, match.away.team_id}:
                continue
            if match.aftermatch_spp_applied_at is not None:
                continue

            match_status = match.status.value if hasattr(match.status, "value") else str(match.status)
            if match_status not in {
                MatchStatus.IN_PROGRESS.value,
                MatchStatus.COMPLETED.value,
            }:
                continue

            budget = await UserTeamService._match_inducement_budget_for_team(
                team,
                league_id=league_id,
                match_id=match.id,
            )
            reservation += budget.treasury_contribution

        return reservation

    @staticmethod
    async def _available_treasury_for_team_management(
        team: UserTeam,
        *,
        league_id: Optional[str],
    ) -> int:
        reserved = await UserTeamService._pending_match_treasury_reservation(
            team,
            league_id=league_id,
        )
        available = team.treasury - reserved
        return available if available > 0 else 0

    @staticmethod
    def _eligible_player_count(team: UserTeam) -> int:
        """Count players able to play the next game."""
        return sum(
            1
            for player in team.players
            if (
                player.status.value
                if hasattr(player.status, "value")
                else player.status
            )
            == "healthy"
        )

    @staticmethod
    def _available_player_count_by_type(team: UserTeam, base_type: str) -> int:
        """Count players of a type able to play the next game."""
        return sum(
            1
            for player in team.players
            if player.base_type == base_type
            and (
                player.status.value
                if hasattr(player.status, "value")
                else player.status
            )
            == "healthy"
        )

    @staticmethod
    async def _calculate_current_team_value(
        team: UserTeam, roster: Optional[BaseRoster] = None
    ) -> int:
        return (
            await UserTeamService._calculate_team_value_breakdown(team, roster)
        ).current_team_value

    @staticmethod
    async def _sync_team_value(
        team: UserTeam, roster: Optional[BaseRoster] = None
    ) -> int:
        normalized = False
        if team.cheerleaders > 6:
            team.cheerleaders = 6
            normalized = True
        if team.assistant_coaches > 6:
            team.assistant_coaches = 6
            normalized = True
        if team.dedicated_fans < 1:
            team.dedicated_fans = 1
            normalized = True
        if team.dedicated_fans > 7:
            team.dedicated_fans = 7
            normalized = True

        breakdown = await UserTeamService._calculate_team_value_breakdown(team, roster)
        if normalized or team.team_value != breakdown.team_value:
            team.team_value = breakdown.team_value
            team.updated_at = datetime.utcnow()
            await team.save()
        return breakdown.team_value

    @staticmethod
    async def _league_memberships_by_team_ids(
        team_ids: list[str],
    ) -> dict[str, list[TeamLeagueMembership]]:
        memberships: dict[str, list[TeamLeagueMembership]] = {
            team_id: [] for team_id in team_ids
        }
        if not team_ids:
            return memberships

        leagues = await League.find({"teams.team_id": {"$in": team_ids}}).to_list()
        team_id_set = set(team_ids)
        for league in leagues:
            membership = TeamLeagueMembership(
                id=str(league.id),
                name=league.name,
                status=(
                    league.status.value
                    if hasattr(league.status, "value")
                    else league.status
                ),
                season=league.season,
            )
            for team in league.teams:
                if team.team_id in team_id_set:
                    memberships.setdefault(team.team_id, []).append(membership)

        return memberships

    @staticmethod
    async def _league_memberships(team_id: str) -> list[TeamLeagueMembership]:
        return (await UserTeamService._league_memberships_by_team_ids([team_id])).get(
            team_id, []
        )

    @staticmethod
    async def _ensure_share_code(team: UserTeam) -> str:
        share_code = getattr(team, "share_code", None)
        if share_code:
            normalized = str(share_code).upper()
            if normalized != share_code:
                team.share_code = normalized
                team.updated_at = datetime.utcnow()
                await team.save()
            return normalized

        legacy_candidate = str(team.id).replace("-", "")[:8].upper()
        if len(legacy_candidate) == 8:
            existing = await UserTeam.find_one(UserTeam.share_code == legacy_candidate)
            if not existing or str(existing.id) == str(team.id):
                team.share_code = legacy_candidate
                team.updated_at = datetime.utcnow()
                await team.save()
                return legacy_candidate

        while True:
            candidate = uuid.uuid4().hex[:8].upper()
            existing = await UserTeam.find_one(UserTeam.share_code == candidate)
            if not existing:
                team.share_code = candidate
                team.updated_at = datetime.utcnow()
                await team.save()
                return candidate

    @staticmethod
    async def _ensure_roster_can_be_managed(team_id: str) -> None:
        if await UserTeamService._is_in_active_league(team_id):
            raise InvalidOperationException(
                "Team roster cannot be changed while registered in an active league"
            )

    @staticmethod
    async def _ensure_team_can_be_deleted(team_id: str) -> None:
        league = await League.find_one({"teams.team_id": team_id})
        if league:
            raise InvalidOperationException(
                "Team cannot be deleted while registered in a league"
            )

    @staticmethod
    def _validate_favoured_of(
        roster_id: str, favoured_of: Optional[str]
    ) -> Optional[str]:
        normalized = normalize_favoured_of(favoured_of)
        if not is_favoured_choice_valid(roster_id, normalized):
            allowed = ", ".join(CHAOS_FAVOURED_LABELS.keys())
            raise InvalidOperationException(
                f"Invalid favoured_of for roster '{roster_id}'. Allowed: {allowed}"
            )
        return normalized

    @staticmethod
    async def create_team(user_id: str, request: CreateTeamRequest) -> UserTeam:
        """Create a new team for a user."""
        # Verify roster exists
        roster = await BaseRoster.find_one(BaseRoster.id == request.base_roster_id)
        if not roster:
            raise InvalidOperationException(
                f"Roster '{request.base_roster_id}' not found"
            )

        favoured_of = UserTeamService._validate_favoured_of(
            request.base_roster_id, request.favoured_of
        )

        team = UserTeam(
            user_id=user_id,
            base_roster_id=request.base_roster_id,
            name=request.name,
            favoured_of=favoured_of,
            treasury=1_000_000,
            team_value=0,
            players=[],
            icon=roster.icon,
            wallpaper=roster.wallpaper,
        )

        cost_delta = 0
        for player_request in request.players:
            base_player = UserTeamService._find_base_player(
                roster, player_request.base_type
            )
            can_hire, reason = team.can_hire_player(
                base_type=player_request.base_type,
                max_allowed=base_player.max,
                cost=base_player.cost,
            )
            if not can_hire:
                raise InvalidOperationException(reason)

            new_player = UserTeamService._build_user_player(
                team=team,
                base_player=base_player,
                base_type=player_request.base_type,
                name=player_request.name,
                number=player_request.number,
            )
            team.players.append(new_player)
            team.treasury -= base_player.cost

        if request.rerolls:
            cost_delta += request.rerolls * roster.reroll_cost
        if request.cheerleaders:
            cost_delta += request.cheerleaders * 10000
        if request.assistant_coaches:
            cost_delta += request.assistant_coaches * 10000
        if request.apothecary:
            if not roster.apothecary_allowed:
                raise InvalidOperationException("Apothecary is not allowed")
            cost_delta += 50000
        cost_delta += (request.dedicated_fans - 1) * 5000

        if cost_delta > team.treasury:
            raise InvalidOperationException("Not enough treasury")

        team.rerolls = request.rerolls
        team.cheerleaders = request.cheerleaders
        team.assistant_coaches = request.assistant_coaches
        team.apothecary = request.apothecary
        team.dedicated_fans = request.dedicated_fans
        team.treasury -= cost_delta
        team.team_value = await UserTeamService._calculate_team_value(team, roster)

        await team.insert()

        # Update user's team list
        user = await User.find_one(User.id == user_id)
        if user:
            user.team_ids.append(str(team.id))
            await user.save()

        logger.info(f"Created team '{team.name}' for user {user_id}")
        return team

    @staticmethod
    async def get_team_by_id(team_id: str) -> Optional[UserTeam]:
        """Get a team by ID."""
        return await UserTeam.get(team_id)

    @staticmethod
    async def get_teams_by_user(user_id: str) -> list[UserTeamSummary]:
        """Get all teams owned by a user."""
        teams = await UserTeam.find(UserTeam.user_id == user_id).to_list()
        team_ids = [str(team.id) for team in teams]
        memberships = await UserTeamService._league_memberships_by_team_ids(team_ids)

        summaries: list[UserTeamSummary] = []
        for t in teams:
            team_id = str(t.id)
            roster = await BaseRoster.find_one(BaseRoster.id == t.base_roster_id)
            await UserTeamService._sync_team_value(t, roster)
            value_breakdown = await UserTeamService._calculate_team_value_breakdown(
                t, roster
            )
            share_code = await UserTeamService._ensure_share_code(t)
            summaries.append(
                UserTeamSummary(
                    id=str(t.id),
                    name=t.name,
                    base_roster_id=t.base_roster_id,
                    team_value=value_breakdown.team_value,
                    current_team_value=value_breakdown.current_team_value,
                    treasury=t.treasury,
                    player_count=len(t.players),
                    can_manage_roster=not await UserTeamService._is_in_active_league(
                        team_id
                    ),
                    share_code=share_code,
                    favoured_of=t.favoured_of,
                    special_rules=effective_special_rules(
                        roster.special_rules if roster else [],
                        t.base_roster_id,
                        t.favoured_of,
                    ),
                    league_memberships=memberships.get(team_id, []),
                    icon=t.icon,
                    created_at=t.created_at,
                )
            )
        return summaries

    @staticmethod
    async def _require_team_owner(team_id: str, user_id: str) -> UserTeam:
        """Return the team only if it belongs to the current user."""
        team = await UserTeam.get(team_id)
        if not team:
            raise TeamNotFoundException(team_id)
        if team.user_id != user_id:
            raise InvalidOperationException("Cannot access another user's team")
        return team

    @staticmethod
    async def _can_access_team_via_league_match(
        team_id: str,
        user_id: str,
        league_id: Optional[str],
        match_id: Optional[str],
    ) -> bool:
        if not league_id or not match_id:
            return False

        league = await League.get(league_id)
        if not league:
            return False

        match = next(
            (candidate for candidate in league.matches if candidate.id == match_id),
            None,
        )
        if not match:
            return False

        if team_id not in {match.home.team_id, match.away.team_id}:
            return False

        return (
            UserTeamService._is_league_commissioner(league, user_id)
            or match.home.user_id == user_id
            or match.away.user_id == user_id
        )

    @staticmethod
    async def _can_access_team_via_league_membership(
        team_id: str,
        user_id: str,
        league_id: Optional[str],
    ) -> bool:
        if not league_id:
            return False

        league = await League.get(league_id)
        if not league or not UserTeamService._is_league_commissioner(league, user_id):
            return False

        return any(participant.team_id == team_id for participant in league.teams)

    @staticmethod
    async def _has_commissioner_team_access(
        team_id: str,
        user_id: str,
        league_id: Optional[str],
    ) -> bool:
        return await UserTeamService._can_access_team_via_league_membership(
            team_id,
            user_id,
            league_id,
        )

    @staticmethod
    async def _can_access_team_via_quick_match(
        team_id: str,
        user_id: str,
        quick_match_id: Optional[str],
    ) -> bool:
        if not quick_match_id:
            return False

        quick_match = await QuickMatch.get(quick_match_id)
        if not quick_match:
            return False

        match = quick_match.match
        if team_id not in {match.home.team_id, match.away.team_id}:
            return False

        return (
            quick_match.owner_id == user_id
            or match.home.user_id == user_id
            or match.away.user_id == user_id
        )

    @staticmethod
    async def _can_access_team_in_match_context(
        team_id: str,
        user_id: str,
        *,
        league_id: Optional[str] = None,
        match_id: Optional[str] = None,
        quick_match_id: Optional[str] = None,
    ) -> bool:
        if await UserTeamService._can_access_team_via_league_membership(
            team_id,
            user_id,
            league_id,
        ):
            return True
        if await UserTeamService._can_access_team_via_league_match(
            team_id,
            user_id,
            league_id,
            match_id,
        ):
            return True
        return await UserTeamService._can_access_team_via_quick_match(
            team_id,
            user_id,
            quick_match_id,
        )

    @staticmethod
    async def _require_team_owner_or_match_access(
        team_id: str,
        user_id: str,
        *,
        league_id: Optional[str] = None,
        match_id: Optional[str] = None,
        quick_match_id: Optional[str] = None,
    ) -> UserTeam:
        team = await UserTeam.get(team_id)
        if not team:
            raise TeamNotFoundException(team_id)
        if team.user_id == user_id:
            return team
        if await UserTeamService._can_access_team_in_match_context(
            team_id,
            user_id,
            league_id=league_id,
            match_id=match_id,
            quick_match_id=quick_match_id,
        ):
            return team
        raise InvalidOperationException("Cannot access another user's team")

    @staticmethod
    async def get_team_detail(
        team_id: str,
        *,
        hide_notes: bool = False,
        viewer_id: Optional[str] = None,
        league_id: Optional[str] = None,
        match_id: Optional[str] = None,
        quick_match_id: Optional[str] = None,
    ) -> Optional[UserTeamDetail]:
        """Get full team detail with players."""
        team = await UserTeam.get(team_id)
        if not team:
            return None

        if viewer_id is not None and team.user_id != viewer_id:
            commissioner_access = await UserTeamService._has_commissioner_team_access(
                team_id,
                viewer_id,
                league_id,
            )
            if (
                not commissioner_access
                and not await UserTeamService._can_access_team_in_match_context(
                    team_id,
                    viewer_id,
                    league_id=league_id,
                    match_id=match_id,
                    quick_match_id=quick_match_id,
                )
            ):
                raise InvalidOperationException("Cannot access another user's team")
            hide_notes = not commissioner_access

        return await UserTeamService._team_to_detail(team, hide_notes=hide_notes)

    @staticmethod
    async def get_team_detail_by_share_code(
        share_code: str,
    ) -> Optional[UserTeamDetail]:
        """Get public team detail by share code without private notes."""
        normalized = share_code.strip().upper()
        team = await UserTeam.find_one({"share_code": normalized})
        if not team:
            team = await UserTeam.find_one({"share_code": share_code.strip()})
        if not team and len(normalized) == 8:
            teams = await UserTeam.find_all().to_list()
            matches = [
                candidate
                for candidate in teams
                if str(candidate.id).replace("-", "").upper().startswith(normalized)
            ]
            if len(matches) == 1:
                team = matches[0]
                team.share_code = normalized
                team.updated_at = datetime.utcnow()
                await team.save()
        if not team:
            return None

        return await UserTeamService._team_to_detail(team, hide_notes=True)

    @staticmethod
    async def _team_to_detail(
        team: UserTeam, *, hide_notes: bool = False
    ) -> UserTeamDetail:
        team_id = str(team.id)

        roster = await BaseRoster.find_one(BaseRoster.id == team.base_roster_id)
        await UserTeamService._sync_team_value(team, roster)
        value_breakdown = await UserTeamService._calculate_team_value_breakdown(
            team, roster
        )

        players = [UserTeamService._player_to_response(p) for p in team.players]
        share_code = await UserTeamService._ensure_share_code(team)

        return UserTeamDetail(
            id=str(team.id),
            user_id=team.user_id,
            base_roster_id=team.base_roster_id,
            name=team.name,
            players=players,
            treasury=team.treasury,
            team_value=value_breakdown.team_value,
            current_team_value=value_breakdown.current_team_value,
            team_value_breakdown=TeamValueBreakdownResponse(
                **value_breakdown.model_dump()
            ),
            rerolls=team.rerolls,
            reroll_cost=roster.reroll_cost if roster else 0,
            fan_factor=team.fan_factor,
            cheerleaders=team.cheerleaders,
            assistant_coaches=team.assistant_coaches,
            apothecary=team.apothecary,
            apothecary_allowed=roster.apothecary_allowed if roster else True,
            dedicated_fans=team.dedicated_fans,
            notes="" if hide_notes else team.notes,
            share_code=share_code,
            can_manage_roster=not await UserTeamService._is_in_active_league(team_id),
            favoured_of=team.favoured_of,
            special_rules=effective_special_rules(
                roster.special_rules if roster else [],
                team.base_roster_id,
                team.favoured_of,
            ),
            league_memberships=await UserTeamService._league_memberships(team_id),
            icon=team.icon,
            wallpaper=team.wallpaper,
            created_at=team.created_at,
            updated_at=team.updated_at,
        )

    @staticmethod
    async def update_team(
        team_id: str, user_id: str, request: UpdateTeamRequest
    ) -> UserTeam:
        """Update team settings."""
        commissioner_mode = bool(request.commissioner_edit)

        if commissioner_mode:
            if not request.league_id:
                raise InvalidOperationException(
                    "League context is required for commissioner edits"
                )
            team = await UserTeam.get(team_id)
            if not team:
                raise TeamNotFoundException(team_id)
            if not await UserTeamService._can_access_team_via_league_membership(
                team_id,
                user_id,
                request.league_id,
            ):
                raise InvalidOperationException("Cannot access another user's team")
        else:
            team = await UserTeamService._require_team_owner_or_match_access(
                team_id,
                user_id,
                league_id=request.league_id,
            )

        if request.name is not None and not commissioner_mode:
            await UserTeamService._ensure_roster_can_be_managed(team_id)

        # Load base roster for costs
        roster = await BaseRoster.find_one(BaseRoster.id == team.base_roster_id)
        reroll_cost = roster.reroll_cost if roster else 60000
        reroll_purchase_cost = reroll_cost
        if not commissioner_mode:
            reroll_purchase_cost = (
                reroll_cost * 2
                if await UserTeamService._is_in_league(team_id)
                else reroll_cost
            )

        # Calculate treasury delta for normal coach-side staff changes.
        cost_delta = 0
        if not commissioner_mode:
            if request.rerolls is not None:
                diff = request.rerolls - team.rerolls
                cost_delta += diff * (reroll_purchase_cost if diff > 0 else reroll_cost)
            if request.cheerleaders is not None:
                diff = request.cheerleaders - team.cheerleaders
                cost_delta += diff * 10000
            if request.assistant_coaches is not None:
                diff = request.assistant_coaches - team.assistant_coaches
                cost_delta += diff * 10000
            if request.apothecary is not None:
                if request.apothecary and not team.apothecary:
                    if roster and not roster.apothecary_allowed:
                        raise InvalidOperationException("Apothecary is not allowed")
                    cost_delta += 50000
                elif not request.apothecary and team.apothecary:
                    cost_delta -= 50000
        elif request.apothecary and roster and not roster.apothecary_allowed:
            raise InvalidOperationException("Apothecary is not allowed")

        # Validate treasury
        if cost_delta > 0:
            available_treasury = (
                await UserTeamService._available_treasury_for_team_management(
                    team,
                    league_id=request.league_id,
                )
            )
            if available_treasury < cost_delta:
                raise InvalidOperationException("Not enough treasury")

        if request.name is not None:
            team.name = request.name
        if request.rerolls is not None:
            team.rerolls = request.rerolls
        if request.cheerleaders is not None:
            team.cheerleaders = request.cheerleaders
        if request.assistant_coaches is not None:
            team.assistant_coaches = request.assistant_coaches
        if request.apothecary is not None:
            team.apothecary = request.apothecary
        if request.fan_factor is not None:
            team.fan_factor = request.fan_factor
        if request.dedicated_fans is not None:
            if not commissioner_mode and not await UserTeamService._is_in_league(
                team_id
            ):
                raise InvalidOperationException(
                    "Dedicated fans can only change during league play"
                )
            team.dedicated_fans = request.dedicated_fans
        if request.treasury is not None:
            team.treasury = request.treasury
        if request.notes is not None:
            team.notes = request.notes
        if "favoured_of" in request.model_fields_set:
            team.favoured_of = UserTeamService._validate_favoured_of(
                team.base_roster_id, request.favoured_of
            )

        if not commissioner_mode:
            team.treasury -= cost_delta
        team.team_value = await UserTeamService._calculate_team_value(team, roster)
        team.updated_at = datetime.utcnow()
        await team.save()

        return team

    @staticmethod
    async def delete_team(team_id: str, user_id: str) -> bool:
        """Delete a team."""
        team = await UserTeam.get(team_id)
        if not team:
            return False

        if team.user_id != user_id:
            raise InvalidOperationException("Cannot delete another user's team")

        await UserTeamService._ensure_team_can_be_deleted(team_id)

        await team.delete()

        # Remove from user's team list
        user = await User.find_one(User.id == user_id)
        if user and team_id in user.team_ids:
            user.team_ids.remove(team_id)
            await user.save()

        logger.info(f"Deleted team {team_id}")
        return True

    # ============== Player Operations ==============

    @staticmethod
    async def hire_player(
        team_id: str, user_id: str, request: HirePlayerRequest
    ) -> HirePlayerResponse:
        """Hire a new player for a team.

        Player hiring is allowed for teams registered in active leagues; other
        roster management actions remain locked by _ensure_roster_can_be_managed.
        """
        team = await UserTeamService._require_team_owner_or_match_access(
            team_id,
            user_id,
            league_id=request.league_id,
        )

        # Get base roster and player type
        roster = await BaseRoster.find_one(BaseRoster.id == team.base_roster_id)
        if not roster:
            raise InvalidOperationException("Team roster not found")

        base_player = UserTeamService._find_base_player(roster, request.base_type)
        treasury_charge = 0

        if request.temporary_for_match:
            if request.mercenary:
                current_available = UserTeamService._available_player_count_by_type(
                    team, request.base_type
                )
                if current_available >= base_player.max:
                    raise InvalidOperationException(
                        f"Maximum available {request.base_type} reached ({base_player.max})"
                    )
                mercenary_cost = base_player.cost + 30_000
                treasury_charge = (
                    await UserTeamService._temporary_match_treasury_charge(
                        team,
                        league_id=request.league_id,
                        match_id=request.temporary_match_id,
                        cost=mercenary_cost,
                    )
                )
            else:
                if base_player.position.lower() != "lineman":
                    raise InvalidOperationException(
                        "Journeymen must be Lineman players"
                    )
                if request.riotous_rookie and not any(
                    "low cost linemen" in rule.lower() for rule in roster.special_rules
                ):
                    raise InvalidOperationException(
                        "Riotous Rookies requires Low Cost Linemen"
                    )
                if (
                    not request.riotous_rookie
                    and UserTeamService._eligible_player_count(team) >= 11
                ):
                    raise InvalidOperationException(
                        "Journeymen cannot take eligible players above 11"
                    )
        else:
            # Validate permanent hiring
            can_hire, reason = team.can_hire_player(
                base_type=request.base_type,
                max_allowed=base_player.max,
                cost=base_player.cost,
            )
            if not can_hire:
                raise InvalidOperationException(reason)
            available_treasury = (
                await UserTeamService._available_treasury_for_team_management(
                    team,
                    league_id=request.league_id,
                )
            )
            if available_treasury < base_player.cost:
                raise InvalidOperationException(
                    "Insufficient treasury "
                    "[source=user_team_service.hire_player.available_treasury] "
                    f"({available_treasury} < {base_player.cost})"
                )

        new_player = UserTeamService._build_user_player(
            team=team,
            base_player=base_player,
            base_type=request.base_type,
            name=request.name,
            number=request.number,
        )
        if request.temporary_for_match:
            new_player.temporary_for_match = True
            new_player.temporary_match_id = request.temporary_match_id
            new_player.journeyman = not request.mercenary
            if request.mercenary:
                new_player.current_value = base_player.cost + 30_000
            elif not UserTeamService._has_loner_perk(new_player.perks):
                new_player.perks.append(await UserTeamService._journeyman_loner_perk())

        # Update team
        team.players.append(new_player)
        if request.temporary_for_match and request.mercenary:
            team.treasury -= treasury_charge
        elif not request.temporary_for_match:
            team.treasury -= base_player.cost
        team.team_value = await UserTeamService._calculate_team_value(team, roster)
        team.updated_at = datetime.utcnow()
        await team.save()

        logger.info(
            f"Hired {'temporary ' if request.temporary_for_match else ''}player '{new_player.name}' ({request.base_type}) for team {team_id}"
        )

        return HirePlayerResponse(
            player=UserTeamService._player_to_response(new_player),
            treasury_remaining=team.treasury,
            team_value=team.team_value,
        )

    @staticmethod
    async def hire_star_player(
        team_id: str, user_id: str, request: HireStarPlayerRequest
    ) -> HirePlayerResponse:
        """Hire a star player for a team."""
        team = await UserTeamService._require_team_owner_or_match_access(
            team_id,
            user_id,
            league_id=request.league_id,
        )

        if not request.temporary_for_match and not request.league_id:
            await UserTeamService._ensure_roster_can_be_managed(team_id)

        # Fetch star player
        star = await StarPlayer.find_one(StarPlayer.id == request.star_player_id)
        if not star:
            raise InvalidOperationException(
                f"Star player '{request.star_player_id}' not found"
            )

        # Validate team compatibility
        if not star_player_available_for_roster(
            star_player_id=star.id,
            plays_for=star.plays_for,
            roster_id=team.base_roster_id,
            favoured_of=team.favoured_of,
        ):
            raise InvalidOperationException(
                f"Star player '{star.name}' cannot play for this team"
            )

        # Check roster space
        if team.permanent_player_count() >= 16:
            raise InvalidOperationException("Roster is full (max 16 players)")

        if not request.temporary_for_match:
            available_treasury = (
                await UserTeamService._available_treasury_for_team_management(
                    team,
                    league_id=request.league_id,
                )
            )
            if available_treasury < star.cost:
                raise InvalidOperationException(
                    "Insufficient treasury "
                    "[source=user_team_service.hire_star_player.available_treasury] "
                    f"({available_treasury} < {star.cost})"
                )

        treasury_charge = await UserTeamService._temporary_match_treasury_charge(
            team,
            league_id=request.league_id if request.temporary_for_match else None,
            match_id=(
                request.temporary_match_id if request.temporary_for_match else None
            ),
            cost=star.cost,
        )

        # Check not already hired
        for p in team.players:
            if p.base_type == f"star_{request.star_player_id}":
                raise InvalidOperationException(
                    f"Star player '{star.name}' is already on the roster"
                )

        name = request.name or star.name
        number = request.number or UserTeamService._next_available_number(team)

        new_player = UserPlayer(
            id=uuid.uuid4().hex,
            base_type=f"star_{request.star_player_id}",
            name=name,
            number=number,
            current_value=star.cost,
            stats=PlayerStats(
                MA=star.stats.MA,
                ST=star.stats.ST,
                AG=star.stats.AG,
                PA=star.stats.PA,
                AV=star.stats.AV,
            ),
            perks=[await UserTeamService._perk_from_star_skill(s) for s in star.skills],
            image=star.image,
        )
        if request.temporary_for_match:
            new_player.temporary_for_match = True
            new_player.temporary_match_id = request.temporary_match_id

        team.players.append(new_player)
        team.treasury -= treasury_charge
        team.team_value = await UserTeamService._calculate_team_value(team)
        team.updated_at = datetime.utcnow()
        await team.save()

        logger.info(
            f"Hired star player '{name}' ({request.star_player_id}) for team {team_id}"
        )

        return HirePlayerResponse(
            player=UserTeamService._player_to_response(new_player),
            treasury_remaining=team.treasury,
            team_value=team.team_value,
        )

    @staticmethod
    async def fire_player(
        team_id: str,
        user_id: str,
        player_id: str,
        *,
        league_id: Optional[str] = None,
    ) -> UserTeam:
        """Remove a player from a team (no refund)."""
        team = await UserTeamService._require_team_owner_or_match_access(
            team_id,
            user_id,
            league_id=league_id,
        )

        player_idx = None
        for i, p in enumerate(team.players):
            if p.id == player_id:
                player_idx = i
                break

        if player_idx is None:
            raise PlayerNotFoundException(player_id)

        removed = team.players.pop(player_idx)
        team.team_value = await UserTeamService._calculate_team_value(team)
        team.updated_at = datetime.utcnow()
        await team.save()

        logger.info(f"Fired player '{removed.name}' from team {team_id}")
        return team

    @staticmethod
    async def add_perk_to_player(
        team_id: str,
        user_id: str,
        player_id: str,
        perk_id: str,
        perk_name: str,
        parameter: Optional[str] = None,
        category: str = None,
        league_id: Optional[str] = None,
    ) -> UserTeam:
        """Add a perk to a player.

        Skills still use the official advancement flow. Traits may be granted
        manually by special rules and can carry a parameter such as Hatred (X).
        """
        perk = await UserTeamService._find_advancement_perk(perk_id)
        if not perk:
            raise InvalidOperationException(f"Perk '{perk_id}' not found")

        perk_kind = (perk.kind or "").lower()
        category_key = (category or "").lower()
        if perk_kind != "trait" and category_key not in {"trait", "t"}:
            return await UserTeamService.apply_player_advancement(
                team_id,
                user_id,
                player_id,
                ApplyPlayerAdvancementRequest(
                    advancement_type="choose_primary_skill",
                    perk_id=perk_id,
                    league_id=league_id,
                ),
            )

        team = await UserTeamService._require_team_owner_or_match_access(
            team_id,
            user_id,
            league_id=league_id,
        )

        roster = await BaseRoster.find_one(BaseRoster.id == team.base_roster_id)
        if not roster:
            raise InvalidOperationException("Team roster not found")

        player = UserTeamService._find_team_player(team, player_id)
        if player.status == "dead":
            raise InvalidOperationException("Dead players cannot gain traits")

        stored_perk_id = str(perk.id)
        normalized_perk_id = UserTeamService._normal_key(stored_perk_id)
        perk_parameter = parameter.strip() if parameter and parameter.strip() else None
        normalized_parameter = (perk_parameter or "").strip().lower()

        if any(
            UserTeamService._normal_key(pk.id) == normalized_perk_id
            and (pk.parameter or "").strip().lower() == normalized_parameter
            for pk in player.perks
        ):
            raise InvalidOperationException("Player already has this trait")

        family = perk.family or category
        name = UserTeamService._localized_name(perk.name, stored_perk_id)
        player.perks.append(
            PlayerPerk(
                id=stored_perk_id,
                name=name,
                parameter=perk_parameter,
                category=family,
            )
        )
        label = f"Rasgo por regla: {name}"
        if perk_parameter:
            label = f"{label} ({perk_parameter})"
        player.injury_history.append(
            PlayerInjuryRecord(
                type="advancement",
                label=label,
                notes="Anadido por regla especial",
            )
        )
        team.team_value = await UserTeamService._calculate_team_value(team, roster)
        team.updated_at = datetime.utcnow()
        await team.save()
        return team

    @staticmethod
    async def apply_player_advancement(
        team_id: str,
        user_id: str,
        player_id: str,
        request: ApplyPlayerAdvancementRequest,
    ) -> UserTeam:
        """Spend SPP on an official player advancement."""
        team = await UserTeamService._require_team_owner_or_match_access(
            team_id,
            user_id,
            league_id=request.league_id,
        )

        roster = await BaseRoster.find_one(BaseRoster.id == team.base_roster_id)
        if not roster:
            raise InvalidOperationException("Team roster not found")

        player = UserTeamService._find_team_player(team, player_id)
        base_player = UserTeamService._find_base_player(roster, player.base_type)

        if player.base_type.startswith("star_"):
            raise InvalidOperationException("Star Players cannot gain advancements")
        if player.status == "dead":
            raise InvalidOperationException("Dead players cannot gain advancements")

        rules = await AdvancementRules.get("advancement_rules")
        if not rules:
            raise InvalidOperationException("Advancement rules not found")

        advancement_count = UserTeamService._player_advancement_count(
            player, base_player
        )
        if advancement_count >= rules.max_advancements:
            raise InvalidOperationException("Player has reached maximum advancements")

        cost_row = rules.cost_table[advancement_count]
        spp_cost = getattr(cost_row, request.advancement_type)
        if player.spp < spp_cost:
            raise InvalidOperationException(
                f"Not enough SPP ({player.spp} < {spp_cost})"
            )

        value_increase = 0
        if request.advancement_type == "characteristic_improvement":
            value_increase = UserTeamService._apply_characteristic_advancement(
                player, request, rules
            )
        else:
            value_increase = await UserTeamService._apply_skill_advancement(
                player, base_player, request, rules
            )

        player.spp -= spp_cost
        player.current_value += value_increase
        player.advancements = advancement_count + 1
        player.injury_history.append(
            PlayerInjuryRecord(
                type="advancement",
                label=UserTeamService._advancement_history_label(player, request),
                notes=UserTeamService._advancement_history_notes(
                    request, spp_cost, value_increase
                ),
                roll=request.characteristic_roll,
                stat=request.characteristic,
                reduction=f"+{value_increase // 1000}k TV" if value_increase else None,
            )
        )
        team.team_value = await UserTeamService._calculate_team_value(team, roster)
        team.updated_at = datetime.utcnow()
        await team.save()

        return team

    @staticmethod
    async def _apply_skill_advancement(
        player: UserPlayer,
        base_player: BasePlayer,
        request: ApplyPlayerAdvancementRequest,
        rules: AdvancementRules,
    ) -> int:
        selected_symbol = None
        perk_id = request.perk_id

        if request.advancement_type == "random_primary_skill":
            selected_symbol = UserTeamService._family_symbol(request.skill_category)
            if not selected_symbol:
                raise InvalidOperationException(
                    "Random primary skill requires a valid skill_category"
                )
            if selected_symbol not in base_player.primary_access:
                raise InvalidOperationException(
                    f"Skill family '{selected_symbol}' is not Primary for this player"
                )
            perk_id = UserTeamService._resolve_random_primary_skill_perk_id(
                rules,
                selected_symbol,
                request.random_skill_first_d6,
                request.random_skill_second_d6,
            )
        elif not perk_id:
            raise InvalidOperationException("Skill advancement requires perk_id")

        perk = await UserTeamService._find_advancement_perk(perk_id)
        if not perk:
            raise InvalidOperationException(f"Perk '{perk_id}' not found")

        stored_perk_id = str(perk.id)
        if (perk.kind or "").lower() != "skill":
            raise InvalidOperationException(
                "Traits cannot be acquired as skill advancements"
            )

        normalized_perk_id = UserTeamService._normal_key(stored_perk_id)
        if any(
            UserTeamService._normal_key(pk.id) == normalized_perk_id
            for pk in player.perks
        ):
            raise InvalidOperationException("Player already has this skill")

        family = perk.family
        symbol = UserTeamService._family_symbol(family)
        if not symbol:
            raise InvalidOperationException("Only skill categories can be advanced")

        if request.advancement_type == "random_primary_skill":
            if symbol != selected_symbol:
                raise InvalidOperationException(
                    "Random skill result does not belong to the selected category"
                )
            value_key = "primary_skill"
        elif request.advancement_type == "choose_primary_skill":
            if symbol not in base_player.primary_access:
                raise InvalidOperationException(
                    f"Skill family '{symbol}' is not Primary for this player"
                )
            value_key = "primary_skill"
        elif request.advancement_type == "choose_secondary_skill":
            if symbol not in base_player.secondary_access:
                raise InvalidOperationException(
                    f"Skill family '{symbol}' is not Secondary for this player"
                )
            value_key = "secondary_skill"
        else:
            raise InvalidOperationException("Invalid skill advancement type")

        name = UserTeamService._localized_name(perk.name, stored_perk_id)
        player.perks.append(PlayerPerk(id=stored_perk_id, name=name, category=family))
        value_increase = UserTeamService._value_increase(rules, value_key)
        if perk.elite:
            value_increase += UserTeamService.ELITE_SKILL_VALUE_BONUS
        return value_increase

    @staticmethod
    def _resolve_random_primary_skill_perk_id(
        rules: AdvancementRules,
        skill_category: str,
        first_d6: int | None,
        second_d6: int | None,
    ) -> str:
        if first_d6 is None or second_d6 is None:
            raise InvalidOperationException(
                "Random primary skill requires both D6 roll values"
            )

        target_symbol = UserTeamService._family_symbol(skill_category)
        if not target_symbol:
            raise InvalidOperationException("Unknown skill category for random skill")

        column_index = next(
            (
                index
                for index, category in enumerate(rules.skill_categories)
                if UserTeamService._family_symbol(category.symbol) == target_symbol
                or UserTeamService._family_symbol(category.family) == target_symbol
            ),
            None,
        )
        if column_index is None:
            raise InvalidOperationException(
                f"Random skill category '{target_symbol}' is not configured"
            )

        entry = next(
            (
                row
                for row in rules.random_primary_skill_table
                if row.first_d6_min <= first_d6 <= row.first_d6_max
                and row.second_d6 == second_d6
            ),
            None,
        )
        if not entry:
            raise InvalidOperationException(
                f"No random primary skill entry for {first_d6}+{second_d6}"
            )
        if column_index >= len(entry.perk_ids):
            raise InvalidOperationException(
                f"Random primary skill entry for {first_d6}+{second_d6} is incomplete"
            )

        return entry.perk_ids[column_index]

    @staticmethod
    def _apply_characteristic_advancement(
        player: UserPlayer,
        request: ApplyPlayerAdvancementRequest,
        rules: AdvancementRules,
    ) -> int:
        if not request.characteristic or request.characteristic_roll is None:
            raise InvalidOperationException(
                "Characteristic advancement requires characteristic and characteristic_roll"
            )

        result = next(
            (
                entry
                for entry in rules.characteristic_table
                if entry.min_roll <= request.characteristic_roll <= entry.max_roll
            ),
            None,
        )
        if not result or request.characteristic not in result.choices:
            raise InvalidOperationException(
                "Characteristic is not allowed for this D8 improvement roll"
            )

        current_increases = player.stat_increases.get(request.characteristic, 0)
        if current_increases >= rules.max_characteristic_improvements_per_stat:
            raise InvalidOperationException(
                "Characteristic cannot be improved more than twice"
            )

        if request.characteristic == "MA":
            player.stats.MA += 1
        elif request.characteristic == "ST":
            player.stats.ST += 1
        elif request.characteristic == "AG":
            player.stats.AG -= 1
        elif request.characteristic == "PA":
            if player.stats.PA is None:
                raise InvalidOperationException("Player cannot improve PA")
            player.stats.PA -= 1
        elif request.characteristic == "AV":
            player.stats.AV += 1

        player.stat_increases[request.characteristic] = current_increases + 1
        return UserTeamService._value_increase(rules, request.characteristic)

    @staticmethod
    def _value_increase(rules: AdvancementRules, advancement_type: str) -> int:
        for increase in rules.value_increases:
            if increase.advancement_type == advancement_type:
                return increase.value
        raise InvalidOperationException(
            f"Value increase for '{advancement_type}' not found"
        )

    @staticmethod
    def _advancement_history_label(
        player: UserPlayer, request: ApplyPlayerAdvancementRequest
    ) -> str:
        if request.advancement_type == "characteristic_improvement":
            return f"Mejora de atributo: {request.characteristic}"
        if player.perks:
            return f"Mejora: {player.perks[-1].name}"
        return "Mejora comprada con SPP"

    @staticmethod
    def _advancement_history_notes(
        request: ApplyPlayerAdvancementRequest, spp_cost: int, value_increase: int
    ) -> str:
        labels = {
            "random_primary_skill": "Primaria al azar",
            "choose_primary_skill": "Primaria elegida",
            "choose_secondary_skill": "Secundaria elegida",
            "characteristic_improvement": "Mejora de atributo",
        }
        details = [labels.get(request.advancement_type, request.advancement_type)]
        details.append(f"Coste {spp_cost} SPP")
        if value_increase:
            details.append(f"+{value_increase // 1000}k TV")
        if request.characteristic_roll is not None:
            details.append(f"D8 {request.characteristic_roll}")
        return " · ".join(details)

    @staticmethod
    async def update_player(
        team_id: str, user_id: str, player_id: str, request: UpdatePlayerRequest
    ) -> UserTeam:
        """Update a player's name, jersey number, image, status and/or injury history."""
        team = await UserTeamService._require_team_owner_or_match_access(
            team_id,
            user_id,
            league_id=request.league_id,
            match_id=request.match_id,
            quick_match_id=request.quick_match_id,
        )

        player = None
        for p in team.players:
            if p.id == player_id:
                player = p
                break

        if not player:
            raise PlayerNotFoundException(player_id)

        if request.number is not None:
            # Check number is not already taken by another player
            for p in team.players:
                if (
                    p.id != player_id
                    and not UserTeamService._is_dead_player(p)
                    and p.number == request.number
                ):
                    raise InvalidOperationException(
                        f"Jersey number {request.number} is already taken"
                    )
            player.number = request.number

        if request.name is not None:
            player.name = request.name

        if request.image is not None:
            player.image = request.image.strip() or None

        if request.injury_category is not None:
            await UserTeamService._apply_player_condition(player, request)
        elif request.status is not None:
            player.status = request.status

        team.updated_at = datetime.utcnow()
        await team.save()

        logger.info(
            f"Updated player '{player.name}' (#{player.number}) in team {team_id}"
        )
        return team

    @staticmethod
    async def _apply_player_condition(
        player: UserPlayer, request: UpdatePlayerRequest
    ) -> None:
        category = request.injury_category

        if category == "miss_next_game":
            player.status = PlayerStatus.MISSING_NEXT_GAME.value
            player.injury_history.append(
                PlayerInjuryRecord(
                    type="miss_next_game",
                    label="Se pierde el proximo partido",
                    notes=request.injury_note,
                )
            )
            return

        if category == "sent_off":
            player.injury_history.append(
                PlayerInjuryRecord(
                    type="sent_off",
                    label="Expulsado",
                    notes=request.injury_note,
                )
            )
            return

        if category == "dead":
            player.status = PlayerStatus.DEAD.value
            if "dead" not in player.injuries:
                player.injuries.append("dead")
            player.injury_history.append(
                PlayerInjuryRecord(
                    type="dead",
                    label="Muerto",
                    notes=request.injury_note,
                )
            )
            return

        if category == "lasting_injury":
            if request.lasting_injury_roll is None:
                raise InvalidOperationException("Lasting injury requires a D6 roll")
            rules = await InjuryRules.get("injury_rules")
            if not rules:
                raise InvalidOperationException("Injury rules are not available")
            lasting = next(
                (
                    result
                    for result in rules.lasting_injury_table
                    if result.min_roll <= request.lasting_injury_roll <= result.max_roll
                ),
                None,
            )
            if not lasting:
                raise InvalidOperationException(
                    f"Invalid lasting injury roll '{request.lasting_injury_roll}'"
                )
            UserTeamService._apply_stat_reduction(player, lasting.stat)
            player.status = PlayerStatus.MISSING_NEXT_GAME.value
            player.injuries.append(lasting.code)
            player.injury_history.append(
                PlayerInjuryRecord(
                    type="lasting_injury",
                    label=lasting.label.es or lasting.label.en or lasting.code,
                    notes=request.injury_note,
                    roll=request.lasting_injury_roll,
                    stat=lasting.stat,
                    reduction=lasting.reduction_label,
                )
            )

    @staticmethod
    def _apply_stat_reduction(player: UserPlayer, stat: str) -> None:
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

    # ============== Helpers ==============

    @staticmethod
    def _next_available_number(team: UserTeam) -> int:
        """Find next available jersey number."""
        used = {
            p.number for p in team.players if not UserTeamService._is_dead_player(p)
        }
        for n in range(1, 100):
            if n not in used:
                return n
        return random.randint(1, 99)

    @staticmethod
    def _is_dead_player(player: UserPlayer) -> bool:
        status = (
            player.status.value if hasattr(player.status, "value") else player.status
        )
        return status == PlayerStatus.DEAD.value

    @staticmethod
    def _find_base_player(roster: BaseRoster, base_type: str) -> BasePlayer:
        """Find a player type in a base roster."""
        for player in roster.players:
            if player.type == base_type:
                return player
        raise InvalidOperationException(
            f"Player type '{base_type}' not available in this roster"
        )

    @staticmethod
    def _find_team_player(team: UserTeam, player_id: str) -> UserPlayer:
        for player in team.players:
            if player.id == player_id:
                return player
        raise PlayerNotFoundException(player_id)

    @staticmethod
    def _player_advancement_count(player: UserPlayer, base_player: BasePlayer) -> int:
        starting_keys = {
            UserTeamService._normal_key(perk.id) for perk in base_player.perks
        } | {UserTeamService._normal_key(perk.name) for perk in base_player.perks}
        acquired_skills = sum(
            1
            for perk in player.perks
            if UserTeamService._normal_key(perk.id) not in starting_keys
            and UserTeamService._normal_key(perk.name) not in starting_keys
            and (perk.category or "").lower() not in {"t", "trait"}
            and UserTeamService._normal_key(perk.id) != "loner"
        )
        stat_advancements = sum(player.stat_increases.values())
        return max(player.advancements, acquired_skills + stat_advancements)

    @staticmethod
    def _normal_key(value: str) -> str:
        stripped = UserTeamService._strip_perk_parameter(value)
        normalized = re.sub(r"[^a-z0-9]+", "-", stripped.lower().strip())
        normalized = normalized.strip("-").replace("perk-", "")
        aliases = {
            "plague-ridden": "infected",
        }
        return aliases.get(normalized, normalized)

    @staticmethod
    def _is_loner_perk(perk: PlayerPerk) -> bool:
        return (
            UserTeamService._normal_key(perk.id) == UserTeamService.JOURNEYMAN_LONER_ID
            or UserTeamService._normal_key(perk.name)
            == UserTeamService.JOURNEYMAN_LONER_ID
        )

    @staticmethod
    def _has_loner_perk(perks: list[PlayerPerk]) -> bool:
        return any(UserTeamService._is_loner_perk(perk) for perk in perks)

    @staticmethod
    def _is_journeyman_loner_perk(perk: PlayerPerk) -> bool:
        return (
            UserTeamService._is_loner_perk(perk)
            and perk.parameter == UserTeamService.JOURNEYMAN_LONER_PARAMETER
        )

    @staticmethod
    async def _journeyman_loner_perk() -> PlayerPerk:
        perk = await UserTeamService._find_advancement_perk(
            UserTeamService.JOURNEYMAN_LONER_ID
        )
        return PlayerPerk(
            id=UserTeamService.JOURNEYMAN_LONER_ID,
            name=UserTeamService._localized_name(
                perk.name if perk else None,
                "Solitario",
            ),
            parameter=UserTeamService.JOURNEYMAN_LONER_PARAMETER,
            category=UserTeamService._family_symbol(perk.family) if perk else "T",
        )

    @staticmethod
    def _extract_perk_parameter(value: str) -> str | None:
        match = re.search(r"\(([^)]+)\)", value or "")
        if not match:
            return None
        parameter = match.group(1).strip()
        return parameter or None

    @staticmethod
    def _strip_perk_parameter(value: str) -> str:
        return re.sub(r"\s*\([^)]*\)", "", value or "").strip()

    @staticmethod
    def _family_symbol(family: str | None) -> str | None:
        if not family:
            return None
        value = family.strip()
        if value in {"A", "D", "G", "M", "P", "S"}:
            return value
        return UserTeamService.FAMILY_TO_SYMBOL.get(value.lower())

    @staticmethod
    async def _find_advancement_perk(perk_id: str) -> Perk | None:
        direct_aliases = {
            "plague_ridden": "infected",
            "plague-ridden": "infected",
            "perk-plague-ridden": "infected",
        }
        perk = await Perk.get(direct_aliases.get(perk_id, perk_id))
        if perk:
            return perk

        normalized_id = perk_id.removeprefix("perk-").replace("-", "_")
        normalized_id = direct_aliases.get(normalized_id, normalized_id)

        if normalized_id != perk_id:
            perk = await Perk.get(normalized_id)
            if perk:
                return perk

        if perk_id.startswith("perk-"):
            return await Perk.get(normalized_id)

        if "-" in perk_id:
            return await Perk.get(normalized_id)

        return None

    @staticmethod
    def _localized_name(name: dict | None, fallback: str) -> str:
        if not name:
            return fallback
        return name.get("es") or name.get("en") or fallback

    @staticmethod
    async def _perk_from_star_skill(raw_skill: str) -> PlayerPerk:
        stored_perk_id = UserTeamService._normal_key(raw_skill).replace("-", "_")
        perk = await UserTeamService._find_advancement_perk(stored_perk_id)

        return PlayerPerk(
            id=stored_perk_id,
            name=UserTeamService._localized_name(
                perk.name if perk else None,
                UserTeamService._strip_perk_parameter(raw_skill),
            ),
            parameter=UserTeamService._extract_perk_parameter(raw_skill),
            category=UserTeamService._family_symbol(perk.family) if perk else None,
        )

    @staticmethod
    def _build_user_player(
        team: UserTeam,
        base_player: BasePlayer,
        base_type: str,
        name: Optional[str],
        number: Optional[int],
    ) -> UserPlayer:
        """Create a user player from a base roster player."""
        jersey_number = number or UserTeamService._next_available_number(team)
        if any(
            player.number == jersey_number
            and not UserTeamService._is_dead_player(player)
            for player in team.players
        ):
            raise InvalidOperationException(
                f"Jersey number {jersey_number} is already taken"
            )
        player_name = name or UserTeamService._default_player_name(
            base_player, len(team.players) + 1
        )

        return UserPlayer(
            id=uuid.uuid4().hex,
            base_type=base_type,
            name=player_name,
            number=jersey_number,
            current_value=base_player.cost,
            stats=PlayerStats(
                MA=base_player.stats.MA,
                ST=base_player.stats.ST,
                AG=base_player.stats.AG,
                PA=base_player.stats.PA,
                AV=base_player.stats.AV,
            ),
            perks=[
                PlayerPerk(
                    id=pk.id,
                    name=pk.name,
                    parameter=pk.parameter,
                    category=pk.category,
                )
                for pk in base_player.perks
            ],
            image=base_player.image,
            tag_image=base_player.tag_image,
        )

    @staticmethod
    def _default_player_name(base_player: BasePlayer, index: int) -> str:
        """Build a compact default name from verbose roster labels."""
        base_name = base_player.name.split("(", 1)[0].strip()
        player_name = f"{base_name} #{index}"
        return player_name[:50]

    @staticmethod
    def _player_to_response(player: UserPlayer) -> UserPlayerResponse:
        """Convert player model to response."""
        return UserPlayerResponse(
            id=player.id,
            base_type=player.base_type,
            name=player.name,
            number=player.number,
            current_value=player.current_value,
            stats=PlayerStatsResponse(
                MA=player.stats.MA,
                ST=player.stats.ST,
                AG=f"{player.stats.AG}+",
                PA=f"{player.stats.PA}+" if player.stats.PA else "-",
                AV=f"{player.stats.AV}+",
            ),
            perks=[
                PlayerPerkResponse(
                    id=pk.id,
                    name=pk.name,
                    parameter=pk.parameter,
                    category=pk.category,
                )
                for pk in player.perks
            ],
            stat_increases=player.stat_increases,
            advancements=player.advancements,
            level=player.advancements + 1,
            injuries=player.injuries,
            injury_history=[
                PlayerInjuryRecordResponse(
                    id=record.id,
                    type=record.type,
                    label=record.label,
                    notes=record.notes,
                    roll=record.roll,
                    stat=record.stat,
                    reduction=record.reduction,
                    created_at=record.created_at,
                )
                for record in player.injury_history
            ],
            spp=player.spp,
            status=player.status,
            career=PlayerCareerResponse(
                games=player.career.games,
                touchdowns=player.career.touchdowns,
                casualties=player.career.casualties,
                interceptions=player.career.interceptions,
                completions=player.career.completions,
                mvp_awards=player.career.mvp_awards,
            ),
            temporary_for_match=player.temporary_for_match,
            temporary_match_id=player.temporary_match_id,
            journeyman=player.journeyman,
            image=player.image,
        )
