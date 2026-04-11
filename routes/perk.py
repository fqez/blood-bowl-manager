from fastapi import APIRouter, Depends

from database.database_dependencies import get_perk_database
from database.mongo_database import MongoDatabase
from exceptions.exceptions import PerkNotFoundException
from schemas.responses import APIResponse, success_response
from services import perk_operations

router = APIRouter()


@router.get("/", response_description="Perks retrieved", response_model=APIResponse)
async def get_perks(db: MongoDatabase = Depends(get_perk_database)):
    perks = await perk_operations.retrieve_perks(db)
    return success_response(perks, "Perks retrieved successfully")


@router.get("/{id}", response_description="Perk retrieved", response_model=APIResponse)
async def get_perk(id: str, db: MongoDatabase = Depends(get_perk_database)):
    perk = await perk_operations.retrieve_perk(id, db)
    if perk:
        return success_response(perk, "Perk retrieved successfully")
    raise PerkNotFoundException(id)
