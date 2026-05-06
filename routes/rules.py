"""Routes for database-backed Blood Bowl rules."""

from fastapi import APIRouter, HTTPException, status

from schemas.rules import ExpensiveMistakesRulesResponse
from services.rules_service import RulesService

router = APIRouter(prefix="/rules", tags=["Rules"])


@router.get("/expensive-mistakes", response_model=ExpensiveMistakesRulesResponse)
async def get_expensive_mistakes_rules():
    """Get the expensive mistakes rule table."""
    rules = await RulesService.get_expensive_mistakes_rules()
    if not rules:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expensive mistakes rules not found",
        )
    return rules
