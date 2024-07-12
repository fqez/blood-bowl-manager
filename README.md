# Blood Bowl League Manager

This is the backend for the Blood Bowl League Manager. It is a RESTful API that is built using the FastAPI framework. The API is designed to be used with the [Blood Bowl League Manager Frontend](). The Frontend aims to be built using Kivy, a Python framework for building multi-platform applications with the same codebase.

## Installation

## Usage

## Contributing

This project is open to contributions. If you would like to contribute, please follow the steps below:

1. Fork the repository
2. Create a new branch (`git checkout -b feature/feature-name`)
3. Commit your changes (`git commit -am 'Add some feature'`)
4. Push to the branch (`git push origin feature/feature-name`)
5. Create a new Pull Request

## License

This project is licensed under Creative Commons Zero v1.0 Universal.

Based on [Youngestdev's FastAPI Template](https://github.com/Youngestdev/fastapi-mongo)


## TODO


### Database (5/9)
![](https://progress-bar.dev/55)

- [x] Create Base Teams collection
- [x] Create Teams collection
- [x] Create Players collection
- [x] Create Matches collection
- [x] Create Perks collection
- [ ] Create Tournaments collection
- [ ] Create Leaderboards collection
- [ ] Create Match Results collection
- [ ] Create Users collection

### API (24/48)
![](https://progress-bar.dev/50)

- [x] Create a FastAPI project
- [x] Create a MongoDB connection
- [x] JWT Authentication

#### Teams (8/15)

- [ ] CRUD for Base Teams
    - [ ] Create a new Base Team
    - [ ] Get a Base Team
    - [ ] Edit a Base Team
    - [ ] Delete a Base Team
    - [ ] Get all Base Teams
- [-] CRUD for Teams
    - [x] Team schemas
    - [x] Create a new Team
        - [x] Create the roster for the Team
    - [x] Get Teams
        - [x] Project characters into Team response
    - [x] Edit a Team (not players, just team info)
    - [x] Delete a Team
        - [x] Delete all Players in a Team
        - [ ] Delete Team from Leaderboard
    - [ ] Get all Teams in a Tournament

#### Players (8/8)

- [x] CRUD for Players
    - [x] Player schemas
    - [x] Create a new Player
        - [x] Create a new Player in a Team
    - [x] Get Players
        - [x] Project perks into Player response
    - [x] Edit a Player
    - [x] Delete a Player
        - [x] Delete a Player from a Team

#### Perks (5/5)

- [-] CRUD for Perks
    - [x] Perk schemas
    - [x] Create a new Perk
    - [x] Get Perks
    - [x] Edit a Perk
    - [x] Delete a Perk

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
- [x] Create a Domain Model for Players
- [x] Create a Domain Model for Perks
- [ ] Create a Domain Model for Matches
- [ ] Create a Domain Model for Tournaments
- [ ] Create a Domain Model for Leaderboards
- [ ] Create a Domain Model for Match Results
- [ ] Create a Domain Model for Users
- [x] Dependency Injection for database
- [x] FastAPI exception handling


### Infrastructure (2/8)

![](https://progress-bar.dev/25)

- [x] Configure a MongoDB database
- [x] Create a docker-compose file for database
- [ ] Create a docker-compose file for backend
- [ ] Create a Dockerfile
- [ ] Study deployment options
    - [ ] Database deployment (MongoDB Atlas?)
    - [ ] API deployment (Heroku? AWS? Azure? Google Cloud? Cloudflare? Free hosting?)
    - [ ] Create a CI/CD pipeline
    - [ ] Configure GitHub Actions workflows
