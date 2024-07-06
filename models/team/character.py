import random
import uuid
from enum import Enum
from typing import Optional

from beanie import Document
from pydantic import Field

from models.team.stats import Stats


class Status(Enum):
    HEALTHY = "Healthy"
    INJURED = "Injured"
    DEAD = "Dead"


class Character(Document):
    id: str = Field(default_factory=lambda: uuid.uuid4().hex, init=False)
    team_id: str
    name: str
    number: Optional[str] = str(random.randint(0, 99)).zfill(2)
    character_type: str
    status: Status = Status.HEALTHY
    value: str
    stats: Stats
    perks: list[str]
    image: Optional[str] = None
    image_tag: Optional[str] = None

    class Config:
        pass

    class Settings:
        name = "characters"
        # indexes = [
        #     IndexModel([("team_id", ASCENDING)], name="team_id_index"),
        # ]
