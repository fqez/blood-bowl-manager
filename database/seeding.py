"""Auto-seeding database with base catalogs on startup."""

import asyncio
import json
import os
from pathlib import Path

from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

from models.base.roster import BasePerk, BasePlayer, BaseRoster, BaseStats
from models.base.skill_family import SkillFamily
from models.base.star_player import SpecialAbility, StarPlayer, StarPlayerStats
from models.team.perk import Perk
from utils.logging_config import get_db_logger

logger = get_db_logger()


def parse_stat_value(value) -> int | None:
    """Parse stat value from string format (e.g., '4+', '5', '-') or int."""
    if value is None or value == "-":
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        if value == "-":
            return None
        if "+" in value:
            return int(value.replace("+", ""))
        return int(value)
    return None


def parse_cost(value) -> int:
    """Parse cost from string format (e.g., '40,000' or '40.000') or int."""
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        return int(value.replace(",", "").replace(".", ""))
    return 0


def normalize_perk_name_to_id(perk_name: str) -> str:
    """Convert perk display name to snake_case ID."""
    perk_id = perk_name.lower()
    perk_id = perk_id.replace("'", "")
    perk_id = perk_id.replace("-", "_")
    perk_id = perk_id.replace(" ", "_")
    perk_id = perk_id.replace("(", "").replace(")", "")
    perk_id = perk_id.replace("+", "_plus")
    return perk_id


def determine_position(name: str) -> str:
    """Determine position from player name."""
    name_lower = name.lower()
    if "blitzer" in name_lower:
        return "Blitzer"
    if "thrower" in name_lower:
        return "Thrower"
    if "catcher" in name_lower:
        return "Catcher"
    if "runner" in name_lower:
        return "Runner"
    if "blocker" in name_lower:
        return "Blocker"
    if "lineman" in name_lower or "linewoman" in name_lower:
        return "Lineman"
    if "big guy" in name_lower or "ogre" in name_lower or "troll" in name_lower:
        return "Big Guy"
    return "Positional"


def is_undead_team(team_id: str) -> bool:
    """Check if team is undead (no apothecary)."""
    undead_teams = [
        "shambling_undead",
        "necromantic",
        "khemri",
        "tomb_kings",
        "nurgle",
        "vampire",
    ]
    return any(u in team_id for u in undead_teams)


def determine_tier(team_id: str) -> int:
    """Determine team tier."""
    tier1 = ["orc", "human", "skaven", "dwarf", "dark_elf", "lizardmen", "wood_elf"]
    tier3 = ["ogre", "goblin", "halfling", "snotling", "gnome"]

    for t in tier1:
        if t in team_id:
            return 1
    for t in tier3:
        if t in team_id:
            return 3
    return 2


async def seed_skill_families(skills_data: dict) -> dict[str, dict]:
    """Seed skill_families collection."""
    families = skills_data.get("families", [])

    existing_count = await SkillFamily.find().count()
    if existing_count > 0:
        logger.info(f"Skill families already seeded ({existing_count} found)")
        return {fam["_id"]: {"name": fam["name"], "symbol": fam["symbol"]} 
                for fam in families}

    family_lookup = {}
    for fam in families:
        skill_family = SkillFamily(
            id=fam["_id"],
            name=fam["name"],
            symbol=fam["symbol"],
        )
        await skill_family.insert()
        family_lookup[fam["_id"]] = {
            "name": fam["name"],
            "symbol": fam["symbol"],
        }
    
    logger.info(f"Seeded {len(families)} skill families")
    return family_lookup


async def seed_perks(skills_data: dict) -> dict[str, dict]:
    """Seed perks collection."""
    skills = skills_data.get("skills", [])

    existing_count = await Perk.find().count()
    if existing_count > 0:
        logger.info(f"Perks already seeded ({existing_count} found)")
        skills_list = await Perk.find_all().to_list()
        perk_lookup = {}
        for perk in skills_list:
            family_to_symbol = {
                "agility": "A",
                "devious": "D",
                "general": "G",
                "mutation": "M",
                "passing": "P",
                "strength": "S",
                "trait": "T",
            }
            perk_lookup[perk.id] = {
                "name": perk.name,
                "category": family_to_symbol.get(perk.family, "G"),
            }
        return perk_lookup

    perk_lookup = {}
    for skill in skills:
        perk = Perk(
            id=skill["_id"],
            name=skill.get("name"),
            description=skill.get("description"),
            family=skill.get("family", "general"),
            modifier=skill.get("modifier"),
        )
        await perk.insert()

        family = skill.get("family", "general")
        family_to_symbol = {
            "agility": "A",
            "devious": "D",
            "general": "G",
            "mutation": "M",
            "passing": "P",
            "strength": "S",
            "trait": "T",
        }
        perk_lookup[skill["_id"]] = {
            "name": skill.get("name", {}).get("en", skill["_id"]) if isinstance(skill.get("name"), dict) else skill.get("name", skill["_id"]),
            "category": family_to_symbol.get(family, "G"),
        }

    logger.info(f"Seeded {len(skills)} perks")
    return perk_lookup


