from typing import Optional
from urllib.parse import urlparse

from beanie import init_beanie
from mongomock_motor import AsyncMongoMockClient
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic_settings import BaseSettings
from pymongo.errors import ConnectionFailure

import models as models
from database.seeding import auto_seed_database
from utils.logging_config import get_db_logger

logger = get_db_logger()


class Settings(BaseSettings):
    # database configurations
    DATABASE_URL: Optional[str] = None
    USE_MOCK_DB: bool = False

    # JWT
    secret_key: str = "secret"
    algorithm: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    class Config:
        env_file = ".env"
        from_attributes = True
        extra = "ignore"


async def initiate_database():
    """Initialize database connection and Beanie ODM."""
    try:
        settings = Settings()
        if settings.USE_MOCK_DB:
            client = AsyncMongoMockClient()
            database_name = urlparse(settings.DATABASE_URL or "").path.strip("/")
            database = client[database_name or "blood-manager"]
            logger.info("Using in-memory MongoDB mock database")
        else:
            client = AsyncIOMotorClient(settings.DATABASE_URL)
            await client.admin.command("ping")
            database = client.get_default_database()
            logger.info("Database connection established successfully")
        await init_beanie(database=database, document_models=models.__all__)
        logger.info("Beanie ODM initialized with document models")

        # Auto-seed database with base catalogs if empty
        await auto_seed_database()
    except ConnectionFailure as e:
        logger.error(f"Database connection failed: {e}")
        raise
