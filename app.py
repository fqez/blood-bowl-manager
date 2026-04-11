from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from auth.jwt_bearer import get_current_user
from config.config import initiate_database
from exceptions import exception_handlers
from routes.admin import router as AdminRouter
from routes.auth import router as AuthRouter
from routes.base_roster import router as BaseRosterRouter
from routes.character import router as CharacterRouter
from routes.league import router as LeagueRouter
from routes.perk import router as PerkRouter
from routes.star_player import router as StarPlayerRouter
from routes.team import router as TeamRouter
from routes.user_team import router as UserTeamRouter


@asynccontextmanager
async def lifespan(app: FastAPI):
    await initiate_database()
    yield


app = FastAPI(lifespan=lifespan)

# CORS configuration for Flutter web frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

exception_handlers.add_exception_handlers(app)


@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Welcome to this fantastic app."}


app.include_router(AdminRouter, tags=["Administrator"], prefix="/admin")
app.include_router(AuthRouter)  # Public: /auth/register, /auth/login, /auth/refresh
app.include_router(PerkRouter, tags=["perks"], prefix="/perks")
app.include_router(TeamRouter, tags=["teams"], prefix="/teams")
app.include_router(CharacterRouter, tags=["characters"], prefix="/characters")

# New routes for the restructured data model (public catalog)
app.include_router(BaseRosterRouter)
app.include_router(StarPlayerRouter)

# Protected routes: require valid JWT
app.include_router(UserTeamRouter, dependencies=[Depends(get_current_user)])
app.include_router(LeagueRouter, dependencies=[Depends(get_current_user)])
