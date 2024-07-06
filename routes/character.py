from fastapi import APIRouter, Body

from database.database import (  # update_character_data,
    add_character,
    add_team,
    retrieve_roster,
    retrieve_team,
    update_team_data,
)
from models.team.team import Team
from schemas.team import CreateTeam, Response, UpdateTeam

router = APIRouter()


# GET /teams
@router.get(
    "/{team_id}",
    response_description="Characters of Team: {team_id} retrieved",
    response_model=Response,
)
async def get_characters(team_id: str):
    roster = await retrieve_roster(team_id)
    return {
        "status_code": 200,
        "response_type": "success",
        "description": "Student data retrieved successfully",
        "data": roster,
    }


# GET /teams/{id}
@router.get(
    "/{id}",
    response_description="Student data retrieved",
    response_model=Response,
)
async def get_team_data(id: str):
    team = await retrieve_team(id)
    if team:
        return {
            "status_code": 200,
            "response_type": "success",
            "description": "Student data retrieved successfully",
            "data": team,
        }
    return {
        "status_code": 404,
        "response_type": "error",
        "description": "Student doesn't exist",
    }


# POST /teams
@router.post(
    "/",
    response_description="Team data added into the database",
    response_model=Response,
)
async def add_team_data(team: CreateTeam = Body(...)):
    roster = []
    for character in team.roster:
        character.team_id = team.id
        roster.append(character.id)
        await add_character(character)
    team.roster = roster
    new_team = await add_team(Team(**team.model_dump()))
    return {
        "status_code": 200,
        "response_type": "success",
        "description": "Student created successfully",
        "data": new_team,
    }


@router.delete("/{id}", response_description="Student data deleted from the database")
async def delete_team_data(id: str):
    deleted_student = await delete_student(id)
    if deleted_student:
        return {
            "status_code": 200,
            "response_type": "success",
            "description": "Student with ID: {} removed".format(id),
            "data": deleted_student,
        }
    return {
        "status_code": 404,
        "response_type": "error",
        "description": "Student with id {0} doesn't exist".format(id),
        "data": False,
    }


@router.put("/{id}", response_model=Response)
async def update_team(
    id: str,
    req: UpdateTeam = Body(...),
):
    updated_team = await update_team_data(id, req.model_dump())
    if updated_team:
        return {
            "status_code": 200,
            "response_type": "success",
            "description": "Student with ID: {} updated".format(id),
            "data": updated_team,
        }
    return {
        "status_code": 404,
        "response_type": "error",
        "description": "An error occurred. Student with ID: {} not found".format(id),
        "data": False,
    }
