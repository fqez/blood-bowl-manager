from typing import List

from database.interfaces.database_interface import DatabaseInterface
from models.team.perk import Perk

perk_collection: List[Perk]


async def retrieve_perks(db: DatabaseInterface) -> List[Perk]:
    return await db.get_all_entities()


async def retrieve_perk(id: str, db: DatabaseInterface) -> Perk:
    return await db.get_entity(id)
