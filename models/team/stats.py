from dataclasses import field
from typing import Dict, Optional

from pydantic import BaseModel


class Stats(BaseModel):
    MA: str
    ST: str
    AG: str
    PA: str
    AV: str

    bonus_stats: Optional[Dict[str, int]] = field(default_factory=dict)

    def update_bonus_stats(self, stats: dict[str,]) -> None:
        self.bonus_stats.update(stats)

    def get_stat(self, key: str) -> str:
        value = 0
        stat = self.stats[key]
        if "+" in stat:
            value = int(stat[:-1])
            return f"{value + self.bonus_stats.get(key, 0)}+"
        else:
            value = int(stat)
            return f"{value + self.bonus_stats.get(key, 0)}"

    def to_dict(self) -> Dict[str, str]:
        return {
            "MA": self.get_stat("MA"),
            "ST": self.get_stat("ST"),
            "AG": self.get_stat("AG"),
            "PA": self.get_stat("PA"),
            "AV": self.get_stat("AV"),
        }
