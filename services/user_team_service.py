"""Service for user team operations."""

import logging
import random
import uuid
from datetime import datetime
from typing import Optional

from exceptions.exceptions import (
    InvalidOperationException,
    PlayerNotFoundException,
    TeamNotFoundException,
)
from models.base.roster import BaseRoster
from models.user.user import User
from models.user_team.team import (
    PlayerPerk,
    PlayerStats,
    UserPlayer,
    UserTeam,
)
from schemas.user_team import (
    CreateTeamRequest,
    HirePlayerRequest,
    HirePlayerResponse,
    PlayerCareerResponse,
    PlayerPerkResponse,
    PlayerStatsResponse,
    UpdateTeamRequest,
    UserPlayerResponse,
    UserTeamDetail,
    UserTeamSummary,
)

logger = logging.getLogger(__name__)


class UserTeamService:
    """Service for managing user teams."""

    # ============== Team Operations ==============

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

        return [
            UserTeamSummary(
                id=str(t.id),
                name=t.name,
                base_roster_id=t.base_roster_id,
                team_value=t.team_value,
                treasury=t.treasury,
                player_count=len(t.players),
                icon=t.icon,
                created_at=t.created_at,
            )
            for t in teams
        ]

    @staticmethod
    async def get_team_detail(team_id: str) -> Optional[UserTeamDetail]:
        """Get full team detail with players."""
        team = await UserTeam.get(team_id)
        if not team:
            return None

        roster = await BaseRoster.find_one(BaseRoster.id == team.base_roster_id)

        players = [UserTeamService._player_to_response(p) for p in team.players]

        return UserTeamDetail(
            id=str(team.id),
            user_id=team.user_id,
            base_roster_id=team.base_roster_id,
            name=team.name,
            players=players,
            treasury=team.treasury,
            team_value=team.team_value,
            rerolls=team.rerolls,
            reroll_cost=roster.reroll_cost if roster else 0,
            fan_factor=team.fan_factor,
            cheerleaders=team.cheerleaders,
            assistant_coaches=team.assistant_coaches,
            apothecary=team.apothecary,
            apothecary_allowed=roster.apothecary_allowed if roster else True,
            dedicated_fans=team.dedicated_fans,
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
        """Hire a new player for a team."""
        team = await UserTeam.get(team_id)
        if not team:
            raise TeamNotFoundException(team_id)

        # Get base roster and player type
        roster = await BaseRoster.find_one(BaseRoster.id == team.base_roster_id)
        if not roster:
            raise InvalidOperationException("Team roster not found")

        base_player = None
        for p in roster.players:
            if p.type == request.base_type:
                base_player = p
                break

        if not base_player:
            raise InvalidOperationException(
                f"Player type '{request.base_type}' not available in this roster"
            )

        # Validate hiring
        can_hire, reason = team.can_hire_player(
            base_type=request.base_type,
            max_allowed=base_player.max,
            cost=base_player.cost,
        )
        if not can_hire:
            raise InvalidOperationException(reason)

        # Generate name and number if not provided
        name = request.name or f"{base_player.name} #{len(team.players) + 1}"
        number = request.number or UserTeamService._next_available_number(team)

        # Create player with copied stats/perks from base
        new_player = UserPlayer(
            id=uuid.uuid4().hex,
            base_type=request.base_type,
            name=name,
            number=number,
            current_value=base_player.cost,
            stats=PlayerStats(
                MA=base_player.stats.MA,
                ST=base_player.stats.ST,
                AG=base_player.stats.AG,
                PA=base_player.stats.PA,
                AV=base_player.stats.AV,
            ),
            perks=[
                PlayerPerk(id=pk.id, name=pk.name, category=pk.category)
                for pk in base_player.perks
            ],
            image=base_player.image,
            tag_image=base_player.tag_image,
        )

        # Update team
        team.players.append(new_player)
        team.treasury -= base_player.cost
        team.team_value = team.calculate_team_value()
        team.updated_at = datetime.utcnow()
        await team.save()

        logger.info(f"Hired player '{name}' ({request.base_type}) for team {team_id}")

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
        team.team_value = team.calculate_team_value()
        team.updated_at = datetime.utcnow()
        await team.save()

        logger.info(f"Fired player '{removed.name}' from team {team_id}")
        return team

    @staticmethod
    async def add_perk_to_player(
        team_id: str, player_id: str, perk_id: str, perk_name: str, category: str = None
    ) -> UserTeam:
        """Add a skill/perk to a player."""
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

        # Check if player already has this perk
        if any(pk.id == perk_id for pk in player.perks):
            raise InvalidOperationException(f"Player already has perk '{perk_name}'")

        player.perks.append(PlayerPerk(id=perk_id, name=perk_name, category=category))
        # Increase player value (simplified: +20k per skill)
        player.current_value += 20000
        team.team_value = team.calculate_team_value()
        team.updated_at = datetime.utcnow()
        await team.save()

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
                PlayerPerkResponse(id=pk.id, name=pk.name, category=pk.category)
                for pk in player.perks
            ],
            stat_increases=player.stat_increases,
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
            image=player.image,
        )
