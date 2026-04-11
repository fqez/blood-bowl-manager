from fastapi import APIRouter, Body, Depends, HTTPException

from database.database_dependencies import get_character_database, get_team_database
from database.mongo_database import MongoDatabase
from models.team.team import Team
from schemas.responses import APIResponse, created_response, success_response
from schemas.team import CreateTeam, UpdateTeam
from services import character_operations, team_operations

router = APIRouter()


# GET /teams
@router.get("/", response_model=APIResponse)
async def get_teams(
    team_db: MongoDatabase = Depends(get_team_database),
    character_db: MongoDatabase = Depends(get_character_database),
):
    teams = await team_operations.retrieve_teams_projections(team_db, character_db)
    return success_response(teams, "Teams retrieved successfully")


# GET /teams/{id}
@router.get("/{id}", response_model=APIResponse)
async def get_team_data(
    id: str,
    team_db: MongoDatabase = Depends(get_team_database),
    character_db: MongoDatabase = Depends(get_character_database),
):
    team = await team_operations.retrieve_team_projection(id, team_db, character_db)
    if team:
        return success_response(team, "Team retrieved successfully")
    raise HTTPException(status_code=404, detail="Team not found")


# POST /teams
@router.post("/", response_model=APIResponse)
async def add_team_data(
    db_team: MongoDatabase = Depends(get_team_database),
    db_chara: MongoDatabase = Depends(get_character_database),
    team: CreateTeam = Body(...),
):
    character_ids = [character.id for character in team.roster]
    roster_data = team.roster
    team.roster = character_ids

    new_team = await team_operations.add_team(Team(**team.model_dump()), db_team)
    if new_team:
        await character_operations.add_characters(roster_data, team.id, db_chara)

    return created_response(new_team, "Team created successfully")


# DELETE /teams/{id}
@router.delete("/{id}", response_description="Team data deleted from the database")
async def delete_team_data(
    id: str,
    team_db: MongoDatabase = Depends(get_team_database),
    character_db: MongoDatabase = Depends(get_character_database),
):
    deleted_team = await team_operations.delete_team_data(id, team_db, character_db)
    if deleted_team:
        return success_response(deleted_team, f"Team {id} deleted successfully")
    raise HTTPException(status_code=404, detail=f"Team {id} not found")


# PUT /teams/{id}
@router.put("/{id}", response_model=APIResponse)
async def update_team(
    id: str,
    req: UpdateTeam = Body(...),
    db: MongoDatabase = Depends(get_team_database),
):
    updated_team = await team_operations.update_team_data(id, req.model_dump(), db)
    if updated_team:
        return success_response(updated_team, f"Team {id} updated successfully")
    raise HTTPException(status_code=404, detail=f"Team {id} not found")
