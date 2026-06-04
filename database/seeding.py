"""Auto-seeding database with base catalogs on startup."""

import json
import re
from datetime import datetime
from pathlib import Path

from models.base.advancement import (
    AdvancementCostRow,
    AdvancementRules,
    AdvancementValueIncrease,
    CharacteristicImprovementResult,
    RandomPrimarySkillTableEntry,
    SkillCategoryRule,
)
from models.base.dedicated_fans import DedicatedFansRules
from models.base.expensive_mistake import (
    ExpensiveMistakeBand,
    ExpensiveMistakeEffect,
    ExpensiveMistakesRules,
    LocalizedText,
)
from models.base.inducement import (
    InducementBudgetRules,
    InducementCostOption,
    InducementRule,
    InducementRules,
    PrayerToNuffleResult,
)
from models.base.injury import (
    CasualtyTableEntry,
    DiceTableEntry,
    InjuryRules,
    LastingInjuryTableEntry,
)
from models.base.league_points import LeaguePointsRules
from models.base.pre_match import DiceRangeTableEntry, KickoffEventRules, WeatherRules
from models.base.roster import BasePerk, BasePlayer, BaseRoster, BaseStats
from models.base.skill_family import SkillFamily
from models.base.spp import SppEventReward, SppRewardsRules, ThrowTeammateReward
from models.base.star_player import SpecialAbility, StarPlayer, StarPlayerStats
from models.base.winnings import WinningsRules
from models.team.perk import Perk
from models.user_team.team import UserTeam
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


def get_localized_text(value, fallback: str = "") -> str:
    """Return Spanish text when available, otherwise English or fallback."""
    if isinstance(value, dict):
        text = value.get("es") or value.get("en") or fallback
        return str(text or fallback).strip()
    return str(value or fallback).strip()


def slugify(value: str) -> str:
    """Convert display text to snake_case identifiers."""
    value = re.sub(r"\([^)]*\)", "", get_english_text(value))
    value = value.replace("'", "").replace("’", "")
    return re.sub(r"_+", "_", re.sub(r"[^A-Za-z0-9]+", "_", value).strip("_").lower())


def normalize_catalog_perk_id(value: str | None) -> str:
    """Normalize embedded perk references to canonical underscore IDs."""
    raw = str(value or "").strip()
    if not raw:
        return ""
    if raw.startswith("perk-"):
        normalized = raw.removeprefix("perk-").replace("-", "_")
    elif re.fullmatch(r"[a-z0-9_]+", raw):
        normalized = raw
    else:
        normalized = slugify(raw)

    aliases = {
        "plague_ridden": "infected",
    }
    return aliases.get(normalized, normalized)


