from typing import Optional

from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic_settings import BaseSettings
from pymongo.errors import ConnectionFailure

import models as models


class Settings(BaseSettings):
    # database configurations
    DATABASE_URL: Optional[str] = None

    # JWT
    secret_key: str = "secret"
    algorithm: str = "HS256"

    class Config:
        env_file = ".env"
        from_attributes = True


async def initiate_database():
    try:
        client = AsyncIOMotorClient(Settings().DATABASE_URL)
        await client.admin.command("ping")  # Check the connection
        await init_beanie(
            database=client.get_default_database(), document_models=models.__all__
        )
    except ConnectionFailure:
        print("Database connection failed. Please check your connection settings.")

    # Load JSON data from file

    # with open("config/base_teams.json") as f:
    #     data = json.load(f)

    # # Insert data into collection
    # collection = client.get_default_database().get_collection("base_teams")
    # await collection.insert_many(data)
