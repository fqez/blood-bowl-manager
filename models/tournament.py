from typing import List

from beanie import Document
from bson import ObjectId
from pydantic import Field


class Torunament(Document):

    id: str = Field(default_factory=ObjectId, alias="_id")
    name: str
    teams: List[str]
    matches: List[str]
    fixtures: List[str]  # This is a list of match ids
    BUDGET: float
