# Contexto para Claude

vale, la idea con esta aplicación es que pueda gestionar ligas con ella además de consultar habilidades, perks, leaderboards, etc. Mi idea inicial era tener una base de datos con los equipos, jugadores y perks por defecto (cada personaje tiene unas habilidades y stats basicos que se pueden ir modificando a lo largo de la liga). Con esta aplicación el usuario debería poder seleccionar uno de los equipos que existen en el juego (no muertos, orcos, humanos, etc) y poder seleccionar jugadores para formar su equipo en base a un presupuesto.

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

## TODO

### Database (5/9)

![](https://progress-bar.dev/55)

- [X] Create Base Teams collection
- [X] Create Teams collection
- [X] Create Players collection
- [X] Create Matches collection
- [X] Create Perks collection
- [ ] Create Tournaments collection
- [ ] Create Leaderboards collection
- [ ] Create Match Results collection
- [ ] Create Users collection

### API (24/48)

![](https://progress-bar.dev/50)

- [X] Create a FastAPI project
- [X] Create a MongoDB connection
- [X] JWT Authentication

#### Teams (8/15)

- [ ] CRUD for Base Teams
  - [ ] Create a new Base Team
  - [ ] Get a Base Team
  - [ ] Edit a Base Team
  - [ ] Delete a Base Team
  - [ ] Get all Base Teams

- [-] CRUD for Teams
  - [X] Team schemas
  - [X] Create a new Team
    - [X] Create the roster for the Team
  - [X] Get Teams
    - [X] Project characters into Team response
  - [X] Edit a Team (not players, just team info)
  - [X] Delete a Team
    - [X] Delete all Players in a Team
    - [ ] Delete Team from Leaderboard
  - [ ] Get all Teams in a Tournament

#### Players (8/8)

- [X] CRUD for Players
  - [X] Player schemas
  - [X] Create a new Player
    - [X] Create a new Player in a Team
  - [X] Get Players
    - [X] Project perks into Player response
  - [X] Edit a Player
  - [X] Delete a Player
    - [X] Delete a Player from a Team

#### Perks (5/5)

- [-] CRUD for Perks
  - [X] Perk schemas
  - [X] Create a new Perk
  - [X] Get Perks
  - [X] Edit a Perk
  - [X] Delete a Perk

#### Matches (0/6)

- [ ] CRUD for Matches
  - [ ] Match schemas
  - [ ] Create a new Match
  - [ ] Get a Match
  - [ ] Edit a Match
  - [ ] Delete a Match
  - [ ] Get all Matches

#### Tournaments (0/5)

- [ ] CRUD for Tournaments
  - [ ] Tournament schemas
  - [ ] Create a new Tournament
  - [ ] Get Tournaments
  - [ ] Edit a Tournament
  - [ ] Delete a Tournament

#### Leaderboards (0/6)

- [ ] CRUD for Leaderboards
  - [ ] Leaderboard schemas
  - [ ] Create a new Leaderboard
  - [ ] Get a Leaderboard
  - [ ] Edit a Leaderboard
  - [ ] Delete a Leaderboard
  - [ ] Get all Leaderboards for a User

### Domain Models (5/11)

![](https://progress-bar.dev/45)

- [ ] Create a Domain Model for Base Teams

- [-] Create a Domain Model for Teams
  - [ ] Add Team stats

- [X] Create a Domain Model for Players
- [X] Create a Domain Model for Perks
- [ ] Create a Domain Model for Matches
- [ ] Create a Domain Model for Tournaments
- [ ] Create a Domain Model for Leaderboards
- [ ] Create a Domain Model for Match Results
- [ ] Create a Domain Model for Users
- [X] Dependency Injection for database
- [X] FastAPI exception handling

### Testing (0/20)

![](https://progress-bar.dev/0)

- [ ] Unit tests for Teams
- [ ] Unit tests for Players
- [ ] Unit tests for Perks
- [ ] Unit tests for Matches
- [ ] Unit tests for Tournaments
- [ ] Unit tests for Leaderboards
- [ ] Unit tests for Match Results
- [ ] Unit tests for Users
- [ ] Integration tests for Teams
- [ ] Integration tests for Players
- [ ] Integration tests for Perks
- [ ] Integration tests for Matches
- [ ] Integration tests for Tournaments
- [ ] Integration tests for Leaderboards
- [ ] Integration tests for Match Results
- [ ] Integration tests for Users
- [ ] End-to-end tests
- [ ] Security tests
- [ ] Regression tests
- [ ] Code coverage

### Infrastructure (4/9)

![](https://progress-bar.dev/44)

- [X] Configure a MongoDB database
- [X] Create a docker-compose file for database
- [X] Create a Dockerfile for backend
- [X] Create a docker-compose file for backend [DONE]
- [ ] Study deployment options
  - [ ] Database deployment (MongoDB Atlas?)
  - [ ] API deployment (Heroku? AWS? Azure? Google Cloud? Cloudflare? Free hosting?)
  - [ ] Create a CI/CD pipeline (GitHub Actions)
    - [ ] PR workflow
    - [ ] Merge workflow
