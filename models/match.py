import datetime
from typing import Optional

from beanie import Document
from bson import ObjectId
from pydantic import BaseModel, Field

from models.team.character import Status


class MatchScoreModel(BaseModel):
    home: int
    away: int


class MatchStatsModel(BaseModel):
    touchdowns: MatchScoreModel
    casualties: MatchScoreModel
    possession: MatchScoreModel
    passes: MatchScoreModel
    catches: MatchScoreModel


class Match(Document):
    id: str = Field(default_factory=ObjectId, alias="_id")
    tournament_id: str
    home_team_id: str
    away_team_id: str
    date: datetime.datetime
    status: Status = Status.PENDING
    winner: Optional[str] = None
    loser: Optional[str] = None
    draw: bool = False
    stats: MatchStatsModel
    score: MatchScoreModel

    class Config:
        pass

    class Settings:
        name = "matches"
        # indexes = [
        #     IndexModel([("tournament_id", ASCENDING)], name="tournament_id_index"),
        # ]
