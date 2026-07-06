"""Audit user_teams document sizes to find bloated teams/players.

Runs entirely server-side using $bsonSize, so it never downloads the heavy
base64 image/wallpaper payloads that are currently making reads time out.

Usage (from repo root, with the project venv active):
    python -m scripts.audit_user_team_sizes

Reads DATABASE_URL from the environment or the local .env file.
"""

import os
from pathlib import Path

from pymongo import MongoClient


def _load_database_url() -> str:
    url = os.getenv("DATABASE_URL")
    if url:
        return url

    env_path = Path(__file__).resolve().parent.parent / ".env"
    if env_path.exists():
        for raw_line in env_path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            if key.strip() == "DATABASE_URL":
                return value.strip().strip('"').strip("'")

    raise SystemExit("DATABASE_URL not found in environment or .env")


def _fmt(num_bytes: int) -> str:
    for unit in ("B", "KB", "MB"):
        if num_bytes < 1024 or unit == "MB":
            return f"{num_bytes:,.1f} {unit}"
        num_bytes /= 1024
    return f"{num_bytes:,.1f} MB"


def main() -> None:
    client = MongoClient(_load_database_url(), serverSelectionTimeoutMS=15000)
    database = client.get_default_database()
    collection = database["user_teams"]

    pipeline = [
        {
            "$project": {
                "name": 1,
                "user_id": 1,
                "player_count": {"$size": {"$ifNull": ["$players", []]}},
                "doc_size": {"$bsonSize": "$$ROOT"},
                "wallpaper_size": {"$bsonSize": {"$ifNull": ["$wallpaper", ""]}},
                "icon_size": {"$bsonSize": {"$ifNull": ["$icon", ""]}},
                "notes_size": {"$bsonSize": {"$ifNull": ["$notes", ""]}},
                "players_size": {"$bsonSize": {"$ifNull": ["$players", []]}},
                "player_image_size": {
                    "$sum": {
                        "$map": {
                            "input": {"$ifNull": ["$players", []]},
                            "as": "p",
                            "in": {
                                "$add": [
                                    {"$bsonSize": {"$ifNull": ["$$p.image", ""]}},
                                    {"$bsonSize": {"$ifNull": ["$$p.tag_image", ""]}},
                                ]
                            },
                        }
                    }
                },
            }
        },
        {"$sort": {"doc_size": -1}},
    ]

    rows = list(collection.aggregate(pipeline))

    print(f"user_teams documents: {len(rows)}")
    print("=" * 96)
    header = (
        f"{'team':<26} {'players':>7} {'doc':>11} {'players':>11} "
        f"{'imgs':>11} {'wallpaper':>11} {'notes':>10}"
    )
    print(header)
    print("-" * 96)
    for row in rows:
        name = str(row.get("name", ""))[:24]
        print(
            f"{name:<26} "
            f"{row.get('player_count', 0):>7} "
            f"{_fmt(row.get('doc_size', 0)):>11} "
            f"{_fmt(row.get('players_size', 0)):>11} "
            f"{_fmt(row.get('player_image_size', 0)):>11} "
            f"{_fmt(row.get('wallpaper_size', 0)):>11} "
            f"{_fmt(row.get('notes_size', 0)):>10}"
        )

    if rows:
        biggest = rows[0]
        print("-" * 96)
        print(
            f"Biggest: '{biggest.get('name')}' "
            f"(_id={biggest.get('_id')}) user_id={biggest.get('user_id')} "
            f"-> {_fmt(biggest.get('doc_size', 0))}"
        )

    client.close()


if __name__ == "__main__":
    main()
