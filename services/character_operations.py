from typing import List, Type, Union

from database.interfaces.database_interface import DatabaseInterface
from exceptions.exceptions import PlayerNotFoundException, TeamNotFoundException
from models.team.character import Character
from models.team.perk import Perk
from schemas.character import CharacterProjection
from schemas.team import UpdateTeam
from services import team_operations

character_collection: Type[Character] = Character
perk_collection: Type[Perk] = Perk


async def _inject_perks_to_character(character: Character) -> dict:
    perks = []
    for id in character.perks:
        modified = id.split(":")
        perk = await perk_collection.get(modified[0])
        if len(modified) > 1:
            perk.modifier = modified[1]
        perks.append(perk.model_dump())
    character_dict = character.model_dump()
    character_dict["perks"] = perks
    return character_dict


async def retrieve_roster(
    team_id: str, db: DatabaseInterface
) -> List[CharacterProjection]:
    players = await db.get_entities_by_key("team_id", team_id)
    projected_players = [
        CharacterProjection(**await _inject_perks_to_character(player))
        for player in players
    ]
    return projected_players


async def retrieve_player(id: str, db: DatabaseInterface) -> CharacterProjection:
    player = await db.get_entity(id)
    if player:
        player_dict = await _inject_perks_to_character(player)
        return CharacterProjection(**player_dict)
    raise PlayerNotFoundException(id)


async def add_character(
    new_character: Character, char_db: DatabaseInterface, team_db: DatabaseInterface
) -> Character:
    team = await team_operations.get_team(new_character.team_id, team_db)
    if not team:
        raise TeamNotFoundException(new_character.team_id)

    new_char = await char_db.add_entity(new_character)
    if new_char:
        team.roster.append(new_char.id)
        await team_db.update_entity(team.id, team.model_dump())
        return new_char
    raise Exception("Failed to add character")


async def add_characters(
    team_roster: List[str], team_id: str, db: DatabaseInterface
) -> List[Character]:
    for character in team_roster:
        character.team_id = team_id
    return await db.add_entities(team_roster)


async def update_character_data(
    id: str, data: dict, db: DatabaseInterface
) -> Union[bool, UpdateTeam]:
    return await db.update_entity(id, data)


async def delete_character_data(id: str, db: DatabaseInterface) -> bool:
    return await db.delete_entity(id)
