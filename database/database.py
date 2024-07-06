from typing import List, Union

from beanie import PydanticObjectId

from models.student import Student
from models.team.character import Character
from models.team.perk import Perk
from models.team.team import Team
from models.user.admin import Admin
from schemas.character import CharacterProjection
from schemas.team import TeamProjection, UpdateTeam

admin_collection = Admin
student_collection = Student
perk_collection = Perk
team_collection = Team
character_collection = Character


async def add_admin(new_admin: Admin) -> Admin:
    admin = await new_admin.create()
    return admin


# Perks CRUD


async def retrieve_perks() -> List[Perk]:
    perks = await perk_collection.all().to_list()
    return perks


async def retrieve_perk(id: str) -> Perk:
    perk = await perk_collection.get(id)
    if perk:
        return perk


# Teams CRUD†


async def _add_character_to_team(team: Team) -> dict:
    roster = []
    for id in team.roster:
        character = await character_collection.get(id)
        roster.append(character.model_dump())
    team_dict = team.model_dump()

    team_dict["roster"] = roster

    return team_dict


async def retrieve_teams() -> List[TeamProjection]:
    teams = await team_collection.find().to_list()
    projected_teams = []
    for team in teams:
        team_dict = await _add_character_to_team(team)
        projected_team = TeamProjection(**team_dict)
        projected_teams.append(projected_team)
    return projected_teams


async def retrieve_team(id: str) -> Team:
    team = await team_collection.get(id)
    if team:
        team_dict = await _add_character_to_team(team)
        return TeamProjection(**team_dict)


async def add_team(new_team: Team) -> Team:
    team = await new_team.create()
    return team


async def update_team_data(id: str, data: dict) -> Union[bool, UpdateTeam]:
    des_body = {k: v for k, v in data.items() if v is not None}
    update_query = {"$set": {field: value for field, value in des_body.items()}}
    team = await team_collection.get(id)
    if team:
        await team.update(update_query)
        return team


# Characters CRUD


async def _add_perks_to_character(character: Character) -> dict:
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


async def retrieve_roster(team_id: str) -> List[CharacterProjection]:
    players = await character_collection.find({"team_id": team_id}).to_list()
    projected_players = []
    for player in players:
        player_dict = await _add_perks_to_character(player)
        projected_player = CharacterProjection(**player_dict)
        projected_players.append(projected_player)
    return projected_players


async def retrieve_player(id: str) -> CharacterProjection:
    player = await character_collection.get(id)
    if player:
        player_dict = await _add_perks_to_character(player)
        return CharacterProjection(**player_dict)


async def add_character(new_character: Character) -> Character:
    character = await new_character.create()
    return character


# ------------------------------------------------


async def retrieve_students() -> List[Student]:
    students = await student_collection.all().to_list()
    return students


async def add_student(new_student: Student) -> Student:
    student = await new_student.create()
    return student


async def retrieve_student(id: PydanticObjectId) -> Student:
    student = await student_collection.get(id)
    if student:
        return student


async def delete_student(id: PydanticObjectId) -> bool:
    student = await student_collection.get(id)
    if student:
        await student.delete()
        return True


# async def update_student_data(id: PydanticObjectId, data: dict) -> Union[bool, Student]:
#     des_body = {k: v for k, v in data.items() if v is not None}
#     update_query = {"$set": {field: value for field, value in des_body.items()}}
#     student = await student_collection.get(id)
#     if student:
#         await student.update(update_query)
#         return student
#     return False
