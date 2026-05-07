"""Routes for database-backed Blood Bowl rules."""

from fastapi import APIRouter, HTTPException, status

from schemas.rules import (
    DedicatedFansRulesResponse,
    ExpensiveMistakesRulesResponse,
    InducementRulesResponse,
    InjuryRulesResponse,
    KickoffEventRulesResponse,
    SppRewardsRulesResponse,
    WeatherRulesResponse,
    WinningsRulesResponse,
)
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
