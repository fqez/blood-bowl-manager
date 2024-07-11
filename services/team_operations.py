import asyncio
from typing import List, Type, Union

from database.interfaces.database_interface import DatabaseInterface
from exceptions.exceptions import TeamNotFoundException
from models.team.character import Character
from models.team.team import Team
from schemas.team import TeamProjection, UpdateTeam

character_collection: Type[Character] = Character


async def _inject_character_to_team(team: Team) -> dict:
    roster = []
    for id in team.roster:
        character = await character_collection.get(id)
        roster.append(character.model_dump())
    team_dict = team.model_dump()
    team_dict["roster"] = roster
    return team_dict


async def retrieve_teams_projections(db: DatabaseInterface) -> List[TeamProjection]:
    teams = await db.get_all_entities()
    team_dicts = await asyncio.gather(
        *[_inject_character_to_team(team) for team in teams]
    )
    projected_teams = [TeamProjection(**team_dict) for team_dict in team_dicts]
    return projected_teams


async def get_team(id: str, db: DatabaseInterface) -> Team:
    team = await db.get_entity(id)
    if team:
        return team
    else:
        raise TeamNotFoundException(id)


async def retrieve_team_projection(id: str, db: DatabaseInterface) -> TeamProjection:
    team = await db.get_entity(id)
    if team:
        team_dict = await _inject_character_to_team(team)
        return TeamProjection(**team_dict)
    else:
        raise TeamNotFoundException(id)


async def add_team(new_team: Team, db: DatabaseInterface) -> Team:
    return await db.add_entity(new_team)


async def update_team_data(
    id: str, data: dict, db: DatabaseInterface
) -> Union[bool, UpdateTeam]:
    return await db.update_entity(id, data)


async def delete_team_data(
    id: str, team_db: DatabaseInterface, char_db: DatabaseInterface
) -> bool:
    team = await team_db.get_entity(id)
    if not team:
        raise TeamNotFoundException(id)
    for char_id in team.roster:
        await char_db.delete_entity(char_id)
    return await team_db.delete_entity(id)
