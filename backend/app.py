from contextlib import asynccontextmanager

from auth.jwt_bearer import JWTBearer
from config.config import initiate_database
from fastapi import Depends, FastAPI
from routes.admin import router as AdminRouter
from routes.student import router as StudentRouter

token_listener = JWTBearer()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await initiate_database()
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Welcome to this fantastic app."}


app.include_router(AdminRouter, tags=["Administrator"], prefix="/admin")
app.include_router(
    StudentRouter,
    tags=["Students"],
    prefix="/student",
    dependencies=[Depends(token_listener)],
)
