"""Skill Family model - Categories for grouping skills/traits."""

from beanie import Document
from pydantic import Field


class SkillFamily(Document):
    """
    Skill Family - Category grouping for skills and traits.

    Skill families define the categories that skills belong to,
    such as Agility, Strength, General, etc. Each family has a
    symbol used for quick reference.
    """

    id: str = Field(..., description="Family identifier (e.g., 'agility')")
    name: dict = Field(
        ..., description="Localized name {'en': 'Agility', 'es': 'Agilidad'}"
    )
    symbol: str = Field(
        ..., max_length=2, description="Short symbol (A, G, S, P, M, D, T)"
    )

    class Settings:
        name = "skill_families"

    class Config:
        json_schema_extra = {
            "example": {
                "id": "agility",
                "name": {"en": "Agility", "es": "Agilidad"},
                "symbol": "A",
            }
        }