def extract_perk_parameter(value: str) -> str | None:
    """Extract roster-specific values from perks like 'Bloodlust (2+)'."""
    match = re.search(r"\(([^)]+)\)", get_english_text(value))
    if not match:
        return None
    parameter = match.group(1).strip()
    return parameter or None


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
    tiers = {
        "amazon": 1,
        "chaos_dwarf": 1,
        "dark_elf": 1,
        "dwarf": 1,
        "high_elf": 1,
        "lizardmen": 1,
        "norse": 1,
        "old_world_alliance": 1,
        "underworld_denizens": 1,
        "wood_elf": 1,
        "bretonnian": 2,
        "elven_union": 2,
        "human": 2,
        "imperial_nobility": 2,
        "necromantic_horror": 2,
        "orc": 2,
        "shambling_undead": 2,
        "skaven": 2,
        "tomb_kings": 2,
        "vampire": 2,
        "black_orc": 3,
        "chaos_chosen": 3,
        "chaos_renegades": 3,
        "khorne": 3,
        "nurgle": 3,
        "gnome": 4,
        "goblin": 4,
        "halfling": 4,
        "ogre": 4,
        "snotling": 4,
    }
    return tiers.get(team_id, 2)


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
            perk_parameter = extract_perk_parameter(perk_name)
            perk_info = perk_lookup.get(perk_id, {})
            player_perks.append(
                BasePerk(
                    id=perk_id,
                    name=perk_info.get("display_name", perk_name),
                    parameter=perk_parameter,
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
    canonical_ids = {skill["_id"] for skill in skills if skill.get("_id")}

    for skill in skills:
        family = skill.get("family", "general").lower()
        kind = skill.get("kind") or ("trait" if family == "trait" else "skill")
        perk = Perk(
            id=skill["_id"],
            name=skill.get("name"),
            description=skill.get("description"),
            family=family,
            kind=kind,
            use=skill.get("use") or skill.get("type"),
            required=skill.get("required", skill.get("mandatory", False)),
            elite=skill.get("elite", kind == "trait"),
            modifier=skill.get("modifier"),
        )
        await upsert_catalog_document(Perk, perk)

        lookup_data = {
            "display_name": get_localized_text(skill.get("name"), skill["_id"]),
            "category": FAMILY_TO_SYMBOL.get(family, "G"),
        }
        perk_lookup[skill["_id"]] = lookup_data
        perk_lookup[f"perk-{skill['_id'].replace('_', '-')}"] = lookup_data

    if canonical_ids:
        await Perk.find({"_id": {"$nin": list(canonical_ids)}}).delete()

    logger.info(f"Upserted {len(skills)} perks")
    return perk_lookup


def convert_team_to_roster(team_data: dict, perk_lookup: dict) -> BaseRoster:
    """Convert team format to BaseRoster format."""
    players = []
    for char in team_data.get("characters", []):
        char_perks = []
        for perk_name in char.get("perks", []):
            perk_id = slugify(perk_name)
            perk_parameter = extract_perk_parameter(perk_name)
            perk_info = perk_lookup.get(perk_id, {})

            char_perks.append(
                BasePerk(
                    id=perk_id,
                    name=perk_info.get("display_name", perk_name),
                    parameter=perk_parameter,
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
    canonical_ids = {sp.get("_id") for sp in star_players_data if sp.get("_id")}

    for sp in star_players_data:
        star_player = convert_star_player(sp)
        await upsert_catalog_document(StarPlayer, star_player)

    if canonical_ids:
        await StarPlayer.find({"_id": {"$nin": list(canonical_ids)}}).delete()

    logger.info(f"Upserted {len(star_players_data)} star players")


async def reconcile_user_team_perk_names(perk_lookup: dict[str, dict]):
    """Refresh embedded user-team perk names from the canonical skills catalog."""
    teams = await UserTeam.find_all().to_list()
    updated_teams = 0

    for team in teams:
        changed = False
        for player in team.players:
            for perk in player.perks:
                canonical_id = normalize_catalog_perk_id(perk.id or perk.name)
                if not canonical_id:
                    continue

                perk_info = (
                    perk_lookup.get(canonical_id)
                    or perk_lookup.get(perk.id)
                    or perk_lookup.get(f"perk-{canonical_id.replace('_', '-')}")
                )
                if not perk_info:
                    continue

                display_name = perk_info.get("display_name", perk.name)
                category = perk_info.get("category", perk.category)

                if perk.id != canonical_id:
                    perk.id = canonical_id
                    changed = True
                if perk.name != display_name:
                    perk.name = display_name
                    changed = True
                if category and perk.category != category:
                    perk.category = category
                    changed = True

        if changed:
            team.updated_at = datetime.utcnow()
            await team.save()
            updated_teams += 1

    logger.info(f"Reconciled perk names in {updated_teams} user teams")


async def seed_expensive_mistakes_rules():
    """Seed the Expensive Mistakes table from the core rules."""
    rules = ExpensiveMistakesRules(
        id="expensive_mistakes",
        min_treasury=100_000,
        bands=[
            ExpensiveMistakeBand(
                min_treasury=100_000,
                max_treasury=195_000,
                results=[
                    "minor_incident",
                    "crisis_avoided",
                    "crisis_avoided",
                    "crisis_avoided",
                    "crisis_avoided",
                    "crisis_avoided",
                ],
            ),
            ExpensiveMistakeBand(
                min_treasury=200_000,
                max_treasury=295_000,
                results=[
                    "minor_incident",
                    "minor_incident",
                    "crisis_avoided",
                    "crisis_avoided",
                    "crisis_avoided",
                    "crisis_avoided",
                ],
            ),
            ExpensiveMistakeBand(
                min_treasury=300_000,
                max_treasury=395_000,
                results=[
                    "major_incident",
                    "minor_incident",
                    "minor_incident",
                    "crisis_avoided",
                    "crisis_avoided",
                    "crisis_avoided",
                ],
            ),
            ExpensiveMistakeBand(
                min_treasury=400_000,
                max_treasury=495_000,
                results=[
                    "major_incident",
                    "major_incident",
                    "minor_incident",
                    "minor_incident",
                    "crisis_avoided",
                    "crisis_avoided",
                ],
            ),
            ExpensiveMistakeBand(
                min_treasury=500_000,
                max_treasury=595_000,
                results=[
                    "catastrophe",
                    "major_incident",
                    "major_incident",
                    "minor_incident",
                    "minor_incident",
                    "crisis_avoided",
                ],
            ),
            ExpensiveMistakeBand(
                min_treasury=600_000,
                max_treasury=None,
                results=[
                    "catastrophe",
                    "catastrophe",
                    "major_incident",
                    "major_incident",
                    "minor_incident",
                    "minor_incident",
                ],
            ),
        ],
        effects=[
            ExpensiveMistakeEffect(
                code="crisis_avoided",
                label=LocalizedText(en="Crisis Averted", es="Crisis evitada"),
                description=LocalizedText(
                    en="No treasury is lost.", es="No se pierde tesorería."
                ),
                calculation="none",
                required_dice=[],
            ),
            ExpensiveMistakeEffect(
                code="minor_incident",
                label=LocalizedText(en="Minor Incident", es="Incidente menor"),
                description=LocalizedText(
                    en="Lose 1D3 × 10,000 gp.",
                    es="Pierdes 1D3 × 10.000 mo.",
                ),
                calculation="lose_d3_x_10000",
                required_dice=["d3"],
            ),
            ExpensiveMistakeEffect(
                code="major_incident",
                label=LocalizedText(en="Major Incident", es="Incidente mayor"),
                description=LocalizedText(
                    en="Lose half your treasury, rounded down to the nearest 5,000 gp.",
                    es="Pierdes la mitad de tu tesorería, redondeando hacia abajo a las 5.000 mo más cercanas.",
                ),
                calculation="lose_half_round_down_5000",
                required_dice=[],
            ),
            ExpensiveMistakeEffect(
                code="catastrophe",
                label=LocalizedText(en="Catastrophe", es="Catástrofe"),
                description=LocalizedText(
                    en="Your treasury is emptied except 2D6 × 10,000 gp.",
                    es="Tu tesorería queda vacía salvo 2D6 × 10.000 mo.",
                ),
                calculation="keep_2d6_x_10000",
                required_dice=["d6", "d6"],
            ),
        ],
    )
    await upsert_catalog_document(ExpensiveMistakesRules, rules)
    logger.info("Upserted expensive mistakes rules")


async def seed_spp_rewards_rules():
    """Seed SPP reward rules from the core rules."""
    rules = SppRewardsRules(
        id="spp_rewards",
        event_rewards=[
            SppEventReward(
                event_type="completion",
                spp=1,
                career_stat="completions",
                description=LocalizedText(
                    en="A Pass Action that results in an Accurate Pass, and is caught by a team-mate without the ball hitting the ground and Bouncing, awards 1 SPP to the passer.",
                    es="Una acción de Pase que resulta en Pase Preciso y es atrapada por un compañero sin que el balón toque el suelo ni Rebote otorga 1 PX al lanzador.",
                ),
            ),
            SppEventReward(
                event_type="interception",
                spp=2,
                career_stat="interceptions",
                description=LocalizedText(
                    en="Successfully Intercepting an opposition Pass Action awards 2 SPP to the interceptor.",
                    es="Interceptar con éxito una acción de Pase rival otorga 2 PX al interceptor.",
                ),
            ),
            SppEventReward(
                event_type="casualty",
                spp=2,
                career_stat="casualties",
                description=LocalizedText(
                    en="A Casualty caused by a player Knocked Down as a result of a Block Action awards 2 SPP to the player who knocked them down. Casualties from other methods do not generate SPP.",
                    es="Una Baja causada por un jugador Derribado como resultado de una acción de Placaje otorga 2 PX al jugador que lo derribó. Las bajas por otros métodos no generan PX.",
                ),
            ),
            SppEventReward(
                event_type="touchdown",
                spp=3,
                career_stat="touchdowns",
                description=LocalizedText(
                    en="A Touchdown awards 3 SPP to the scorer. Touchdowns awarded because an opponent concedes may be allocated to chosen players on that team.",
                    es="Un Touchdown otorga 3 PX al anotador. Los touchdowns otorgados porque el rival concede pueden asignarse a jugadores elegidos de ese equipo.",
                ),
            ),
        ],
        mvp_spp=4,
        non_spp_event_types=[
            "badly_hurt",
            "foul",
            "kickoff_change",
            "ko",
            "reroll_change",
            "rip",
            "score_change",
            "serious_injury",
            "stall",
            "stalling",
            "stun",
            "turn_change",
            "weather_change",
        ],
        throw_teammate=ThrowTeammateReward(
            thrown_player_landed_spp=1,
            superb_thrower_spp=1,
            description=LocalizedText(
                en="If the thrown player lands standing, the thrown player gets 1 SPP. If the throw was superb too, the thrower also gets 1 SPP.",
                es="Si el jugador lanzado cae de pie, gana 1 PX. Si además el lanzamiento fue soberbio, el lanzador también gana 1 PX.",
            ),
        ),
    )
    await upsert_catalog_document(SppRewardsRules, rules)
    logger.info("Upserted SPP reward rules")


async def seed_advancement_rules():
    """Seed player advancement rules from the core rules."""

    def level(number: int, en: str, es: str, costs: tuple[int, int, int, int]):
        random_primary, choose_primary, choose_secondary, characteristic = costs
        return AdvancementCostRow(
            advancement_number=number,
            level_name=LocalizedText(en=en, es=es),
            random_primary_skill=random_primary,
            choose_primary_skill=choose_primary,
            choose_secondary_skill=choose_secondary,
            characteristic_improvement=characteristic,
        )

    def characteristic(
        min_roll: int, max_roll: int, choices: list[str], en: str, es: str
    ):
        return CharacteristicImprovementResult(
            min_roll=min_roll,
            max_roll=max_roll,
            choices=choices,
            description=LocalizedText(en=en, es=es),
        )

    def category(symbol: str, family: str, en: str, es: str):
        return SkillCategoryRule(
            symbol=symbol,
            family=family,
            name=LocalizedText(en=en, es=es),
        )

    def random_primary_entry(
        first_d6_min: int,
        first_d6_max: int,
        second_d6: int,
        perk_ids: list[str],
    ):
        return RandomPrimarySkillTableEntry(
            first_d6_min=first_d6_min,
            first_d6_max=first_d6_max,
            second_d6=second_d6,
            perk_ids=perk_ids,
        )

    rules = AdvancementRules(
        id="advancement_rules",
        max_advancements=6,
        max_characteristic_improvements_per_stat=2,
        random_skill_rolls=2,
        random_skill_dice="2D6",
        cost_table=[
            level(1, "Experienced (1st)", "Experimentado (1ª)", (3, 6, 10, 14)),
            level(2, "Veteran (2nd)", "Veterano (2ª)", (4, 8, 12, 16)),
            level(3, "Emerging Star (3rd)", "Estrella Emergente (3ª)", (6, 12, 16, 20)),
            level(4, "Star (4th)", "Estrella (4ª)", (8, 16, 20, 24)),
            level(5, "Superstar (5th)", "Superestrella (5ª)", (10, 20, 24, 28)),
            level(6, "Legend (6th)", "Leyenda (6ª)", (15, 30, 34, 38)),
        ],
        characteristic_table=[
            characteristic(
                1,
                1,
                ["AV"],
                "Improve the player's AV by 1.",
                "Mejora la AV del jugador en 1.",
            ),
            characteristic(
                2,
                2,
                ["AV", "PA"],
                "Improve the player's AV or PA by 1.",
                "Mejora la AV o PA del jugador en 1.",
            ),
            characteristic(
                3,
                4,
                ["AV", "MA", "PA"],
                "Improve the player's AV, MA or PA by 1.",
                "Mejora la AV, MA o PA del jugador en 1.",
            ),
            characteristic(
                5,
                5,
                ["MA", "PA"],
                "Improve the player's MA or PA by 1.",
                "Mejora la MA o PA del jugador en 1.",
            ),
            characteristic(
                6,
                6,
                ["AG", "MA"],
                "Improve the player's AG or MA by 1.",
                "Mejora la AG o MA del jugador en 1.",
            ),
            characteristic(
                7,
                7,
                ["AG", "ST"],
                "Improve the player's AG or ST by 1.",
                "Mejora la AG o ST del jugador en 1.",
            ),
            characteristic(
                8,
                8,
                ["MA", "ST", "AG", "PA", "AV"],
                "Improve a Characteristic of your choice by 1.",
                "Mejora un Atributo de tu elección en 1.",
            ),
        ],
        value_increases=[
            AdvancementValueIncrease(advancement_type="primary_skill", value=20000),
            AdvancementValueIncrease(advancement_type="secondary_skill", value=40000),
            AdvancementValueIncrease(advancement_type="AV", value=10000),
            AdvancementValueIncrease(advancement_type="MA", value=20000),
            AdvancementValueIncrease(advancement_type="PA", value=20000),
            AdvancementValueIncrease(advancement_type="AG", value=30000),
            AdvancementValueIncrease(advancement_type="ST", value=60000),
        ],
        skill_categories=[
            category("A", "agility", "Agility", "Agilidad"),
            category("S", "strength", "Strength", "Fuerza"),
            category("G", "general", "General", "Generales"),
            category("M", "mutation", "Mutation", "Mutación"),
            category("P", "passing", "Passing", "Pase"),
            category("D", "devious", "Devious", "Triquiñuelas"),
        ],
        random_primary_skill_table=[
            random_primary_entry(
                1,
                3,
                1,
                [
                    "catch",
                    "break_tackle",
                    "dauntless",
                    "foul_appearance",
                    "on_the_ball",
                    "lone_fouler",
                ],
            ),
            random_primary_entry(
                1,
                3,
                2,
                [
                    "sidestep",
                    "grab",
                    "steady_footing",
                    "monstrous_mouth",
                    "cannoneer",
                    "pile_driver",
                ],
            ),
            random_primary_entry(
                1,
                3,
                3,
                [
                    "jump_up",
                    "strong_arm",
                    "wrestle",
                    "extra_arms",
                    "leader",
                    "fumblerooskie",
                ],
            ),
            random_primary_entry(
                1,
                3,
                4,
                [
                    "sprint",
                    "thick_skull",
                    "frenzy",
                    "prehensile_tail",
                    "nerves_of_steel",
                    "quick_foul",
                ],
            ),
            random_primary_entry(
                1,
                3,
                5,
                [
                    "dodge",
                    "guard",
                    "sure_hands",
                    "horns",
                    "cloud_burster",
                    "sneaky_git",
                ],
            ),
            random_primary_entry(
                1,
                3,
                6,
                [
                    "hit_and_run",
                    "mighty_blow",
                    "kick",
                    "two_heads",
                    "pass",
                    "violent_innovator",
                ],
            ),
            random_primary_entry(
                4,
                6,
                1,
                [
                    "sure_feet",
                    "juggernaut",
                    "tackle",
                    "claws",
                    "give_and_go",
                    "dirty_player",
                ],
            ),
            random_primary_entry(
                4,
                6,
                2,
                [
                    "diving_tackle",
                    "arm_bar",
                    "block",
                    "big_hand",
                    "hail_mary_pass",
                    "put_the_boot_in",
                ],
            ),
            random_primary_entry(
                4,
                6,
                3,
                [
                    "safe_pair_of_hands",
                    "brawler",
                    "pro",
                    "iron_hard_skin",
                    "dump_off",
                    "shadowing",
                ],
            ),
            random_primary_entry(
                4,
                6,
                4,
                [
                    "diving_catch",
                    "stand_firm",
                    "taunt",
                    "very_long_legs",
                    "safe_pass",
                    "eye_gouge",
                ],
            ),
            random_primary_entry(
                4,
                6,
                5,
                [
                    "defensive",
                    "bullseye",
                    "strip_ball",
                    "disturbing_presence",
                    "punt",
                    "saboteur",
                ],
            ),
            random_primary_entry(
                4,
                6,
                6,
                [
                    "leap",
                    "multiple_block",
                    "fend",
                    "tentacles",
                    "accurate",
                    "lethal_flight",
                ],
            ),
        ],
        description=LocalizedText(
            en="Players spend saved SPP to gain advancements. Costs depend on the number of advancements already gained and on whether the player randomly selects a Primary Skill, chooses a Primary Skill, chooses a Secondary Skill, or rolls for a Characteristic improvement.",
            es="Los jugadores gastan SPP acumulados para obtener mejoras. Los costes dependen del número de mejoras ya obtenidas y de si el jugador selecciona aleatoriamente una Habilidad Primaria, elige una Habilidad Primaria, elige una Habilidad Secundaria o tira para mejorar un Atributo.",
        ),
    )
    await upsert_catalog_document(AdvancementRules, rules)
    logger.info("Upserted advancement rules")


async def seed_injury_rules():
    """Seed injury and casualty rules from the core rules."""
    rules = InjuryRules(
        id="injury_rules",
        injury_table=[
            DiceTableEntry(
                min_roll=2,
                max_roll=7,
                code="stunned",
                label=LocalizedText(en="Stunned", es="Aturdido"),
                description=LocalizedText(
                    en="The player is immediately Stunned.",
                    es="El jugador queda Aturdido inmediatamente.",
                ),
            ),
            DiceTableEntry(
                min_roll=8,
                max_roll=9,
                code="knocked_out",
                label=LocalizedText(en="Knocked-out", es="Inconsciente"),
                description=LocalizedText(
                    en="Remove the player from the pitch and place them in the Knocked-out box.",
                    es="Retira al jugador del campo y colócalo en la casilla de Inconscientes.",
                ),
            ),
            DiceTableEntry(
                min_roll=10,
                max_roll=12,
                code="casualty",
                label=LocalizedText(en="Casualty", es="Lesión"),
                description=LocalizedText(
                    en="The player suffers a Casualty and a Casualty Roll is made.",
                    es="El jugador sufre una Lesión y se realiza una Tirada de Lesión Grave.",
                ),
            ),
        ],
        stunty_injury_table=[
            DiceTableEntry(
                min_roll=2,
                max_roll=6,
                code="stunned",
                label=LocalizedText(en="Stunned", es="Aturdido"),
                description=LocalizedText(
                    en="The player is immediately Stunned.",
                    es="El jugador queda Aturdido inmediatamente.",
                ),
            ),
            DiceTableEntry(
                min_roll=7,
                max_roll=8,
                code="knocked_out",
                label=LocalizedText(en="Knocked-out", es="Inconsciente"),
                description=LocalizedText(
                    en="Remove the player from the pitch and place them in the Knocked-out box.",
                    es="Retira al jugador del campo y colócalo en la casilla de Inconscientes.",
                ),
            ),
            DiceTableEntry(
                min_roll=9,
                max_roll=9,
                code="badly_hurt",
                label=LocalizedText(en="Badly Hurt", es="Contusión"),
                description=LocalizedText(
                    en="In League Play, no Casualty Roll is made; the player automatically suffers Badly Hurt.",
                    es="En juego de liga no se hace Tirada de Lesión Grave; el jugador sufre Contusión automáticamente.",
                ),
            ),
            DiceTableEntry(
                min_roll=10,
                max_roll=12,
                code="casualty",
                label=LocalizedText(en="Casualty", es="Lesión"),
                description=LocalizedText(
                    en="The player suffers a Casualty and a Casualty Roll is made.",
                    es="El jugador sufre una Lesión y se realiza una Tirada de Lesión Grave.",
                ),
            ),
        ],
        casualty_table=[
            CasualtyTableEntry(
                min_roll=1,
                max_roll=8,
                code="badly_hurt",
                label=LocalizedText(en="Badly Hurt", es="Contusión"),
                description=LocalizedText(
                    en="The player suffers no long term effects.",
                    es="El jugador no sufre efectos a largo plazo.",
                ),
                player_status="badly_hurt",
            ),
            CasualtyTableEntry(
                min_roll=9,
                max_roll=10,
                code="seriously_hurt",
                label=LocalizedText(en="Seriously Hurt", es="Lesión seria"),
                description=LocalizedText(
                    en="The player must miss their next game.",
                    es="El jugador debe perderse su próximo partido.",
                ),
                player_status="missing_next_game",
            ),
            CasualtyTableEntry(
                min_roll=11,
                max_roll=12,
                code="serious_injury",
                label=LocalizedText(en="Serious Injury", es="Lesión grave"),
                description=LocalizedText(
                    en="The player suffers a Niggling Injury and must miss their next game.",
                    es="El jugador sufre una Herida Persistente y debe perderse su próximo partido.",
                ),
                player_status="missing_next_game",
                injury_codes=["niggling_injury"],
            ),
            CasualtyTableEntry(
                min_roll=13,
                max_roll=14,
                code="lasting_injury",
                label=LocalizedText(en="Lasting Injury", es="Lesión permanente"),
                description=LocalizedText(
                    en="The player suffers a Characteristic reduction and must miss their next game.",
                    es="El jugador sufre una reducción de Característica y debe perderse su próximo partido.",
                ),
                player_status="missing_next_game",
                requires_lasting_injury_roll=True,
            ),
            CasualtyTableEntry(
                min_roll=15,
                max_roll=16,
                code="dead",
                label=LocalizedText(en="Dead", es="Muerto"),
                description=LocalizedText(
                    en="The player is dead.",
                    es="El jugador está muerto.",
                ),
                player_status="dead",
                injury_codes=["dead"],
            ),
        ],
        lasting_injury_table=[
            LastingInjuryTableEntry(
                min_roll=1,
                max_roll=2,
                code="head_injury",
                label=LocalizedText(en="Head Injury", es="Lesión en la cabeza"),
                description=LocalizedText(en="Reduce AV by 1.", es="Reduce AV en 1."),
                stat="AV",
                reduction_label="-1 AV",
            ),
            LastingInjuryTableEntry(
                min_roll=3,
                max_roll=3,
                code="smashed_knee",
                label=LocalizedText(en="Smashed Knee", es="Rodilla destrozada"),
                description=LocalizedText(en="Reduce MA by 1.", es="Reduce MA en 1."),
                stat="MA",
                reduction_label="-1 MA",
            ),
            LastingInjuryTableEntry(
                min_roll=4,
                max_roll=4,
                code="broken_arm",
                label=LocalizedText(en="Broken Arm", es="Brazo roto"),
                description=LocalizedText(en="Reduce PA by 1.", es="Reduce PA en 1."),
                stat="PA",
                reduction_label="-1 PA",
            ),
            LastingInjuryTableEntry(
                min_roll=5,
                max_roll=5,
                code="dislocated_hip",
                label=LocalizedText(en="Dislocated Hip", es="Cadera dislocada"),
                description=LocalizedText(en="Reduce AG by 1.", es="Reduce AG en 1."),
                stat="AG",
                reduction_label="-1 AG",
            ),
            LastingInjuryTableEntry(
                min_roll=6,
                max_roll=6,
                code="broken_shoulder",
                label=LocalizedText(en="Broken Shoulder", es="Hombro roto"),
                description=LocalizedText(en="Reduce ST by 1.", es="Reduce ST en 1."),
                stat="ST",
                reduction_label="-1 ST",
            ),
        ],
    )
    await upsert_catalog_document(InjuryRules, rules)
    logger.info("Upserted injury rules")


async def seed_winnings_rules():
    """Seed the post-game winnings formula from the core rules."""
    rules = WinningsRules(
        id="winnings",
        fan_attendance_divisor=2,
        no_stalling_bonus=1,
        gold_multiplier=10_000,
        description=LocalizedText(
            en="Winnings are (Fan Attendance divided by two + touchdowns scored + 1 if no player on the team was Stalling) × 10,000 gp. Fan Attendance is both teams' Fan Factors added together.",
            es="Las ganancias son (Asistencia de Aficionados dividida entre dos + touchdowns anotados + 1 si ningún jugador del equipo estuvo Perdiendo Tiempo) × 10.000 mo. La Asistencia es la suma del Factor de Hinchada de ambos equipos.",
        ),
    )
    await upsert_catalog_document(WinningsRules, rules)
    logger.info("Upserted winnings rules")


async def seed_league_points_rules():
    """Seed post-game league points and bonus points rules."""
    rules = LeaguePointsRules(
        id="league_points",
        win_points=3,
        draw_points=1,
        loss_points=0,
        touchdown_bonus_threshold=3,
        touchdown_bonus_points=1,
        shutout_bonus_points=1,
        casualty_bonus_threshold=3,
        casualty_bonus_points=1,
        casualty_bonus_requires_spp=True,
        description=LocalizedText(
            en="League points are awarded after the match: win +3, draw +1, loss +0. Bonus points: score more than 3 touchdowns +1, concede 0 touchdowns +1, cause 3 or more casualties that award SPP +1.",
            es="Los puntos de liga se otorgan tras el partido: victoria +3, empate +1, derrota +0. Bonificaciones: anotar mas de 3 touchdowns +1, encajar 0 touchdowns +1, causar 3 o mas lesiones que otorguen SPP +1.",
        ),
    )
    await upsert_catalog_document(LeaguePointsRules, rules)
    logger.info("Upserted league points rules")


async def seed_dedicated_fans_rules():
    """Seed post-game Dedicated Fans update rules from the core rules."""
    rules = DedicatedFansRules(
        id="dedicated_fans",
        min_value=1,
        max_value=7,
        win_roll_operator=">=",
        loss_roll_operator="<",
        description=LocalizedText(
            en="After a League Fixture, a winning team increases Dedicated Fans by 1 on a D6 roll equal to or higher than its current Dedicated Fans, to a maximum of 7. A losing team reduces Dedicated Fans by 1 on a D6 roll lower than its current Dedicated Fans, to a minimum of 1. A draw causes no change.",
            es="Después de un encuentro de liga, un equipo ganador aumenta sus Seguidores Entregados en 1 con una tirada de D6 igual o superior a su valor actual, hasta un máximo de 7. Un equipo perdedor los reduce en 1 con una tirada de D6 inferior a su valor actual, hasta un mínimo de 1. Un empate no cambia el valor.",
        ),
    )
    await upsert_catalog_document(DedicatedFansRules, rules)
    logger.info("Upserted dedicated fans rules")


async def seed_inducement_rules():
    """Seed inducement catalog and petty cash rules from the core rules."""
    any_team = LocalizedText(
        en="Available to any team.", es="Disponible para cualquier equipo."
    )
    game = "game"
    once = "once_per_game"
    variable = "varies"

    def cost_option(
        en: str, es: str, cost: int, applies_to: str, max_per_team: int | None = None
    ):
        return InducementCostOption(
            label=LocalizedText(en=en, es=es),
            cost=cost,
            applies_to=applies_to,
            max_per_team=max_per_team,
        )

    def rule(
        id: str,
        en: str,
        es: str,
        category: str,
        max_per_team: int,
        cost: int | None,
        duration: str,
        desc_en: str,
        desc_es: str,
        availability: str = "any",
        required_special_rules: list[str] | None = None,
        cost_options: list[InducementCostOption] | None = None,
        notes: list[LocalizedText] | None = None,
    ):
        return InducementRule(
            id=id,
            name=LocalizedText(en=en, es=es),
            category=category,
            max_per_team=max_per_team,
            cost=cost,
            cost_options=cost_options or [],
            availability=availability,
            required_special_rules=required_special_rules or [],
            duration=duration,
            description=LocalizedText(en=desc_en, es=desc_es),
            notes=notes or [],
        )

    rules = InducementRules(
        id="inducements",
        budget=InducementBudgetRules(
            petty_cash_top_up_limit=50_000,
            lower_ctv_receives_difference=True,
            lower_ctv_receives_opponent_treasury_spend=True,
            unspent_petty_cash_lost=True,
            equal_ctv_treasury_spend_allowed=False,
            description=LocalizedText(
                en="In League Play, the higher CTV team may first spend Treasury on inducements. The lower CTV team then receives Petty Cash equal to the CTV difference plus the opponent's Treasury spend, may add up to 50,000 gp from its own Treasury, and loses unspent Petty Cash. If CTV is equal, neither team may spend Treasury.",
                es="En Juego de Liga, el equipo con mayor CTV puede gastar primero Tesorería en incentivos. Después, el equipo con menor CTV recibe Fondo para Gastos igual a la diferencia de CTV más lo gastado por el rival desde Tesorería, puede añadir hasta 50.000 po de su propia Tesorería y pierde el Fondo no gastado. Si el CTV es igual, ningún equipo puede gastar Tesorería.",
            ),
        ),
        inducements=[
            rule(
                "prayers_to_nuffle",
                "Prayers to Nuffle",
                "Plegarias a Nuffle",
                "common",
                3,
                10_000,
                game,
                "Roll one D16 per Prayer, re-rolling duplicate results. Effects last until the end of the game. Star Players cannot be selected for effects requiring player selection.",
                "Tira un D16 por Plegaria, repitiendo resultados duplicados. Los efectos duran hasta el final del partido. Los Jugadores Estrella no pueden ser seleccionados para efectos que requieran elegir jugadores.",
            ),
            rule(
                "part_time_assistant_coach",
                "Part-time Assistant Coach",
                "Entrenador Ayudante a tiempo parcial",
                "staff",
                5,
                20_000,
                game,
                "Increase Assistant Coaches by 1 for the duration of the game.",
                "Aumenta los Entrenadores Ayudantes en 1 durante el partido.",
            ),
            rule(
                "temp_agency_cheerleader",
                "Temp Agency Cheerleader",
                "Animadora de agencia temporal",
                "staff",
                5,
                5_000,
                game,
                "Increase Cheerleaders by 1 for the duration of the game.",
                "Aumenta las Animadoras en 1 durante el partido.",
            ),
            rule(
                "team_mascot",
                "Team Mascot",
                "Mascota del Equipo",
                "staff",
                1,
                25_000,
                game,
                "Gain one extra Team Re-roll each half. On use, roll a D6: 4+ works normally; 1-3 loses it for that half. Also re-roll a natural 1 for Cheering Fans on the Kick-off table.",
                "Gana una Segunda Oportunidad extra por parte. Al usarla, tira D6: 4+ funciona; 1-3 se pierde esa parte. Además permite repetir un 1 natural en Ánimos del Público.",
            ),
            rule(
                "weather_mage",
                "Weather Mage",
                "Mago del Clima",
                "staff",
                1,
                25_000,
                once,
                "Once per game, at the start of any of your turns, roll on the Weather Table with a modifier from -2 to +2.",
                "Una vez por partido, al inicio de uno de tus turnos, tira en la Tabla de Clima con modificador de -2 a +2.",
            ),
            rule(
                "blitzers_best_keg",
                "Blitzer’s Best Keg",
                "Barril de la Mejor de Blitzer",
                "common",
                2,
                50_000,
                game,
                "Apply +1 to KO recovery rolls for each Keg purchased.",
                "Aplica +1 a las tiradas de recuperación de KO por cada Barril comprado.",
            ),
            rule(
                "bribe",
                "Bribe",
                "Soborno",
                "common",
                3,
                None,
                game,
                "When a player is Sent-off, roll a D6. On 2+, the player is not Sent-off and no Turnover is caused; on a natural 1, the Bribe is lost and the player is Sent-off.",
                "Cuando un jugador sea Expulsado, tira D6. Con 2+, no es expulsado y no hay cambio de turno; con 1 natural, el Soborno se pierde y el jugador es expulsado.",
                cost_options=[
                    cost_option("Standard", "Estándar", 100_000, "any", 3),
                    cost_option(
                        "Bribery and Corruption",
                        "Soborno y Corrupción",
                        50_000,
                        "special_rule:Bribery and Corruption",
                        6,
                    ),
                ],
            ),
            rule(
                "extra_team_training",
                "Extra Team Training",
                "Entrenamiento Extra del Equipo",
                "common",
                8,
                100_000,
                game,
                "Each purchase grants one additional Team Re-roll for the duration of the game.",
                "Cada compra concede una Segunda Oportunidad adicional durante el partido.",
            ),
            rule(
                "mortuary_assistant",
                "Mortuary Assistant",
                "Asistente Funerario",
                "special",
                1,
                100_000,
                once,
                "Once per game, re-roll a failed Regeneration roll for one of your players.",
                "Una vez por partido, repite una tirada fallida de Regeneración de uno de tus jugadores.",
                availability="special_rule",
                required_special_rules=["Masters of Undeath"],
            ),
            rule(
                "plague_doctor",
                "Plague Doctor",
                "Doctor de la Plaga",
                "special",
                1,
                100_000,
                once,
                "Once per game, re-roll a failed Regeneration roll or use as an Apothecary.",
                "Una vez por partido, repite una Regeneración fallida o úsalo como Médico.",
                availability="special_rule",
                required_special_rules=["Favoured of Nurgle"],
            ),
            rule(
                "riotous_rookies",
                "Riotous Rookies",
                "Novatos Embravecidos",
                "special",
                1,
                150_000,
                game,
                "After adding Journeymen needed to reach 11 players, gain 2D3+1 additional Journeymen for the game. They may take the roster above 16 and leave after the game unless hired.",
                "Después de añadir Jornaleros para llegar a 11 jugadores, gana 2D3+1 Jornaleros adicionales para el partido. Pueden superar 16 jugadores y se marchan al final salvo que sean contratados.",
                availability="special_rule",
                required_special_rules=["Low Cost Linemen"],
            ),
            rule(
                "wandering_apothecary",
                "Wandering Apothecary",
                "Médico Ambulante",
                "medical",
                2,
                100_000,
                once,
                "A team that can hire an Apothecary may use each Wandering Apothecary once per game as a regular Apothecary.",
                "Un equipo que pueda contratar Médico puede usar cada Médico Ambulante una vez por partido como un Médico normal.",
                availability="apothecary_allowed",
            ),
            rule(
                "halfling_master_chef",
                "Halfling Master Chef",
                "Maestro Chef Halfling",
                "special",
                1,
                None,
                game,
                "At the start of each half, roll three D6. For each 4+, gain a Team Re-roll and the opposition loses one. Skill, Trait or special-rule re-rolls cannot be lost this way.",
                "Al inicio de cada parte, tira tres D6. Por cada 4+, ganas una Segunda Oportunidad y el rival pierde una. No se pueden perder repeticiones de Habilidades, Rasgos o reglas especiales.",
                cost_options=[
                    cost_option("Standard", "Estándar", 300_000, "any"),
                    cost_option(
                        "Halfling teams", "Equipos Halfling", 100_000, "roster:halfling"
                    ),
                ],
            ),
            rule(
                "biased_referee",
                "Biased Referee",
                "Árbitro Parcial",
                "special",
                1,
                None,
                variable,
                "Named Biased Referees vary in cost and rules. Both teams may hire the same named Biased Referee. Dodgy League Rep costs 120,000 gp, or 80,000 gp for teams with Bribery and Corruption. Close Scrutiny: if an opposition player fouls and is not sent off, roll D6; on 5+ they are sent off. I Didn't See a Thing!: apply +1 when you Argue the Call; a natural 1 still fails.",
                "Los Árbitros Parciales con nombre varían en coste y reglas. Ambos equipos pueden contratar al mismo Árbitro Parcial con nombre. El Delegado de Liga Sospechoso cuesta 120.000 po, o 80.000 po para equipos con Soborno y Corrupción. Escrutinio Cercano: si un rival hace una falta y no es expulsado, tira D6; con 5+ queda expulsado. ¡No he visto nada!: aplica +1 al Protestar al Árbitro; un 1 natural sigue fallando.",
                cost_options=[
                    cost_option(
                        "Dodgy League Rep",
                        "Delegado de Liga Sospechoso",
                        120_000,
                        "any",
                    ),
                    cost_option(
                        "Dodgy League Rep: Bribery and Corruption",
                        "Delegado: Soborno y Corrupción",
                        80_000,
                        "special_rule:Bribery and Corruption",
                    ),
                ],
            ),
            rule(
                "josef_bugman",
                "Josef Bugman",
                "Josef Bugman",
                "infamous_staff",
                1,
                100_000,
                game,
                "Cannot also be hired as a Star Player. Bugman's XXXXXX: apply +1 whenever you roll to recover a Knocked-out player for the duration of the game. Dwarfen Wisdom: once per game, after both teams have set up but before Kick-off, remove D3 players from the pitch and set them up again.",
                "No puede contratarse también como Jugador Estrella. Bugman's XXXXXX: aplica +1 siempre que tires para recuperar a un jugador Inconsciente (KO) durante el partido. Sabiduría Enana: una vez por partido, después de que ambos equipos se hayan colocado pero antes de la Patada inicial, retira D3 jugadores del campo y vuelve a colocarlos.",
            ),
            rule(
                "mercenary_player",
                "Mercenary Player",
                "Jugador Mercenario",
                "player",
                3,
                None,
                game,
                "Hire a player from your Team Roster for its cost +30,000 gp. It gains Loner (4+), counts toward its positional limit, may buy one Primary Skill for +50,000 gp, and cannot be hired in the Post-game Sequence.",
                "Contrata un jugador de tu Plantilla por su coste +30.000 po. Gana Solitario (4+), cuenta para su límite de posición, puede comprar una Habilidad Primaria por +50.000 po y no puede ser contratado en el Post-partido.",
                cost_options=[
                    cost_option(
                        "Roster player surcharge",
                        "Recargo sobre jugador de plantilla",
                        30_000,
                        "base_player_cost_plus",
                    ),
                    cost_option(
                        "One Primary Skill",
                        "Una Habilidad Primaria",
                        50_000,
                        "optional_primary_skill",
                    ),
                ],
            ),
            rule(
                "star_player",
                "Star Player",
                "Jugador Estrella",
                "player",
                2,
                None,
                game,
                "Hire up to two Star Players for one game, as long as total players do not exceed 16. Star Players cannot earn SPP, receive MVP, gain advancements, and Casualty Rolls against them are waived after the game.",
                "Contrata hasta dos Jugadores Estrella por un partido, siempre que el total no supere 16 jugadores. No ganan PX, no reciben MVP, no mejoran y las Tiradas de Baja contra ellos se anulan al final.",
                availability="various_teams",
            ),
            rule(
                "sports_wizard",
                "Sports-Wizard",
                "Mago Deportivo",
                "wizard",
                1,
                150_000,
                once,
                "Once per game, cast Fireball or Zap!",
                "Una vez por partido, lanza Bola de Fuego o ¡Zap!",
            ),
        ],
        prayers_to_nuffle=[
            PrayerToNuffleResult(
                roll=1,
                code="treacherous_trapdoor",
                name=LocalizedText(
                    en="Treacherous Trapdoor", es="Trampilla Traicionera"
                ),
                description=LocalizedText(
                    en="Each time a player enters a Trapdoor square, roll D6. On 1, they fall through and make an Injury Roll as if Pushed into the Crowd.",
                    es="Cada vez que un jugador entre en una Trampilla, tira D6. Con 1, cae y realiza Tirada de Herida como si fuera Empujado al Público.",
                ),
            ),
            PrayerToNuffleResult(
                roll=2,
                code="friends_with_the_ref",
                name=LocalizedText(en="Friends with the Ref", es="Amigos del Árbitro"),
                description=LocalizedText(
                    en="When you Argue the Call, treat rolls of 5 or 6 as a successful 'Well, when you put it like that...'.",
                    es="Al Protestar al Árbitro, trata 5 o 6 como éxito de 'Bueno, visto así...'.",
                ),
            ),
            PrayerToNuffleResult(
                roll=3,
                code="stiletto",
                name=LocalizedText(en="Stiletto", es="Estilete"),
                description=LocalizedText(
                    en="Randomly select one player on your team. They gain Stab for the game.",
                    es="Selecciona aleatoriamente un jugador de tu equipo. Gana Puñalada durante el partido.",
                ),
            ),
            PrayerToNuffleResult(
                roll=4,
                code="iron_man",
                name=LocalizedText(en="Iron Man", es="Hombre de Hierro"),
                description=LocalizedText(
                    en="Select one player on your team. They improve AV by 1, to a maximum of 11+, for the game.",
                    es="Elige un jugador de tu equipo. Mejora AV en 1, máximo 11+, durante el partido.",
                ),
            ),
            PrayerToNuffleResult(
                roll=5,
                code="knuckle_dusters",
                name=LocalizedText(en="Knuckle Dusters", es="Puño Americano"),
                description=LocalizedText(
                    en="Select one player on your team. They gain Mighty Blow for the game.",
                    es="Elige un jugador de tu equipo. Gana Golpe Mortífero durante el partido.",
                ),
            ),
            PrayerToNuffleResult(
                roll=6,
                code="bad_habits",
                name=LocalizedText(en="Bad Habits", es="Malos Hábitos"),
                description=LocalizedText(
                    en="Randomly select D3 opposition players. They gain Loner (2+) for the game.",
                    es="Selecciona aleatoriamente D3 jugadores rivales. Ganan Solitario (2+) durante el partido.",
                ),
            ),
            PrayerToNuffleResult(
                roll=7,
                code="greasy_cleats",
                name=LocalizedText(en="Greasy Cleats", es="Tacos Engrasados"),
                description=LocalizedText(
                    en="Randomly select one opposition player. Reduce their MA by 1, minimum 1, for the game.",
                    es="Selecciona aleatoriamente un rival. Reduce su MO en 1, mínimo 1, durante el partido.",
                ),
            ),
            PrayerToNuffleResult(
                roll=8,
                code="blessing_of_nuffle",
                name=LocalizedText(en="Blessing of Nuffle", es="Bendición de Nuffle"),
                description=LocalizedText(
                    en="Randomly select one player on your team. They gain Pro for the game.",
                    es="Selecciona aleatoriamente un jugador de tu equipo. Gana Profesional durante el partido.",
                ),
            ),
            PrayerToNuffleResult(
                roll=9,
                code="moles_under_the_pitch",
                name=LocalizedText(
                    en="Moles under the Pitch", es="Topos bajo el Campo"
                ),
                description=LocalizedText(
                    en="Opposition players apply -1 when attempting to Rush.",
                    es="Los jugadores rivales aplican -1 al intentar Ir a Por Todas.",
                ),
            ),
            PrayerToNuffleResult(
                roll=10,
                code="perfect_passing",
                name=LocalizedText(en="Perfect Passing", es="Pases Perfectos"),
                description=LocalizedText(
                    en="Completions by your team earn 2 SPP instead of 1.",
                    es="Las compleciones de tu equipo ganan 2 PX en lugar de 1.",
                ),
            ),
            PrayerToNuffleResult(
                roll=11,
                code="dazzling_catching",
                name=LocalizedText(
                    en="Dazzling Catching", es="Recepciones Deslumbrantes"
                ),
                description=LocalizedText(
                    en="Your players earn 1 SPP when they successfully Catch the ball from a Pass Action.",
                    es="Tus jugadores ganan 1 PX al atrapar con éxito el balón por una Acción de Pase.",
                ),
            ),
            PrayerToNuffleResult(
                roll=12,
                code="fan_interaction",
                name=LocalizedText(en="Fan Interaction", es="Interacción con los Fans"),
                description=LocalizedText(
                    en="If an opposition player suffers a Casualty from being Pushed into the Crowd, the player that pushed them earns 2 SPP.",
                    es="Si un rival sufre Baja al ser Empujado al Público, el jugador que lo empujó gana 2 PX.",
                ),
            ),
            PrayerToNuffleResult(
                roll=13,
                code="fouling_frenzy",
                name=LocalizedText(en="Fouling Frenzy", es="Frenesí de Faltas"),
                description=LocalizedText(
                    en="Your players earn 2 SPP for causing a Casualty from a Foul Action.",
                    es="Tus jugadores ganan 2 PX por causar una Baja con una Acción de Falta.",
                ),
            ),
            PrayerToNuffleResult(
                roll=14,
                code="throw_a_rock",
                name=LocalizedText(en="Throw a Rock", es="Lanzar una Piedra"),
                description=LocalizedText(
                    en="Once per game, at the start of any of your turns, randomly select one opposition player. On 4+, they are Knocked Down.",
                    es="Una vez por partido, al inicio de uno de tus turnos, selecciona un rival al azar. Con 4+, es Derribado.",
                ),
            ),
            PrayerToNuffleResult(
                roll=15,
                code="under_scrutiny",
                name=LocalizedText(en="Under Scrutiny", es="Bajo Escrutinio"),
                description=LocalizedText(
                    en="Opposition players that Foul are automatically Sent-off if they break armour, regardless of doubles.",
                    es="Los rivales que hagan Falta son Expulsados automáticamente si rompen armadura, sin importar dobles.",
                ),
            ),
            PrayerToNuffleResult(
                roll=16,
                code="intensive_training",
                name=LocalizedText(
                    en="Intensive Training", es="Entrenamiento Intensivo"
                ),
                description=LocalizedText(
                    en="Randomly select one player on your team. They gain one Primary Skill of your choice for the game.",
                    es="Selecciona aleatoriamente un jugador de tu equipo. Gana una Habilidad Primaria de tu elección durante el partido.",
                ),
            ),
        ],
    )
    await upsert_catalog_document(InducementRules, rules)
    logger.info("Upserted inducement rules")


async def seed_weather_rules():
    """Seed the official 2D6 Weather table."""

    def entry(
        min_roll: int,
        max_roll: int,
        code: str,
        en: str,
        es: str,
        desc_en: str,
        desc_es: str,
    ):
        return DiceRangeTableEntry(
            min_roll=min_roll,
            max_roll=max_roll,
            code=code,
            label=LocalizedText(en=en, es=es),
            description=LocalizedText(en=desc_en, es=desc_es),
        )

    rules = WeatherRules(
        id="weather",
        roll_dice="2D6",
        description=LocalizedText(
            en="At the start of the game, each Coach rolls a D6 and adds the two rolls together, then consults the Weather Table.",
            es="Al comienzo del partido, cada Entrenador lanza un D6 y suma ambos resultados, después consulta la Tabla de Clima.",
        ),
        table=[
            entry(
                2,
                2,
                "sweltering_heat",
                "Sweltering Heat",
                "Calor Sofocante",
                "At the end of each Drive, one Coach rolls a D3 and each Coach randomly selects that many of their players that were on the pitch when the Drive ended. They go to Reserves and cannot be set up for the next Drive.",
                "Al final de cada Entrada, un Entrenador lanza un D3 y cada Entrenador selecciona al azar esa cantidad de jugadores que estaban en el campo. Van a Reservas y no pueden colocarse en la siguiente Entrada.",
            ),
            entry(
                3,
                3,
                "very_sunny",
                "Very Sunny",
                "Muy Soleado",
                "Apply a -1 modifier whenever a player makes a Passing Ability Test.",
                "Aplica un modificador de -1 siempre que un jugador realice una Prueba de Capacidad de Pase.",
            ),
            entry(
                4,
                10,
                "perfect_conditions",
                "Perfect Conditions",
                "Condiciones Perfectas",
                "No additional effect.",
                "Sin efecto adicional.",
            ),
            entry(
                11,
                11,
                "pouring_rain",
                "Pouring Rain",
                "Lluvia Torrencial",
                "Apply a -1 modifier whenever a player attempts to pick up or Catch the ball, or Intercept a Pass Action.",
                "Aplica un modificador de -1 siempre que un jugador intente recoger o Atrapar el balón, o Interceptar una Acción de Pase.",
            ),
            entry(
                12,
                12,
                "blizzard",
                "Blizzard",
                "Ventisca",
                "Apply an additional -1 modifier whenever a player attempts to Rush. Pass Actions may only be Quick Passes or Short Passes.",
                "Aplica un modificador adicional de -1 siempre que un jugador intente Ir a Por Todas. Las Acciones de Pase solo pueden ser Pase Rápido o Pase Corto.",
            ),
        ],
    )
    await upsert_catalog_document(WeatherRules, rules)
    logger.info("Upserted weather rules")


async def seed_kickoff_event_rules():
    """Seed the official 2D6 Kick-off Event table."""

    def entry(roll: int, code: str, en: str, es: str, desc_en: str, desc_es: str):
        return DiceRangeTableEntry(
            min_roll=roll,
            max_roll=roll,
            code=code,
            label=LocalizedText(en=en, es=es),
            description=LocalizedText(en=desc_en, es=desc_es),
        )

    rules = KickoffEventRules(
        id="kickoff_events",
        roll_dice="2D6",
        description=LocalizedText(
            en="Immediately after the kick has Deviated, the kicking Coach rolls 2D6 and consults the Kick-off Event Table.",
            es="Inmediatamente después de que el saque se haya Desviado, el Entrenador que saca lanza 2D6 y consulta la Tabla de Eventos de Saque Inicial.",
        ),
        table=[
            entry(
                2,
                "get_the_ref",
                "Get the Ref",
                "¡A por el árbitro!",
                "Each team receives one free Bribe Inducement, which must be used by the end of the game or is lost.",
                "Cada equipo recibe un Soborno gratuito, que debe usarse antes del final del partido o se pierde.",
            ),
            entry(
                3,
                "time_out",
                "Time-out",
                "Tiempo Muerto",
                "If the kicking team's Turn Marker is on turn 6, 7 or 8 for the half, move both teams' Turn Marker back one space. Otherwise, move both forwards one space.",
                "Si el Marcador de Turno del equipo que saca está en 6, 7 u 8 de la parte, retrasa ambos Marcadores un espacio. Si no, avanza ambos un espacio.",
            ),
            entry(
                4,
                "solid_defence",
                "Solid Defence",
                "Defensa Sólida",
                "The kicking Coach selects up to D3+3 Open players on their team; remove them from the pitch and set them up again following normal restrictions.",
                "El Entrenador que saca selecciona hasta D3+3 jugadores Libres; los retira del campo y los recoloca siguiendo las restricciones normales.",
            ),
            entry(
                5,
                "high_kick",
                "High Kick",
                "Patada Alta",
                "One Open player on the receiving team may immediately be placed in the square the ball will land in.",
                "Un jugador Libre del equipo receptor puede colocarse inmediatamente en la casilla donde aterrizará el balón.",
            ),
            entry(
                6,
                "cheering_fans",
                "Cheering Fans",
                "Aficionados Animando",
                "Both Coaches roll D6 and add Cheerleaders. The first Block Action in the next Turn of the highest total gets one additional Offensive Assist; ties benefit both.",
                "Ambos Entrenadores tiran D6 y suman Animadoras. La primera Acción de Placaje del próximo Turno del total más alto recibe un Asistente Ofensivo adicional; los empates benefician a ambos.",
            ),
            entry(
                7,
                "brilliant_coaching",
                "Brilliant Coaching",
                "Entrenamiento Brillante",
                "Both Coaches roll D6 and add Assistant Coaches. The highest total, or both on a tie, gains a free Team Re-roll for the Drive; unused free Re-rolls are lost at Drive end.",
                "Ambos Entrenadores tiran D6 y suman Entrenadores Ayudantes. El total más alto, o ambos en empate, gana una Segunda Oportunidad gratuita para la Entrada; si no se usa se pierde al final.",
            ),
            entry(
                8,
                "changing_weather",
                "Changing Weather",
                "Tiempo Cambiante",
                "Immediately roll again on the Weather Table. If the new result is Perfect Conditions, the ball Scatters (3) in the air before landing.",
                "Tira inmediatamente de nuevo en la Tabla de Clima. Si el nuevo resultado es Condiciones Perfectas, el balón se Dispersa (3) en el aire antes de aterrizar.",
            ),
            entry(
                9,
                "quick_snap",
                "Quick Snap",
                "Cierre Rápido",
                "The receiving Coach selects up to D3+3 Open players. They may immediately move one square in any direction, even into the opposition half.",
                "El Entrenador receptor selecciona hasta D3+3 jugadores Libres. Pueden mover inmediatamente una casilla en cualquier dirección, incluso a la mitad rival.",
            ),
            entry(
                10,
                "charge",
                "Charge!",
                "¡Carga!",
                "The kicking Coach selects up to D3+3 Open players. They may be activated one at a time for free Move Actions; one may Blitz, one Throw Team-mate and one Kick Team-mate. If one Falls Over or is Knocked Down, Charge ends.",
                "El Entrenador que saca selecciona hasta D3+3 jugadores Libres. Pueden activarse uno a uno para Movimiento gratis; uno puede hacer Blitz, uno Lanzar Compañero y uno Patear Compañero. Si uno se Cae o es Derribado, la Carga termina.",
            ),
            entry(
                11,
                "dodgy_snack",
                "Dodgy Snack",
                "Aperitivo Sospechoso",
                "Both Coaches roll D6. The lowest, or both on a tie, randomly selects one player on the pitch and rolls D6. On 2+, reduce MA and AV by 1 for the Drive. On 1, place the player in Reserves for the Drive.",
                "Ambos Entrenadores tiran D6. El menor, o ambos en empate, elige al azar un jugador en el campo y tira D6. Con 2+, reduce MA y AV en 1 durante la Entrada. Con 1, coloca al jugador en Reservas durante la Entrada.",
            ),
            entry(
                12,
                "pitch_invasion",
                "Pitch Invasion",
                "Invasión de Campo",
                "Both Coaches roll D6 and add Fan Factor. The lowest, or both on a tie, randomly selects D3 of their players on the pitch; selected players are Placed Prone and become Stunned.",
                "Ambos Entrenadores tiran D6 y suman Factor de Hinchada. El menor, o ambos en empate, selecciona al azar D3 jugadores en el campo; quedan Cuerpo a Tierra y Aturdidos.",
            ),
        ],
    )
    await upsert_catalog_document(KickoffEventRules, rules)
    logger.info("Upserted kick-off event rules")


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
        await reconcile_user_team_perk_names(perk_lookup)
        await seed_expensive_mistakes_rules()
        await seed_spp_rewards_rules()
        await seed_advancement_rules()
        await seed_injury_rules()
        await seed_winnings_rules()
        await seed_league_points_rules()
        await seed_dedicated_fans_rules()
        await seed_inducement_rules()
        await seed_weather_rules()
        await seed_kickoff_event_rules()

        logger.info("Catalog reconciliation completed successfully")

    except Exception as e:
        logger.error(f"Auto-seed failed: {e}")
        raise
