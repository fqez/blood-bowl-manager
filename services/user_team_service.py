"""Service for user team operations."""

import logging
import random
import re
import uuid
from datetime import datetime
from typing import Optional

from exceptions.exceptions import (
    InvalidOperationException,
    PlayerNotFoundException,
    TeamNotFoundException,
)
from models.base.advancement import AdvancementRules
from models.base.roster import BasePlayer, BaseRoster
from models.base.star_player import StarPlayer
from models.league.league import League, LeagueStatus
from models.user.user import User
from models.user_team.team import (
    PlayerPerk,
    PlayerStats,
    TeamValueBreakdown,
    UserPlayer,
    UserTeam,
)
from models.team.perk import Perk
from schemas.user_team import (
    ApplyPlayerAdvancementRequest,
    CreateTeamRequest,
    HirePlayerRequest,
    HirePlayerResponse,
    HireStarPlayerRequest,
    PlayerCareerResponse,
    PlayerPerkResponse,
    PlayerStatsResponse,
    TeamValueBreakdownResponse,
    TeamLeagueMembership,
    UpdatePlayerRequest,
    UpdateTeamRequest,
    UserPlayerResponse,
    UserTeamDetail,
    UserTeamSummary,
)

logger = logging.getLogger(__name__)


class UserTeamService:
    """Service for managing user teams."""

    JOURNEYMAN_LONER_ID = "loner"
    JOURNEYMAN_LONER_PARAMETER = "4+"

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
        return team.calculate_team_value_breakdown(reroll_cost=reroll_cost)

    @staticmethod
    def _eligible_player_count(team: UserTeam) -> int:
        """Count players able to play the next game."""
        return sum(1 for player in team.players if player.status == "healthy")

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
    async def create_team(user_id: str, request: CreateTeamRequest) -> UserTeam:
        """Create a new team for a user."""
        # Verify roster exists
        roster = await BaseRoster.find_one(BaseRoster.id == request.base_roster_id)
        if not roster:
            raise InvalidOperationException(
                f"Roster '{request.base_roster_id}' not found"
            )

        team = UserTeam(
            user_id=user_id,
            base_roster_id=request.base_roster_id,
            name=request.name,
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
                    league_memberships=memberships.get(team_id, []),
                    icon=t.icon,
                    created_at=t.created_at,
                )
            )
        return summaries

    @staticmethod
    async def get_team_detail(team_id: str) -> Optional[UserTeamDetail]:
        """Get full team detail with players."""
        team = await UserTeam.get(team_id)
        if not team:
            return None

        roster = await BaseRoster.find_one(BaseRoster.id == team.base_roster_id)
        await UserTeamService._sync_team_value(team, roster)
        value_breakdown = await UserTeamService._calculate_team_value_breakdown(
            team, roster
        )

        players = [UserTeamService._player_to_response(p) for p in team.players]

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
            can_manage_roster=not await UserTeamService._is_in_active_league(team_id),
            league_memberships=await UserTeamService._league_memberships(team_id),
            icon=team.icon,
            wallpaper=team.wallpaper,
            created_at=team.created_at,
            updated_at=team.updated_at,
        )

    @staticmethod
    async def update_team(team_id: str, request: UpdateTeamRequest) -> UserTeam:
        """Update team settings."""
        team = await UserTeam.get(team_id)
        if not team:
            raise TeamNotFoundException(team_id)

        if request.name is not None:
            await UserTeamService._ensure_roster_can_be_managed(team_id)

        # Load base roster for costs
        roster = await BaseRoster.find_one(BaseRoster.id == team.base_roster_id)
        reroll_cost = roster.reroll_cost if roster else 60000
        reroll_purchase_cost = (
            reroll_cost * 2
            if await UserTeamService._is_in_league(team_id)
            else reroll_cost
        )

        # Calculate treasury delta for staff changes
        cost_delta = 0
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

        # Validate treasury
        if cost_delta > 0 and team.treasury < cost_delta:
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
            if not await UserTeamService._is_in_league(team_id):
                raise InvalidOperationException(
                    "Dedicated fans can only change during league play"
                )
            team.dedicated_fans = request.dedicated_fans
        if request.treasury is not None:
            team.treasury = request.treasury

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
        team_id: str, request: HirePlayerRequest
    ) -> HirePlayerResponse:
        """Hire a new player for a team.

        Player hiring is allowed for teams registered in active leagues; other
        roster management actions remain locked by _ensure_roster_can_be_managed.
        """
        team = await UserTeam.get(team_id)
        if not team:
            raise TeamNotFoundException(team_id)

        # Get base roster and player type
        roster = await BaseRoster.find_one(BaseRoster.id == team.base_roster_id)
        if not roster:
            raise InvalidOperationException("Team roster not found")

        base_player = UserTeamService._find_base_player(roster, request.base_type)

        if request.temporary_for_match:
            if base_player.position.lower() != "lineman" or base_player.max != 16:
                raise InvalidOperationException(
                    "Journeymen must be Lineman position players with QTY 0-16"
                )
            if UserTeamService._eligible_player_count(team) >= 11:
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
            new_player.journeyman = True
            if not UserTeamService._has_loner_perk(new_player.perks):
                new_player.perks.append(UserTeamService._journeyman_loner_perk())

        # Update team
        team.players.append(new_player)
        if not request.temporary_for_match:
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
        team_id: str, request: HireStarPlayerRequest
    ) -> HirePlayerResponse:
        """Hire a star player for a team."""
        team = await UserTeam.get(team_id)
        if not team:
            raise TeamNotFoundException(team_id)

        if not request.temporary_for_match:
            await UserTeamService._ensure_roster_can_be_managed(team_id)

        # Fetch star player
        star = await StarPlayer.find_one(StarPlayer.id == request.star_player_id)
        if not star:
            raise InvalidOperationException(
                f"Star player '{request.star_player_id}' not found"
            )

        # Validate team compatibility
        if team.base_roster_id not in star.plays_for:
            raise InvalidOperationException(
                f"Star player '{star.name}' cannot play for this team"
            )

        # Check roster space
        if len(team.players) >= 16:
            raise InvalidOperationException("Roster is full (max 16 players)")

        # Check treasury
        if team.treasury < star.cost:
            raise InvalidOperationException(
                f"Insufficient treasury ({team.treasury} < {star.cost})"
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
            perks=[
                PlayerPerk(
                    id=UserTeamService._normal_key(s),
                    name=UserTeamService._strip_perk_parameter(s),
                    parameter=UserTeamService._extract_perk_parameter(s),
                )
                for s in star.skills
            ],
            image=star.image,
        )
        if request.temporary_for_match:
            new_player.temporary_for_match = True
            new_player.temporary_match_id = request.temporary_match_id

        team.players.append(new_player)
        team.treasury -= star.cost
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
    async def fire_player(team_id: str, player_id: str) -> UserTeam:
        """Remove a player from a team (no refund)."""
        team = await UserTeam.get(team_id)
        if not team:
            raise TeamNotFoundException(team_id)

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
        team_id: str, player_id: str, perk_id: str, perk_name: str, category: str = None
    ) -> UserTeam:
        """Spend SPP to add a chosen Primary skill to a player."""
        return await UserTeamService.apply_player_advancement(
            team_id,
            player_id,
            ApplyPlayerAdvancementRequest(
                advancement_type="choose_primary_skill",
                perk_id=perk_id,
            ),
        )

    @staticmethod
    async def apply_player_advancement(
        team_id: str, player_id: str, request: ApplyPlayerAdvancementRequest
    ) -> UserTeam:
        """Spend SPP on an official player advancement."""
        team = await UserTeam.get(team_id)
        if not team:
            raise TeamNotFoundException(team_id)

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
        if not request.perk_id:
            raise InvalidOperationException("Skill advancement requires perk_id")

        perk = await UserTeamService._find_advancement_perk(request.perk_id)
        if not perk:
            raise InvalidOperationException(f"Perk '{request.perk_id}' not found")

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

        if request.advancement_type in {"random_primary_skill", "choose_primary_skill"}:
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
        return UserTeamService._value_increase(rules, value_key)

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
    async def update_player(
        team_id: str, player_id: str, request: UpdatePlayerRequest
    ) -> UserTeam:
        """Update a player's name and/or jersey number."""
        team = await UserTeam.get(team_id)
        if not team:
            raise TeamNotFoundException(team_id)

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
                if p.id != player_id and p.number == request.number:
                    raise InvalidOperationException(
                        f"Jersey number {request.number} is already taken"
                    )
            player.number = request.number

        if request.name is not None:
            player.name = request.name

        team.updated_at = datetime.utcnow()
        await team.save()

        logger.info(
            f"Updated player '{player.name}' (#{player.number}) in team {team_id}"
        )
        return team

    # ============== Helpers ==============

    @staticmethod
    def _next_available_number(team: UserTeam) -> int:
        """Find next available jersey number."""
        used = {p.number for p in team.players}
        for n in range(1, 100):
            if n not in used:
                return n
        return random.randint(1, 99)

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
        return normalized.strip("-").replace("perk-", "")

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
    def _journeyman_loner_perk() -> PlayerPerk:
        return PlayerPerk(
            id=UserTeamService.JOURNEYMAN_LONER_ID,
            name="Loner",
            parameter=UserTeamService.JOURNEYMAN_LONER_PARAMETER,
            category="T",
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
        perk = await Perk.get(perk_id)
        if perk:
            return perk

        if perk_id.startswith("perk-"):
            normalized_id = perk_id.removeprefix("perk-").replace("-", "_")
            return await Perk.get(normalized_id)

        return None

    @staticmethod
    def _localized_name(name: dict | None, fallback: str) -> str:
        if not name:
            return fallback
        return name.get("en") or name.get("es") or fallback

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
        if any(player.number == jersey_number for player in team.players):
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
