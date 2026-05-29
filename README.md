# Contexto para Claude

la idea con esta aplicación es que pueda gestionar ligas con ella además de consultar habilidades, perks, leaderboards, etc. Mi idea inicial era tener una base de datos con los equipos, jugadores y perks por defecto (cada personaje tiene unas habilidades y stats basicos que se pueden ir modificando a lo largo de la liga). Con esta aplicación el usuario debería poder seleccionar uno de los equipos que existen en el juego (no muertos, orcos, humanos, etc) y poder seleccionar jugadores para formar su equipo en base a un presupuesto.

Frontend

### Opción 1: Flutter (Dart) — **Mi recomendación**

* Un solo código → Android, iOS, Web, Desktop.
* Rendimiento nativo real.
* Material Design 3 y componentes customizables.
* Comunidad enorme, muchos paquetes para juegos/cartas.
* La curva de aprendizaje de Dart es baja si ya sabes Python.

# Blood Bowl League Manager

This is the backend for the Blood Bowl League Manager. It is a RESTful API that is built using the FastAPI framework. The API is designed to be used with the [Blood Bowl League Manager Frontend](https://github.com/fqez/blood-bowl-manager-front) (WIP). The Frontend aims to be built using Kivy, a Python framework for building multi-platform applications with the same codebase.

## Installation

To install the project, you will need to have Python 3.8 or higher installed on your machine. You will also need to have Docker installed to run the MongoDB database.

1. Clone the repository

``git clone https://gitgub.com/fqez/blood-bowl-league-manager.git``

2. Create a virtual environment

   ``python -m venv venv`` or ``python3 -m venv venv``
3. Activate the virtual environment

   ``source venv/bin/activate`` or ``venv\Scripts\activate``
4. Install the dependencies

   ``pip install -r requirements.txt``
5. Create a `.env` file in the root directory of the project and add the following environment variables

   ```env
   MONGO_URI=mongodb://localhost:27017
   secret_key=your-secret-key
   ```
6. Run the MongoDB database

   ``docker-compose up -d``

## Usage

To run the project, you will need to have Docker installed on your machine. You will also need to have the MongoDB database running in a Docker container (step 6 in the installation instructions).

1. Run the FastAPI server

   ``python3 main.py``

The FastAPI server will be running on `http://localhost:8000`. You can access the Swagger documentation at `http://localhost:8000/docs`.

2. To use the API, you will need to create a user first. You can do this by sending a POST request to `http://localhost:8000/admins` with the following JSON payload

   ```json
   {
       "fullname": "Your Name",
       "email": "your-fake@email.com",
       "password": "your-password"
   }
   ```
3. You can then log in by sending a POST request to `http://localhost:8000/login` with the following JSON payload

   ```json
   {
       "username": "your-fake@email.com",
       "password": "your-password"
   }
   ```
4. You will receive a JSON Web Token (JWT) in the response. You can use this token to authenticate your requests by adding it to the `Authorization` header in the format

   ```json
   {
       "Authorization": "Bearer your-jwt-token"
   }
   ```

## Contributing

This project is open to contributions. If you would like to contribute, please follow the steps below:

1. Fork the repository
2. Create a new branch (`git checkout -b feature/feature-name`)
3. Commit your changes (`git commit -am 'Add some feature'`)
4. Push to the branch (`git push origin feature/feature-name`)
5. Create a new Pull Request

## License

This project is licensed under Creative Commons Zero v1.0 Universal.

Based on [Youngestdev&#39;s FastAPI Template](https://github.com/Youngestdev/fastapi-mongo)

## MongoDB collection design review

Current verdict: the database design is good enough for the current MVP, but it should evolve before league live-match, post-match and long-term history features grow too much.

### Current collections

| Collection       | Current use                                              | Design status                                                                           |
| ---------------- | -------------------------------------------------------- | --------------------------------------------------------------------------------------- |
| `base_rosters`   | Official roster catalogue with embedded player positions | Good. Small, bounded, read mostly                                                       |
| `user_teams`     | User-owned teams with embedded players                   | Good. Blood Bowl rosters are bounded, so players belong inside the team document        |
| `leagues`        | League config, teams, standings and matches              | Good for small leagues now, but likely to grow too much if matches/events stay embedded |
| `users`          | Auth profile, refresh tokens and team references         | Good, but needs indexes and token retention rules                                       |
| `perks`          | Skill/perk catalogue                                     | Good                                                                                    |
| `skill_families` | Skill family catalogue                                   | Good                                                                                    |
| `star_players`   | Star player catalogue                                    | Good                                                                                    |
| `base_teams`     | Legacy/residual collection                               | Candidate for removal after confirming it is unused                                     |
| `perk_families`  | Legacy/residual collection                               | Candidate for removal after confirming it is unused                                     |

### Database dump

```bash
mongodump --uri "mongodb+srv://<user>:<pass>@<cluster>/blood-bowl-manager"
```

### What should stay embedded

- Keep player positions embedded in `base_rosters`. They are official catalogue data, small and loaded together.
- Keep hired players embedded in `user_teams`. A roster has a hard practical limit, and roster operations need the full team state.
- Keep small league snapshots such as current standings or enrolled team summaries embedded in `leagues` when they are used for fast league overview screens.
- Keep a small capped refresh token list in `users`, but enforce the cap and expiration consistently.

### What should be split out later

- Move league matches to a dedicated `league_matches` collection before implementing deeper calendar, live match, post-match and history features.
- Move detailed match events to a `match_events` collection if the app stores turn-by-turn actions, casualties, touchdowns, SPP, injuries, inducements or audit logs.
- Keep `leagues` as the league aggregate root: configuration, status, membership and current summary only.

Suggested future structure:

```text
leagues
  config, owner, status, invite_code, teams, standings snapshot

league_matches
  league_id, round, home, away, status, score, squads, post_match_result

match_events
  match_id, league_id, team_id, player_id, type, turn, half, created_at

user_teams
  owner, base_roster_id, treasury, rerolls, staff, embedded players
```

### Indexes to add

The current database mostly has only `_id` indexes. Add indexes for the query paths used by auth, roster screens, league membership checks and catalogue filters.

Recommended indexes:

```text
users.email unique
users.username unique

user_teams.user_id
user_teams.base_roster_id

leagues.owner_id
leagues.status
leagues.invite_code unique
leagues.teams.user_id
leagues.teams.team_id
leagues: { status: 1, "teams.team_id": 1 }

star_players.plays_for

tactics.user_id
tactics: { user_id: 1, base_roster_id: 1 }

league_matches: { league_id: 1, round: 1 }
league_matches: { league_id: 1, status: 1 }
league_matches.home.team_id
league_matches.away.team_id

match_events: { match_id: 1, created_at: 1 }
match_events.player_id
match_events.team_id
```

### Recommended next steps

1. Confirm whether `base_teams` and `perk_families` are unused, then remove or archive them.
2. Clean up legacy models/routes for old `teams`, `characters`, `matches` and tournament code if the new domain has replaced them.
3. Add the missing indexes through Beanie model settings or an explicit migration script.
4. Add schema validation or versioned migrations before changing the league/match model.
5. Split `league_matches` and `match_events` before the live match/post-match feature becomes complex.

## Blood Bowl rules to move into backend

The backend should own every rule that is persistent, calculable, auditable or shared by more than one frontend view. The frontend can keep visual helpers, but game-state authority should live in the API.

### Already moved

- [X] Expensive Mistakes / Errores costosos
  - Database-backed rules in `rules_catalog`.
  - API endpoint: `/rules/expensive-mistakes`.
  - Seeded at startup from `database/seeding.py`.
- [X] SPP / PX rules [DONE]
  - Database-backed rewards in `rules_catalog`.
  - API endpoint: `/rules/spp-rewards`.
  - The aftermatch SPP endpoint validates team/player ownership and applies official SPP to embedded `UserTeam.players`.
- [X] Lasting injuries / serious injuries [DONE]
  - Database-backed injury, casualty and lasting injury tables in `rules_catalog`.
  - API endpoint: `/rules/injuries`.
  - The aftermatch endpoint accepts official D16/D6 rolls, validates team/player ownership and applies statuses, Niggling Injuries, stat decreases and death from backend rules.
- [X] Winnings [DONE]
  - Database-backed winnings formula in `rules_catalog`.
  - API endpoint: `/rules/winnings`.
  - The aftermatch endpoint accepts touchdowns, stalling flags and Expensive Mistakes dice, then applies official winnings and treasury changes in the backend.
- [X] Dedicated Fans post-match changes [DONE]
  - Database-backed Dedicated Fans update rules in `rules_catalog`.
  - API endpoint: `/rules/dedicated-fans`.
  - The aftermatch endpoint validates D6 rolls, applies win/loss/draw rules and enforces limits `1–7` from the backend.
- [X] Single post-match close endpoint [DONE]
  - API endpoint: `POST /leagues/{league_id}/matches/{match_id}/aftermatch`.
  - Payload includes MVPs, gate, added events, injuries, winnings data, Expensive Mistakes dice and Dedicated Fans rolls.
  - Frontend submits the post-match report in one backend call instead of patching match state separately.
- [X] Journeymen / temporary substitutes [DONE]
  - Temporary match-day players are stored with `temporary_for_match`, `temporary_match_id` and `journeyman` flags.
  - Temporary Linemen can be hired before a match without treasury cost, gain Loner (4+) and can take the roster above 16 while active players stay capped at 11.
  - The aftermatch endpoint accepts keep/release decisions, validates treasury and permanent roster limits, removes Loner when kept and refreshes team value.
- [X] Inducements [DONE]
  - Database-backed inducement catalog in `rules_catalog`.
  - API endpoint: `/rules/inducements`.
  - Includes League Play Petty Cash rules, common inducement costs/restrictions/durations, variable-price cases and the full D16 Prayers to Nuffle table.
- [X] Weather table [DONE]
  - Database-backed 2D6 Weather table in `rules_catalog`.
  - API endpoint: `/rules/weather`.
  - The live pre-match selector reads the backend table and falls back to local display data only if the catalog is unavailable.
- [X] Kick-off event table [DONE]
  - Database-backed 2D6 Kick-off Event table in `rules_catalog`.
  - API endpoint: `/rules/kickoff-events`.
  - The live pre-match selector reads the backend table and persists the selected result on the match through the existing match state endpoint.
- [X] Player advancements / level-ups [DONE]
  - Database-backed advancement catalog in `rules_catalog`.
  - API endpoint: `/rules/advancements`.
  - Player advancement endpoint validates SPP costs, Primary/Secondary skill access, random/selected skill choices and Characteristic improvement rolls.
  - Player and team value are recalculated after every advancement.

### High priority

### Medium priority

- [X] Team value calculation [DONE]

  - Centralized official TV/CTV calculation in the backend.
  - Full TV includes current player values, gained skills/characteristic increases, Team Re-rolls and Sideline Staff.
  - CTV subtracts players unable to play the next game.
  - Treasury and Dedicated Fans are explicitly excluded from TV/CTV.
- [X] Player availability maintenance [DONE]

  - Backend validates match squads/events/MVP/aftermatch inputs against available selected players.
  - `Miss Next Game` players are excluded from match selection and recover after missing the fixture.
  - Match-day Star Players are stored as temporary signings and automatically released after the match.
- [X] Generic rules catalogue [DONE]

  - Centralized backend catalogue index at `/rules/catalogue`.
  - Generic document lookup at `/rules/catalogue/{rule_id}` for every backend-owned rules document.
  - Catalogue covers casualty, injury, weather, kick-off, Prayers to Nuffle, expensive mistakes, inducements, advancements, winnings, Dedicated Fans and SPP rewards.
  - Dice semantics such as D3, D6, D8, D16 and 2D6 stay as compact metadata/helpers around the real persisted rule tables.

12. **Redraft / end-of-season rules**

- Redraft budget.
- Re-hiring players.
- Agent fees / season count if implemented later.

### Suggested backend structure

```text
rules_catalog
  expensive_mistakes
  spp_rewards
  injury_table
  casualty_table
  weather_table
  kickoff_table
  inducements
  advancement_rules

services
  RulesService
  AftermatchService
  PlayerProgressionService
  TreasuryService
```

Recommended next implementation: **Redraft / end-of-season rules**.
