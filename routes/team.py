from typing import List

from fastapi import APIRouter, Body

from database.database import (  # update_character_data,
    add_character,
    add_team,
    retrieve_teams,
)
from models.team.team import Team
from schemas.team import CreateTeam, Response, TeamProjection

router = APIRouter()


@router.get(
    "/", response_description="Teams retrieved", response_model=List[TeamProjection]
)
async def get_teams():
    teams = await retrieve_teams()
    return teams


# @router.get(
#     "/{id}", response_description="Student data retrieved", response_model=Response
# )
# async def get_student_data(id: PydanticObjectId):
#     student = await retrieve_student(id)
#     if student:
#         return {
#             "status_code": 200,
#             "response_type": "success",
#             "description": "Student data retrieved successfully",
#             "data": student,
#         }
#     return {
#         "status_code": 404,
#         "response_type": "error",
#         "description": "Student doesn't exist",
#     }


@router.post(
    "/",
    response_description="Student data added into the database",
    response_model=Response,
)
async def add_team_data(team: CreateTeam = Body(...)):
    roster_ids = []
    for character in team.roster:
        character.team_id = team.id
        roster_ids.append(character.id)
        await add_character(character)
    team.roster = roster_ids

    new_team = await add_team(Team(**team.dict()))
    return {
        "status_code": 200,
        "response_type": "success",
        "description": "Student created successfully",
        "data": new_team,
    }


# @router.delete("/{id}", response_description="Student data deleted from the database")
# async def delete_student_data(id: PydanticObjectId):
#     deleted_student = await delete_student(id)
#     if deleted_student:
#         return {
#             "status_code": 200,
#             "response_type": "success",
#             "description": "Student with ID: {} removed".format(id),
#             "data": deleted_student,
#         }
#     return {
#         "status_code": 404,
#         "response_type": "error",
#         "description": "Student with id {0} doesn't exist".format(id),
#         "data": False,
#     }


# @router.put("/{team_id}/character/{character_id}", response_model=Response)
# async def update_team(
#     team_id: str,
#     character_id: str,
#     req: UpdateCharacter = Body(...),
# ):
#     team = await retrieve_team(team_id)
#     if team:
#         for character in team.roster:
#             if character.id == character_id:
#                 await update_character_data(team, character, req.dict())
#                 return {
#                     "status_code": 200,
#                     "response_type": "success",
#                     "description": "Team updated successfully",
#                     "data": team,
# }
