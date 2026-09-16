from contextlib import asynccontextmanager

from fastapi import FastAPI
from pymongo import AsyncMongoClient

from database.database import MONGO_DB_URI, MONGO_DB_NAME
from routers.pair import pair_router
from routers.user import user_router


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

    # setting 'session_id' as unique
    """
        NOTE: MongoDB won't error or recreate the index 
            if it already exists with the same specification on every app restart.
    """
    user_sessions_collection = app.state.mongo_client[MONGO_DB_NAME]["user_sessions"]
    await user_sessions_collection.create_index("session_id", unique=True)

    yield
    # shutdown events goes here
    await app.state.mongo_client.close()


app = FastAPI(
    title="Badminton Pair'r",
    lifespan=lifespan
)

app.include_router(router=pair_router)
app.include_router(router=user_router)


@app.get("/")
async def root():
    return {"Hello World": "It works!"}
