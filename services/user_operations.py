from database.interfaces.database_interface import DatabaseInterface
from models.user.admin import Admin


async def add_admin(new_admin: Admin, db: DatabaseInterface) -> Admin:
    return await db.add_entity(new_admin)


async def get_admin(email: str, db: DatabaseInterface) -> Admin:
    return await db.get_entity(email)
