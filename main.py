from contextlib import asynccontextmanager

from fastapi import FastAPI
from pymongo import AsyncMongoClient

from database.database import MONGO_DB_URI
from routers.pair import pair_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
        The prerequisite setup before the app starts and/or cleanup after the app ends
    """
    # startup events goes here
    """
        - this ensures that exactly one open and one close for the whole app's lifecycle.
        - `app.state` is used, so route dependencies can reach it via the request.
    """
    app.state.mongo_client = AsyncMongoClient(MONGO_DB_URI)
    yield
    # shutdown events goes here
    await app.state.mongo_client.close()


app = FastAPI(
    title="Badminton Pair'r",
    lifespan=lifespan
)

app.include_router(router=pair_router)


@app.get("/")
async def root():
    return {"Hello World": "It works!"}
