from contextlib import asynccontextmanager

import motor
from beanie import init_beanie
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles


from config import config

from models import Game, Player
from routes import api_router
from ws import ws_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    client = motor.motor_asyncio.AsyncIOMotorClient(
        config.mongo_dsn
    )

    # await init_beanie(client.beanie_db, document_models=[Game, Player])

    # Load the ML model
    yield
    # Clean up the ML models and release the resources

app = FastAPI(lifespan=lifespan)

app.mount("/assets", StaticFiles(directory="static/assets"), name="static")

app.include_router(api_router)
app.include_router(ws_router)

