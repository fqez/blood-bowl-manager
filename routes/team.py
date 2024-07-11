from fastapi import APIRouter, Body, Depends, HTTPException

from database.database_dependencies import get_character_database, get_team_database
from database.mongo_database import MongoDatabase
from models.team.team import Team
from schemas.team import CreateTeam, Response, UpdateTeam
from services import character_operations, team_operations

router = APIRouter()


# GET /teams
@router.get("/", response_model=Response)
async def get_teams(db: MongoDatabase = Depends(get_team_database)):
    teams = await team_operations.retrieve_teams_projections(db)
    return {
        "status_code": 200,
        "response_type": "success",
        "description": "Team data retrieved successfully",
        "data": teams,
    }


# GET /teams/{id}
@router.get(
    "/{id}",
    response_model=Response,
)
async def get_team_data(id: str, db: MongoDatabase = Depends(get_team_database)):
    team = await team_operations.retrieve_team_projection(id, db)
    if team:
        return {
            "status_code": 200,
            "response_type": "success",
            "description": "Team data retrieved successfully",
            "data": team,
        }
    raise HTTPException(status_code=404, detail="Item not found")


# POST /teams
@router.post(
    "/",
    response_model=Response,
)
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

    return {
        "status_code": 200,
        "response_type": "success",
        "description": "Team created successfully",
        "data": new_team,
    }


@router.delete("/{id}", response_description="Team data deleted from the database")
async def delete_team_data(
    id: str,
    team_db: MongoDatabase = Depends(get_team_database),
    character_db: MongoDatabase = Depends(get_character_database),
):

    deleted_Team = await team_operations.delete_team_data(id, team_db, character_db)
    if deleted_Team:
        return {
            "status_code": 200,
            "response_type": "success",
            "description": "Team with ID: {} removed".format(id),
            "data": deleted_Team,
        }
    raise HTTPException(status_code=404, detail=f"Team {id} not found")


@router.put("/{id}", response_model=Response)
async def update_team(
    id: str,
    req: UpdateTeam = Body(...),
    db: MongoDatabase = Depends(get_team_database),
):
    updated_team = await team_operations.update_team_data(id, req.model_dump(), db)
    if updated_team:
        return {
            "status_code": 200,
            "response_type": "success",
            "description": "Team with ID: {} updated".format(id),
            "data": updated_team,
        }
    raise HTTPException(status_code=404, detail=f"Team {id} not found")
