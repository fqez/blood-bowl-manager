from fastapi import APIRouter, Body, Depends

from database.database_dependencies import get_character_database, get_team_database
from database.mongo_database import MongoDatabase
from exceptions.exceptions import PlayerNotFoundException, TeamNotFoundException
from models.team.character import Character
from schemas.character import CreateCharacter, UpdateCharacter
from schemas.team import Response
from services import character_operations

router = APIRouter()


# DONE
# GET /characters/team/{team_id}
@router.get(
    "/team/{team_id}",
    response_model=Response,
)
async def get_characters(
    team_id: str, db: MongoDatabase = Depends(get_character_database)
):
    roster = await character_operations.retrieve_roster(team_id, db)
    if roster:
        return {
            "status_code": 200,
            "response_type": "success",
            "description": "Student data retrieved successfully",
            "data": roster,
        }
    raise TeamNotFoundException(team_id)


# DONE
# GET /characters/{character_id}
@router.get(
    "/{id}",
    response_model=Response,
)
async def get_character(id: str, db: MongoDatabase = Depends(get_character_database)):
    character = await character_operations.retrieve_player(id, db)
    if character:
        return {
            "status_code": 200,
            "response_type": "success",
            "description": "Student data retrieved successfully",
            "data": character,
        }
    raise PlayerNotFoundException(id)


# DONE
# POST /characters
@router.post(
    "/",
    response_model=Response,
)
async def create_character(
    char_db: MongoDatabase = Depends(get_character_database),
    team_db: MongoDatabase = Depends(get_team_database),
    character: CreateCharacter = Body(...),
):
    new_character = await character_operations.add_character(
        Character(**character.model_dump()), char_db, team_db
    )
    if new_character:
        return {
            "status_code": 201,
            "response_type": "success",
            "description": "Student data created successfully",
            "data": new_character,
        }
    return {
        "status_code": 400,
        "response_type": "error",
        "description": "An error occurred. Student data not created",
        "data": False,
    }


# DONE
@router.put("/{id}", response_model=Response)
async def update_character(
    id: str,
    req: UpdateCharacter = Body(...),
    db: MongoDatabase = Depends(get_character_database),
):
    updated_character = await character_operations.update_character_data(
        id, req.model_dump(), db
    )
    if updated_character:
        return {
            "status_code": 200,
            "response_type": "success",
            "description": "Student with ID: {} updated".format(id),
            "data": updated_character,
        }
    return {
        "status_code": 404,
        "response_type": "error",
        "description": "An error occurred. Student with ID: {} not found".format(id),
        "data": False,
    }
