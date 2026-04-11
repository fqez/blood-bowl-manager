import asyncio
from typing import List, Union

from database.interfaces.database_interface import DatabaseInterface
from exceptions.exceptions import TeamNotFoundException
from models.team.team import Team
from schemas.team import TeamProjection, UpdateTeam
from utils.logging_config import get_service_logger

logger = get_service_logger()


async def _inject_character_to_team(
    team: Team, character_db: DatabaseInterface
) -> dict:
    """Inject full character objects into team roster."""
    roster = []
    for char_id in team.roster:
        character = await character_db.get_entity(char_id)
        if character:
            roster.append(character.model_dump())
        else:
            logger.warning(f"Character {char_id} not found for team {team.id}")
    team_dict = team.model_dump()
    team_dict["roster"] = roster
    return team_dict


async def retrieve_teams_projections(
    team_db: DatabaseInterface, character_db: DatabaseInterface
) -> List[TeamProjection]:
    """Retrieve all teams with full character data injected."""
    teams = await team_db.get_all_entities()
    team_dicts = await asyncio.gather(
        *[_inject_character_to_team(team, character_db) for team in teams]
    )
    projected_teams = [TeamProjection(**team_dict) for team_dict in team_dicts]
    return projected_teams


async def get_team(id: str, db: DatabaseInterface) -> Team:
    """Get a team by ID."""
    team = await db.get_entity(id)
    if team:
        return team
    raise TeamNotFoundException(id)


async def retrieve_team_projection(
    id: str, team_db: DatabaseInterface, character_db: DatabaseInterface
) -> TeamProjection:
    """Retrieve a single team with full character data."""
    team = await team_db.get_entity(id)
    if team:
        team_dict = await _inject_character_to_team(team, character_db)
        return TeamProjection(**team_dict)
    raise TeamNotFoundException(id)


async def add_team(new_team: Team, db: DatabaseInterface) -> Team:
    """Add a new team to the database."""
    logger.info(f"Creating new team: {new_team.name}")
    return await db.add_entity(new_team)


async def update_team_data(
    id: str, data: dict, db: DatabaseInterface
) -> Union[bool, UpdateTeam]:
    """Update team data."""
    logger.info(f"Updating team: {id}")
    return await db.update_entity(id, data)


async def delete_team_data(
    id: str, team_db: DatabaseInterface, char_db: DatabaseInterface
) -> bool:
    """Delete a team and all its characters."""
    team = await team_db.get_entity(id)
    if not team:
        raise TeamNotFoundException(id)

    logger.info(f"Deleting team {id} with {len(team.roster)} characters")
    for char_id in team.roster:
        await char_db.delete_entity(char_id)
    return await team_db.delete_entity(id)
