"""Script to seed base_rosters collection from base_teams.json."""

import asyncio
import json
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

from config.config import Settings
from models.base.roster import BasePerk, BasePlayer, BaseRoster, BaseStats


def parse_stat_value(value: str) -> int | None:
    """Parse stat value from string format (e.g., '4+', '5', '-')."""
    if value == "-" or value is None:
        return None
    if "+" in value:
        return int(value.replace("+", ""))
    return int(value)


def parse_cost(value: str) -> int:
    """Parse cost from string format (e.g., '40,000' or '40.000')."""
    if isinstance(value, int):
        return value
    return int(value.replace(",", "").replace(".", ""))


def convert_team_to_roster(team_data: dict, perks_data: dict) -> BaseRoster:
    """Convert old team format to new BaseRoster format."""

    players = []
    for char in team_data.get("characters", []):
        # Convert perks
        char_perks = []
        for perk_id in char.get("perks", []):
            # Handle perks with modifiers like "perk-mighty-blow:+1"
            base_perk_id = perk_id.split(":")[0]
            perk_info = perks_data.get(base_perk_id, {})

            # Handle name as dict (translations) or string
            perk_name = perk_info.get(
                "name", perk_id.replace("perk-", "").replace("-", " ").title()
            )
            if isinstance(perk_name, dict):
                perk_name = perk_name.get("en", perk_name.get("es", "Unknown"))

            char_perks.append(
                BasePerk(
                    id=base_perk_id,
                    name=perk_name,
                    category=perk_info.get("category", "G"),
                )
            )

        # Convert stats
        stats = char.get("stats", {})
        base_stats = BaseStats(
            MA=parse_stat_value(stats.get("MA", "5")) or 5,
            ST=parse_stat_value(stats.get("ST", "3")) or 3,
            AG=parse_stat_value(stats.get("AG", "4+")) or 4,
            PA=parse_stat_value(stats.get("PA", "-")),
            AV=parse_stat_value(stats.get("AV", "8+")) or 8,
        )

        player = BasePlayer(
            type=char.get("type", char.get("name", "").lower().replace(" ", "-")),
            name=char.get("name", "Unknown"),
            position=determine_position(char.get("name", "")),
            max=char.get("max", 12),
            cost=parse_cost(char.get("value", "50000")),
            stats=base_stats,
            perks=char_perks,
            primary_access=["G"],  # Default, should be customized per roster
            secondary_access=["A", "S"],
            image=char.get("image"),
            tag_image=char.get("tag_image"),
        )
        players.append(player)

    return BaseRoster(
        id=team_data.get("_id", team_data.get("name", "").lower().replace(" ", "-")),
        name=team_data.get("name", "Unknown"),
        reroll_cost=parse_cost(team_data.get("reroll_value", "60000")),
        apothecary_allowed=not is_undead_team(team_data.get("_id", "")),
        tier=determine_tier(team_data.get("_id", "")),
        special_rules=[],
        players=players,
        icon=f"teams/{team_data.get('_id', 'default')}/icon.png",
        wallpaper=f"teams/{team_data.get('_id', 'default')}/bg.png",
    )


def determine_position(name: str) -> str:
    """Determine position from player name."""
    name_lower = name.lower()
    if "blitzer" in name_lower:
        return "Blitzer"
    if "thrower" in name_lower:
        return "Thrower"
    if "catcher" in name_lower or "runner" in name_lower:
        return "Runner"
    if "blocker" in name_lower or "black orc" in name_lower:
        return "Blocker"
    if "lineman" in name_lower or "linewoman" in name_lower:
        return "Lineman"
    return "Positional"


def is_undead_team(team_id: str) -> bool:
    """Check if team is undead (no apothecary)."""
    undead_teams = [
        "shambling-undead",
        "necromantic-horrors",
        "khemri",
        "nurgles",
        "vampire",
    ]
    return any(u in team_id for u in undead_teams)


def determine_tier(team_id: str) -> int:
    """Determine team tier."""
    tier1 = ["orcs", "humans", "skaven", "dwarfs", "dark-elves", "lizardmen"]
    tier3 = ["ogres", "goblins", "halflings", "snotlings"]

    for t in tier1:
        if t in team_id:
            return 1
    for t in tier3:
        if t in team_id:
            return 3
    return 2


async def seed_base_rosters():
    """Seed base_rosters collection from JSON files."""

    # Connect to database
    settings = Settings()
    client = AsyncIOMotorClient(settings.DATABASE_URL)

    await init_beanie(
        database=client.get_default_database(),
        document_models=[BaseRoster],
    )

    # Load existing data
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    with open(
        os.path.join(base_dir, "config", "base_teams.json"), encoding="utf-8"
    ) as f:
        teams_data = json.load(f)

    with open(os.path.join(base_dir, "config", "perks.json"), encoding="utf-8") as f:
        perks_list = json.load(f)
        perks_data = {p["_id"]: p for p in perks_list}

    # Clear existing data
    await BaseRoster.delete_all()
    print(f"Cleared existing base_rosters")

    # Convert and insert
    for team in teams_data:
        roster = convert_team_to_roster(team, perks_data)
        await roster.insert()
        print(f"Inserted roster: {roster.name} ({len(roster.players)} player types)")

    print(f"\nSeeded {len(teams_data)} rosters successfully!")


if __name__ == "__main__":
    asyncio.run(seed_base_rosters())
