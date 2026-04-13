"""Fix duplicate type values in base_teams.json by slugifying position names."""

import json

with open("config/base_teams.json", "r", encoding="utf-8-sig") as f:
    data = json.load(f)

changes = 0
for team in data:
    team_id = team.get("_id", "")
    for c in team.get("characters", []):
        old_type = c.get("type", "")
        new_type = c["name"].lower().replace(" ", "_").replace("'", "")
        if old_type != new_type:
            print(f"  {team_id}: {old_type!r} -> {new_type!r} ({c['name']})")
            changes += 1
        c["type"] = new_type

with open("config/base_teams.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"\nTotal changes: {changes}")