def convert_team_to_roster(team_data: dict, perk_lookup: dict) -> BaseRoster:
    """Convert team format to BaseRoster format."""
    players = []
    for char in team_data.get("characters", []):
        char_perks = []
        for perk_name in char.get("perks", []):
            perk_id = normalize_perk_name_to_id(perk_name)
            perk_info = perk_lookup.get(perk_id, {})

            char_perks.append(
                BasePerk(
                    id=perk_id,
                    name=perk_info.get("name", perk_name),
                    category=perk_info.get("category", "G"),
                )
            )

        stats = char.get("stats", {})
        base_stats = BaseStats(
            MA=parse_stat_value(stats.get("MA", 5)) or 5,
            ST=parse_stat_value(stats.get("ST", 3)) or 3,
            AG=parse_stat_value(stats.get("AG", "4+")) or 4,
            PA=parse_stat_value(stats.get("PA", "-")),
            AV=parse_stat_value(stats.get("AV", "8+")) or 8,
        )

        player_type = char.get("type", "").lower().replace(" ", "_")

        player = BasePlayer(
            type=player_type or char.get("name", "").lower().replace(" ", "-"),
            name=char.get("name", "Unknown"),
            position=determine_position(char.get("name", "")),
            max=char.get("max", 12),
            cost=parse_cost(char.get("value", 50000)),
            stats=base_stats,
            perks=char_perks,
            primary_access=["G"],
            secondary_access=["A", "S"],
            image=char.get("image"),
            tag_image=char.get("tag_image"),
        )
        players.append(player)

    team_id = team_data.get("_id", team_data.get("name", "").lower().replace(" ", "_"))

    return BaseRoster(
        id=team_id,
        name=team_data.get("name", "Unknown"),
        reroll_cost=parse_cost(team_data.get("reroll_value", 60000)),
        apothecary_allowed=not is_undead_team(team_id),
        tier=determine_tier(team_id),
        special_rules=[],
        players=players,
        icon=f"teams/{team_id}/icon.png",
        wallpaper=f"teams/{team_id}/bg.png",
    )


async def seed_base_rosters(teams_data: list, perk_lookup: dict):
    """Seed base_rosters collection."""
    existing_count = await BaseRoster.find().count()
    if existing_count > 0:
        logger.info(f"Base rosters already seeded ({existing_count} found)")
        return

    for team in teams_data:
        roster = convert_team_to_roster(team, perk_lookup)
        await roster.insert()

    logger.info(f"Seeded {len(teams_data)} base rosters")


def convert_star_player(sp_data: dict) -> StarPlayer:
    """Convert star player JSON to StarPlayer model."""
    stats = sp_data.get("stats", {})

    star_stats = StarPlayerStats(
        MA=parse_stat_value(stats.get("MA", 5)) or 5,
        ST=parse_stat_value(stats.get("ST", 3)) or 3,
        AG=parse_stat_value(stats.get("AG", "4+")) or 4,
        PA=parse_stat_value(stats.get("PA", "-")),
        AV=parse_stat_value(stats.get("AV", "8+")) or 8,
    )

    special_ability = None
    if sp_data.get("special_ability"):
        special_ability = SpecialAbility(
            name=sp_data["special_ability"].get("name", ""),
            description=sp_data["special_ability"].get("description", ""),
        )

    return StarPlayer(
        id=sp_data.get("_id", sp_data.get("name", "").lower().replace(" ", "_")),
        name=sp_data.get("name", "Unknown"),
        cost=parse_cost(sp_data.get("cost", 100000)),
        stats=star_stats,
        player_types=sp_data.get("type", []),
        skills=sp_data.get("skills", []),
        special_ability=special_ability,
        plays_for=sp_data.get("plays_for", []),
        image=sp_data.get("image"),
    )


async def seed_star_players(star_players_data: list):
    """Seed star_players collection."""
    existing_count = await StarPlayer.find().count()
    if existing_count > 0:
        logger.info(f"Star players already seeded ({existing_count} found)")
        return

    for sp in star_players_data:
        star_player = convert_star_player(sp)
        await star_player.insert()

    logger.info(f"Seeded {len(star_players_data)} star players")


async def auto_seed_database():
    """Auto-seed database with base catalogs if empty."""
    try:
        # Check if database has any data
        perk_count = await Perk.find().count()
        roster_count = await BaseRoster.find().count()
        star_count = await StarPlayer.find().count()

        if perk_count > 0 and roster_count > 0 and star_count > 0:
            logger.info("Database already seeded - skipping auto-seed")
            return

        logger.info("Starting auto-seed of database catalogs...")

        # Find config directory
        base_dir = Path(__file__).parent.parent

        # Load JSON files
        skills_path = base_dir / "config" / "skills.json"
        teams_path = base_dir / "config" / "base_teams.json"
        star_players_path = base_dir / "config" / "star_players.json"

        if not all([skills_path.exists(), teams_path.exists(), star_players_path.exists()]):
            logger.warning("Some JSON config files are missing - skipping auto-seed")
            return

        with open(skills_path, encoding="utf-8-sig") as f:
            skills_data = json.load(f)
        with open(teams_path, encoding="utf-8-sig") as f:
            teams_data = json.load(f)
        with open(star_players_path, encoding="utf-8-sig") as f:
            star_players_data = json.load(f)

        # Seed in order
        family_lookup = await seed_skill_families(skills_data)
        perk_lookup = await seed_perks(skills_data)
        await seed_base_rosters(teams_data, perk_lookup)
        await seed_star_players(star_players_data)

        logger.info("Auto-seed completed successfully")

    except Exception as e:
        logger.error(f"Auto-seed failed: {e}")
        raise
