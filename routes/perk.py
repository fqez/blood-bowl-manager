from fastapi import APIRouter

from database.database import retrieve_perks
from schemas.perk import Response

router = APIRouter()


@router.get("/", response_description="Perks retrieved", response_model=Response)
async def get_perks():
    perks = await retrieve_perks()
    return {
        "data": perks,  # Ensure this includes 'name' and 'family' fields for each perk
    }
