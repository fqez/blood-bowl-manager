from dataclasses import dataclass
from typing import Dict


@dataclass
class Stats:
    base_movement: int
    base_strength: int
    base_agility: int
    base_armor_value: int

    bonus_movement: int = 0
    bonus_strength: int = 0
    bonus_agility: int = 0
    bonus_armor_value: int = 0

    def get_movement(self) -> int:
        return self.base_movement + self.bonus_movement

    def get_strength(self) -> int:
        return self.base_strength + self.bonus_strength

    def get_agility(self) -> int:
        return self.base_agility + self.bonus_agility

    def get_armor_value(self) -> int:
        return self.base_armor_value + self.bonus_armor_value

    def get_stats(self) -> Dict[str, int]:
        return {
            "movement": self.get_movement(),
            "strength": self.get_strength(),
            "agility": self.get_agility(),
            "armor_value": self.get_armor_value(),
        }
