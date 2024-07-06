from typing import Optional

from beanie import Document
from pymongo import ASCENDING, IndexModel


class Perk(Document):
    _id: str
    name: Optional[dict] = None
    description: Optional[dict] = None
    family: str
    modifier: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "name": {"en": "Name of the Perk"},
                "description": {"en": "Description of the Perk"},
                "family": "Family of the Perk (General, Strength, etc)",
            }
        }

    class Settings:
        name = "perk"
        indexes = [
            IndexModel([("family", ASCENDING)], name="perk_family_index"),
            IndexModel([("name", ASCENDING)], name="perk_name_index"),
        ]
