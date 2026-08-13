from contextlib import asynccontextmanager

from fastapi import FastAPI

from database.database import create_db_and_tables
from routers.pair import pair_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
        The prerequisite setup before the app starts and/or cleanup after the app ends
    """
    # startup events goes here
    """
        Although this is called everytime on startup, it won't execute unless the db-file is missing.
        So to make changes on db, delete the db-file after adding the changes.
    """
    # create the db file and tables
    create_db_and_tables()
    yield
    # shutdown events goes here


app = FastAPI(lifespan=lifespan)

app.include_router(router=pair_router)


@app.get("/")
async def root():
    return {"Hello World": "It works!"}
