from typing import Optional, Union

from beanie import Document, PydanticObjectId
from pymongo import ASCENDING, IndexModel


class Perk(Document):
    id: Union[str, PydanticObjectId]
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
        name = "perks"
        indexes = [
            IndexModel([("family", ASCENDING)], name="perk_family_index"),
            IndexModel([("name", ASCENDING)], name="perk_name_index"),
        ]
