from fastapi import APIRouter, Body, Depends

from database.database_dependencies import get_character_database, get_team_database
from database.mongo_database import MongoDatabase
from exceptions.exceptions import PlayerNotFoundException, TeamNotFoundException
from models.team.character import Character
from schemas.character import CreateCharacter, UpdateCharacter
from schemas.responses import (
    APIResponse,
    created_response,
    error_response,
    success_response,
)
from services import character_operations

router = APIRouter()


# GET /characters/team/{team_id}
@router.get("/team/{team_id}", response_model=APIResponse)
async def get_characters(
    team_id: str, db: MongoDatabase = Depends(get_character_database)
):
    roster = await character_operations.retrieve_roster(team_id, db)
    if roster:
        return success_response(roster, "Characters retrieved successfully")
    raise TeamNotFoundException(team_id)


# GET /characters/{character_id}
@router.get("/{id}", response_model=APIResponse)
async def get_character(id: str, db: MongoDatabase = Depends(get_character_database)):
    character = await character_operations.retrieve_player(id, db)
    if character:
        return success_response(character, "Character retrieved successfully")
    raise PlayerNotFoundException(id)


# POST /characters
@router.post("/", response_model=APIResponse)
async def create_character(
    char_db: MongoDatabase = Depends(get_character_database),
    team_db: MongoDatabase = Depends(get_team_database),
    character: CreateCharacter = Body(...),
):
    new_character = await character_operations.add_character(
        Character(**character.model_dump()), char_db, team_db
    )
    if new_character:
        return created_response(new_character, "Character created successfully")
    return error_response("Failed to create character")


# PUT /characters/{id}
@router.put("/{id}", response_model=APIResponse)
async def update_character(
    id: str,
    req: UpdateCharacter = Body(...),
    db: MongoDatabase = Depends(get_character_database),
):
    updated_character = await character_operations.update_character_data(
        id, req.model_dump(), db
    )
    if updated_character:
        return success_response(
            updated_character, f"Character {id} updated successfully"
        )
    raise PlayerNotFoundException(id)
