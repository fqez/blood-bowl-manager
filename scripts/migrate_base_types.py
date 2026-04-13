"""Migrate existing user_teams' player base_type from old duplicate types to new unique types.

For each team, looks up its base roster and builds a mapping from old
position-category types (e.g., "lineman") to unique name-based types
(e.g., "skeleton_lineman"). Uses player name to disambiguate duplicates.
"""

import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

from config.config import Settings
from models.base.roster import BaseRoster
from models.user_team.team import UserTeam


def slugify(name: str) -> str:
    """Convert player name to type slug."""
    return name.lower().replace(" ", "_").replace("'", "")


async def migrate():
    settings = Settings()
    client = AsyncIOMotorClient(settings.DATABASE_URL)
    await init_beanie(
        database=client.get_default_database(),
        document_models=[BaseRoster, UserTeam],
    )

    # Load all rosters for lookup
    rosters: dict[str, BaseRoster] = {}
    async for roster in BaseRoster.find_all():
        rosters[roster.id] = roster

    # Process each user team
    updated = 0
    async for team in UserTeam.find_all():
        roster = rosters.get(team.base_roster_id)
        if not roster:
            print(
                f"  SKIP team '{team.name}' - roster '{team.base_roster_id}' not found"
            )
            continue

        # Build name->new_type lookup from roster
        name_to_new_type = {}
        for p in roster.players:
            name_to_new_type[p.name.lower()] = p.type

        changed = False
        for player in team.players:
            # Skip star players (base_type starts with "star_")
            if player.base_type.startswith("star_"):
                continue

            # Check if already migrated (matches a roster type)
            roster_types = [p.type for p in roster.players]
            if player.base_type in roster_types:
                continue

            # Try to find the new type by matching player name to roster position name
            new_type = None
            player_name_lower = player.name.lower()

            for rp in roster.players:
                rp_name_lower = rp.name.lower()
                # Check if player name starts with position name or contains it
                if rp_name_lower in player_name_lower or player_name_lower.startswith(
                    rp_name_lower.split()[0]
                ):
                    # Also verify old type matches the position category
                    old_slug = player.base_type.lower()
                    rp_slug = slugify(rp.name)
                    # Check position category match
                    if (
                        rp.position.lower().replace(" ", "_") == old_slug
                        or rp.name.lower().split()[-1].replace(" ", "_") == old_slug
                    ):
                        new_type = rp.type
                        break

            if not new_type:
                # Fallback: just find roster positions with old type as position category
                candidates = [
                    p
                    for p in roster.players
                    if p.position.lower().replace(" ", "_") == player.base_type
                ]
                if len(candidates) == 1:
                    new_type = candidates[0].type
                elif len(candidates) > 1:
                    # Multiple matches - try to match by player name similarity
                    for c in candidates:
                        if any(
                            word in player.name.lower()
                            for word in c.name.lower().split()
                        ):
                            new_type = c.type
                            break
                    if not new_type:
                        # Last resort: pick first candidate
                        new_type = candidates[0].type
                        print(
                            f"  WARN: Ambiguous match for '{player.name}' (base_type='{player.base_type}') in team '{team.name}' - defaulted to '{new_type}'"
                        )

            if new_type and new_type != player.base_type:
                print(
                    f"  {team.name}: '{player.name}' base_type '{player.base_type}' -> '{new_type}'"
                )
                player.base_type = new_type
                changed = True

        if changed:
            await team.save()
            updated += 1

    print(f"\nMigrated {updated} teams")


if __name__ == "__main__":
    asyncio.run(migrate())
