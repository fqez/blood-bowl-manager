import random
import uuid
from enum import Enum
from typing import Optional

from pydantic import BaseModel

from models.team.stats import Stats


class Status(Enum):
    HEALTHY = "Healthy"
    INJURED = "Injured"
    DEAD = "Dead"


class Character(BaseModel):
    id: str = uuid.uuid4().hex
    name: str
    number: Optional[str] = str(random.randint(0, 99)).zfill(2)
    character_type: str
    status: Status = Status.HEALTHY
    value: str
    stats: Stats
    perks: list[str]
    image: Optional[str] = None
    image_tag: Optional[str] = None

    def update_stats(self, bonus_stats: Stats):
        self.stats.update_bonus_stats(bonus_stats)
