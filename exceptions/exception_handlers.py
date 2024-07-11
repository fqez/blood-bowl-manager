# exception_handlers.py
from fastapi.responses import JSONResponse
from pymongo.errors import DuplicateKeyError, OperationFailure

from .exceptions import (
    PerkNotFoundException,
    PlayerNotFoundException,
    TeamNotFoundException,
)


def add_exception_handlers(app):
    @app.exception_handler(TeamNotFoundException)
    async def team_not_found_exception_handler(request, exc: TeamNotFoundException):
        return JSONResponse(
            status_code=404,
            content={"message": exc.detail},
        )

    @app.exception_handler(PlayerNotFoundException)
    async def player_not_found_exception_handler(request, exc: PlayerNotFoundException):
        return JSONResponse(
            status_code=404,
            content={"message": exc.detail},
        )

    @app.exception_handler(PerkNotFoundException)
    async def perk_not_found_exception_handler(request, exc: PerkNotFoundException):
        return JSONResponse(
            status_code=404,
            content={"message": exc.detail},
        )

    @app.exception_handler(OperationFailure)
    async def operation_failure_handler(request, exc: OperationFailure):
        return JSONResponse(
            status_code=500,
            content={"message": f"MongoDB operation failed: {exc}"},
        )

    # Exception handler for DuplicateKeyError
    @app.exception_handler(DuplicateKeyError)
    async def duplicate_key_error_handler(request, exc: DuplicateKeyError):
        return JSONResponse(
            status_code=400,
            content={"message": "Duplicated entity"},
        )

    # Generic exception handler
    @app.exception_handler(Exception)
    async def generic_exception_handler(request, exc: Exception):
        return JSONResponse(
            status_code=500,
            content={"message": f"An unexpected error occurred: {exc}"},
        )
