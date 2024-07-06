from fastapi import APIRouter, Body

from database.database import (
    add_team,
    retrieve_team,
    retrieve_teams,
    update_character_data,
)
from models.team.team import Team
from schemas.team import Response, UpdateTeam

router = APIRouter()


@router.get("/", response_description="Teams retrieved", response_model=Response)
async def get_teams():
    teams = await retrieve_teams()
    return {
        "status_code": 200,
        "response_type": "success",
        "description": "Students data retrieved successfully",
        "data": teams,
    }


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
async def add_team_data(team: Team = Body(...)):
    new_team = await add_team(team)
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


@router.put("/{team_id}/character/{character_id}", response_model=Response)
async def update_team(
    team_id: str,
    character_id: str,
    req: UpdateTeam = Body(...),
):
    team = await retrieve_team(team_id)
    if team:
        for character in team.roster:
            if character.id == character_id:
                await update_character_data(team, character, req.dict())
                return {
                    "status_code": 200,
                    "response_type": "success",
                    "description": "Team updated successfully",
                    "data": team,
                }
