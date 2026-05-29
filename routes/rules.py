"""Routes for database-backed Blood Bowl rules."""

from fastapi import APIRouter, HTTPException, status

from schemas.rules import (
    AdvancementRulesResponse,
    DedicatedFansRulesResponse,
    ExpensiveMistakesRulesResponse,
    InducementRulesResponse,
    InjuryRulesResponse,
    KickoffEventRulesResponse,
    LeaguePointsRulesResponse,
    RuleCatalogDocumentResponse,
    RuleCatalogResponse,
    SppRewardsRulesResponse,
    WeatherRulesResponse,
    WinningsRulesResponse,
)
from services.rules_service import RulesService

router = APIRouter(prefix="/rules", tags=["Rules"])


@router.get("/catalogue", response_model=RuleCatalogResponse)
async def get_rules_catalogue():
    """Get the generic backend-owned rules catalogue index."""
    return await RulesService.get_rules_catalogue()


@router.get("/catalogue/{rule_id}", response_model=RuleCatalogDocumentResponse)
async def get_catalogue_document(rule_id: str):
    """Get one raw rules document from the generic catalogue."""
    document = await RulesService.get_catalogue_document(rule_id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Rules document '{rule_id}' not found",
        )
    return document


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


@router.get("/spp-rewards", response_model=SppRewardsRulesResponse)
async def get_spp_rewards_rules():
    """Get the SPP reward rule table."""
    rules = await RulesService.get_spp_rewards_rules()
    if not rules:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="SPP reward rules not found",
        )
    return rules


@router.get("/advancements", response_model=AdvancementRulesResponse)
async def get_advancement_rules():
    """Get the player advancement cost and value tables."""
    rules = await RulesService.get_advancement_rules()
    if not rules:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Advancement rules not found",
        )
    return rules


@router.get("/injuries", response_model=InjuryRulesResponse)
async def get_injury_rules():
    """Get the injury, casualty and lasting injury rule tables."""
    rules = await RulesService.get_injury_rules()
    if not rules:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Injury rules not found",
        )
    return rules


@router.get("/winnings", response_model=WinningsRulesResponse)
async def get_winnings_rules():
    """Get the post-game winnings formula."""
    rules = await RulesService.get_winnings_rules()
    if not rules:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Winnings rules not found",
        )
    return rules


@router.get("/league-points", response_model=LeaguePointsRulesResponse)
async def get_league_points_rules():
    """Get the post-game league points formula."""
    rules = await RulesService.get_league_points_rules()
    if not rules:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="League points rules not found",
        )
    return rules


@router.get("/dedicated-fans", response_model=DedicatedFansRulesResponse)
async def get_dedicated_fans_rules():
    """Get the post-game Dedicated Fans update rules."""
    rules = await RulesService.get_dedicated_fans_rules()
    if not rules:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dedicated Fans rules not found",
        )
    return rules


@router.get("/inducements", response_model=InducementRulesResponse)
async def get_inducement_rules():
    """Get the inducement catalog and pre-game petty cash rules."""
    rules = await RulesService.get_inducement_rules()
    if not rules:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inducement rules not found",
        )
    return rules


@router.get("/weather", response_model=WeatherRulesResponse)
async def get_weather_rules():
    """Get the official 2D6 Weather table."""
    rules = await RulesService.get_weather_rules()
    if not rules:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Weather rules not found",
        )
    return rules


@router.get("/kickoff-events", response_model=KickoffEventRulesResponse)
async def get_kickoff_event_rules():
    """Get the official 2D6 Kick-off Event table."""
    rules = await RulesService.get_kickoff_event_rules()
    if not rules:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Kick-off event rules not found",
        )
    return rules
