from typing import Optional

from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic_settings import BaseSettings
from pymongo.errors import ConnectionFailure

import models as models
from utils.logging_config import get_db_logger

logger = get_db_logger()


class Settings(BaseSettings):
    # database configurations
    DATABASE_URL: Optional[str] = None

    # JWT
    secret_key: str = "secret"
    algorithm: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    class Config:
        env_file = ".env"
        from_attributes = True


async def initiate_database():
    """Initialize database connection and Beanie ODM."""
    try:
        client = AsyncIOMotorClient(Settings().DATABASE_URL)
        await client.admin.command("ping")
        logger.info("Database connection established successfully")
        await init_beanie(
            database=client.get_default_database(), document_models=models.__all__
        )
        logger.info("Beanie ODM initialized with document models")
    except ConnectionFailure as e:
        logger.error(f"Database connection failed: {e}")
        raise

    # Load JSON data from file

    # with open("config/base_teams.json") as f:
    #     data = json.load(f)

    # # Insert data into collection
    # collection = client.get_default_database().get_collection("base_teams")
    # await collection.insert_many(data)
