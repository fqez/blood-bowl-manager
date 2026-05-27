"""Helpers for team-level selectable special rules."""

from typing import Optional

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
