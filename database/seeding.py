"""Auto-seeding database with base catalogs on startup."""

import json
import re
from pathlib import Path


from models.base.roster import BasePerk, BasePlayer, BaseRoster, BaseStats
from models.base.skill_family import SkillFamily
from models.base.star_player import SpecialAbility, StarPlayer, StarPlayerStats
from models.team.perk import Perk
from utils.logging_config import get_db_logger

logger = get_db_logger()

FAMILY_TO_SYMBOL = {
    "agility": "A",
    "devious": "D",
    "general": "G",
    "mutation": "M",
    "passing": "P",
    "strength": "S",
    "trait": "T",
}


async def upsert_catalog_document(document_model, document):
    """Upsert catalog documents without parsing existing legacy documents first."""
    collection = document_model.get_motor_collection()
    await collection.replace_one(
        {"_id": document.id},
        document.model_dump(by_alias=True, exclude_none=True),
        upsert=True,
    )


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
        english_value = get_english_text(value)
        digits = re.sub(r"[^0-9]", "", english_value)
        return int(digits) if digits else 0
    return 0


def get_english_text(value) -> str:
    """Return the English half from bilingual values like 'Dodge / Esquivar'."""
    return str(value or "").split(" / ", 1)[0].strip()


def slugify(value: str) -> str:
    """Convert display text to snake_case identifiers."""
    value = re.sub(r"\([^)]*\)", "", get_english_text(value))
    value = value.replace("'", "").replace("’", "")
    return re.sub(r"_+", "_", re.sub(r"[^A-Za-z0-9]+", "_", value).strip("_").lower())


def parse_max_quantity(value) -> int:
    """Parse max quantity from values like '0-16'."""
    match = re.search(r"(\d+)\s*-\s*(\d+)", str(value or ""))
    if match:
        return int(match.group(2))
    match = re.search(r"\d+", str(value or ""))
    return int(match.group(0)) if match else 1


def parse_skill_access(value) -> list[str]:
    """Parse skill access strings like 'A, S'."""
    text = get_english_text(value)
    if not text or text == "-":
        return []
    return [part.strip() for part in text.split(",") if part.strip()]


def split_top_level_commas(value: str) -> list[str]:
    """Split comma-separated rules while preserving commas inside parentheses."""
    text = get_english_text(value)
    if not text or text.lower() == "none":
        return []
    parts = []
    current = []
    depth = 0
    for char in text:
        if char == "(":
            depth += 1
        elif char == ")" and depth:
            depth -= 1
        if char == "," and depth == 0:
            part = "".join(current).strip()
            if part:
                parts.append(part)
            current = []
        else:
            current.append(char)
    part = "".join(current).strip()
    if part:
        parts.append(part)
    return parts


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


def convert_front_team_to_roster(team_data: dict, perk_lookup: dict) -> BaseRoster:
    """Convert frontend assets/rules/teams.json format to BaseRoster format."""
    team_id = team_data.get("name", "unknown")
    details = team_data.get("team_details", {})
    players = []

    for raw_player in team_data.get("roster", []):
        player_name = get_english_text(raw_player.get("position", "Unknown"))
        player_perks = []
        for raw_perk in raw_player.get("skills_traits", []):
            perk_name = get_english_text(raw_perk)
            if not perk_name or perk_name.lower() == "none":
                continue
            perk_id = slugify(perk_name)
            perk_info = perk_lookup.get(perk_id, {})
            player_perks.append(
                BasePerk(
                    id=perk_id,
                    name=perk_info.get("name", perk_name),
                    category=perk_info.get("category", "G"),
                )
            )

        stats = raw_player.get("stats", {})
        players.append(
            BasePlayer(
                type=f"{team_id}_{slugify(player_name)}",
                name=player_name,
                position=determine_position(player_name),
                max=parse_max_quantity(raw_player.get("qty")),
                cost=parse_cost(raw_player.get("cost", 0)),
                stats=BaseStats(
                    MA=parse_stat_value(stats.get("MA", 5)) or 5,
                    ST=parse_stat_value(stats.get("ST", 3)) or 3,
                    AG=parse_stat_value(stats.get("AG", "4+")) or 4,
                    PA=parse_stat_value(stats.get("PA", "-")),
                    AV=parse_stat_value(stats.get("AV", "8+")) or 8,
                ),
                perks=player_perks,
                primary_access=parse_skill_access(
                    raw_player.get("categories", {}).get("primary", "")
                ),
                secondary_access=parse_skill_access(
                    raw_player.get("categories", {}).get("secondary", "")
                ),
                image=raw_player.get("image"),
                tag_image=raw_player.get("tag_image"),
            )
        )

    return BaseRoster(
        id=team_id,
        name=" ".join(part.capitalize() for part in team_id.split("_")),
        reroll_cost=parse_cost(details.get("rerolls", {}).get("cost", 0)),
        apothecary_allowed=get_english_text(details.get("apothecary", "")).upper()
        in {"YES", "SI", "SÍ"},
        tier=determine_tier(team_id),
        special_rules=split_top_level_commas(details.get("special_rules", "")),
        players=players,
        icon=f"teams/{team_id}/icon.png",
        wallpaper=f"teams/{team_id}/wallpaper.png",
    )


async def seed_skill_families(skills_data: dict) -> dict[str, dict]:
    """Seed skill_families collection."""
    families = skills_data.get("families", [])
    family_lookup = {}

    for fam in families:
        skill_family = SkillFamily(
            id=fam["_id"],
            name=fam["name"],
            symbol=fam["symbol"],
        )
        await upsert_catalog_document(SkillFamily, skill_family)
        family_lookup[fam["_id"]] = {
            "name": fam["name"],
            "symbol": fam["symbol"],
        }

    logger.info(f"Upserted {len(families)} skill families")
    return family_lookup


async def seed_perks(skills_data: dict) -> dict[str, dict]:
    """Seed perks collection."""
    skills = skills_data.get("skills", [])
    perk_lookup = {}

    for skill in skills:
        perk = Perk(
            id=skill["_id"],
            name=skill.get("name"),
            description=skill.get("description"),
            family=skill.get("family", "general"),
            modifier=skill.get("modifier"),
        )
        await upsert_catalog_document(Perk, perk)

        family = skill.get("family", "general")
        perk_lookup[skill["_id"]] = {
            "name": (
                skill.get("name", {}).get("en", skill["_id"])
                if isinstance(skill.get("name"), dict)
                else skill.get("name", skill["_id"])
            ),
            "category": FAMILY_TO_SYMBOL.get(family, "G"),
        }

    logger.info(f"Upserted {len(skills)} perks")
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
    for team in teams_data:
        if "team_details" in team and "roster" in team:
            roster = convert_front_team_to_roster(team, perk_lookup)
        else:
            roster = convert_team_to_roster(team, perk_lookup)
        await upsert_catalog_document(BaseRoster, roster)

    logger.info(f"Upserted {len(teams_data)} base rosters")


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
        logger.info("Starting catalog reconciliation...")

        # Find config directory
        base_dir = Path(__file__).parent.parent

        # Load JSON files
        skills_path = base_dir / "config" / "skills.json"
        teams_path = base_dir / "config" / "base_teams.json"
        star_players_path = base_dir / "config" / "star_players.json"

        if not all(
            [skills_path.exists(), teams_path.exists(), star_players_path.exists()]
        ):
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

        logger.info("Catalog reconciliation completed successfully")

    except Exception as e:
        logger.error(f"Auto-seed failed: {e}")
        raise
