from fastapi import APIRouter, Depends

from database.database_dependencies import get_perk_database
from database.mongo_database import MongoDatabase
from schemas.perk import Response
from services import perk_operations

router = APIRouter()


@router.get("/", response_description="Perks retrieved", response_model=Response)
async def get_perks(db: MongoDatabase = Depends(get_perk_database)):
    perks = await perk_operations.retrieve_perks(db)
    return {
        "data": perks,  # Ensure this includes 'name' and 'family' fields for each perk
    }


@router.get("/{id}", response_description="Perk retrieved", response_model=Response)
async def get_perk(id: str, db: MongoDatabase = Depends(get_perk_database)):
    perk = await perk_operations.retrieve_perk(id, db)
    return {
        "data": perk,  # Ensure this includes 'name' and 'family' fields for the perk
    }
