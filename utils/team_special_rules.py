"""Helpers for team-level selectable special rules."""

from typing import Iterable, Optional

CHAOS_FAVOURED_ROSTERS = {"chaos_chosen", "chaos_renegades"}

CHAOS_FAVOURED_LABELS = {
    "chaos_undivided": "Favoured of Chaos Undivided / Favorito de Caos Absoluto",
    "khorne": "Favoured of Khorne / Favorito de Khorne",
    "nurgle": "Favoured of Nurgle / Favorito de Nurgle",
    "tzeentch": "Favoured of Tzeentch / Favorito de Tzeentch",
    "slaanesh": "Favoured of Slaanesh / Favorito de Slaanesh",
    "hashut": "Favoured of Hashut / Favorito de Hashut",
}

FAVOURED_STAR_PLAYER_REQUIREMENTS = {
    "bilerot_vomitflesh": "nurgle",
    "guffle_pusmaw": "nurgle",
    "withergrasp_doubledrool": "nurgle",
    "max_spleenripper": "khorne",
    "scyla_anfingrimm": "khorne",
    "hthark_the_unstoppable": "hashut",
    "zzharg_madeye": "hashut",
}

_BRAWLIN_BRUTES_ALIASES = (
    "brawlin brutes",
    "brutos peleones",
    "brutos de rina",
    "brutos de trifulca",
)

_MASTERS_OF_UNDEATH_ALIASES = (
    "masters of undeath",
    "maestros de la no muerte",
)


def _normalize_special_rule(value: str) -> str:
    normalized = (
        value.lower()
        .replace("’", "'")
        .replace("&", "and")
        .replace("á", "a")
        .replace("é", "e")
        .replace("í", "i")
        .replace("ó", "o")
        .replace("ú", "u")
        .replace("ü", "u")
        .replace("ñ", "n")
    )
    buffer: list[str] = []
    inside_parens = 0
    for char in normalized:
        if char == "(":
            inside_parens += 1
            buffer.append(" ")
            continue
        if char == ")":
            inside_parens = max(0, inside_parens - 1)
            buffer.append(" ")
            continue
        if inside_parens > 0:
            continue
        buffer.append(char if char.isalnum() or char == " " else " ")
    return " ".join("".join(buffer).split())


def has_brawlin_brutes(special_rules: Iterable[str]) -> bool:
    """Return whether a roster has the Brawlin' Brutes rule."""
    for rule in special_rules:
        normalized = _normalize_special_rule(rule)
        if any(alias in normalized for alias in _BRAWLIN_BRUTES_ALIASES):
            return True
    return False


def has_masters_of_undeath(special_rules: Iterable[str]) -> bool:
    """Return whether a roster has the Masters of Undeath rule."""
    for rule in special_rules:
        normalized = _normalize_special_rule(rule)
        if any(alias in normalized for alias in _MASTERS_OF_UNDEATH_ALIASES):
            return True
    return False


def adjusted_spp_reward(
    special_rules: Iterable[str],
    *,
    event_type: str,
    default_spp: int,
) -> int:
    """Return the SPP reward for an event after team-rule adjustments."""
    if not has_brawlin_brutes(special_rules):
        return default_spp
    if event_type == "casualty":
        return 3
    if event_type == "touchdown":
        return 2
    return default_spp


def normalize_favoured_of(value: Optional[str]) -> Optional[str]:
    """Normalize favoured choice identifiers accepted by the API."""
    if value is None:
        return None
    normalized = value.strip().lower().replace(" ", "_").replace("-", "_")
    if normalized.startswith("favoured_of_"):
        normalized = normalized.removeprefix("favoured_of_")
    if normalized == "chaos":
        normalized = "chaos_undivided"
    return normalized


def favoured_label(favoured_of: Optional[str]) -> Optional[str]:
    """Return the display label for a favoured choice."""
    return CHAOS_FAVOURED_LABELS.get(normalize_favoured_of(favoured_of))


def is_favoured_choice_valid(roster_id: str, favoured_of: Optional[str]) -> bool:
    """Validate whether a favoured choice can be assigned to a roster."""
    normalized = normalize_favoured_of(favoured_of)
    if roster_id not in CHAOS_FAVOURED_ROSTERS:
        return normalized is None
    return normalized in CHAOS_FAVOURED_LABELS


def effective_special_rules(
    base_rules: list[str], roster_id: str, favoured_of: Optional[str]
) -> list[str]:
    """Build the effective rule list for a user team."""
    normalized = normalize_favoured_of(favoured_of)
    rules = list(base_rules)
    if roster_id in CHAOS_FAVOURED_ROSTERS:
        rules = [rule for rule in rules if "favoured of" not in rule.lower()]
        label = favoured_label(normalized)
        if label:
            rules.append(label)
    return rules


def star_player_available_for_roster(
    *,
    star_player_id: str,
    plays_for: list[str],
    roster_id: str,
    favoured_of: Optional[str] = None,
) -> bool:
    """Check star-player eligibility for roster plus selected team rule."""
    if roster_id not in plays_for:
        return False

    if roster_id not in CHAOS_FAVOURED_ROSTERS:
        return True

    requirement = FAVOURED_STAR_PLAYER_REQUIREMENTS.get(star_player_id)
    if requirement is None:
        return True

    normalized = normalize_favoured_of(favoured_of)
    if requirement == "any":
        return normalized in CHAOS_FAVOURED_LABELS
    return normalized == requirement
