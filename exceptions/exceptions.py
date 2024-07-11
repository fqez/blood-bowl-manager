from fastapi import HTTPException


class TeamNotFoundException(HTTPException):
    def __init__(self, team_id: str):
        detail = f"Team {team_id} not found"
        super().__init__(status_code=404, detail=detail)


class PlayerNotFoundException(HTTPException):
    def __init__(self, player_id: str):
        detail = f"Team {player_id} not found"
        super().__init__(status_code=404, detail=detail)


class PerkNotFoundException(HTTPException):
    def __init__(self, perk_id: str):
        detail = f"Team {perk_id} not found"
        super().__init__(status_code=404, detail=detail)
