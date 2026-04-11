from fastapi import HTTPException


class TeamNotFoundException(HTTPException):
    def __init__(self, team_id: str):
        detail = f"Team {team_id} not found"
        super().__init__(status_code=404, detail=detail)


class PlayerNotFoundException(HTTPException):
    def __init__(self, player_id: str):
        detail = f"Player {player_id} not found"
        super().__init__(status_code=404, detail=detail)


class PerkNotFoundException(HTTPException):
    def __init__(self, perk_id: str):
        detail = f"Perk {perk_id} not found"
        super().__init__(status_code=404, detail=detail)


class LeagueNotFoundException(HTTPException):
    def __init__(self, league_id: str):
        detail = f"League {league_id} not found"
        super().__init__(status_code=404, detail=detail)


class InvalidOperationException(Exception):
    """Raised when an operation cannot be completed due to business rules."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)

    def __str__(self):
        return self.message
