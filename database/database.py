from typing import Final, Annotated

from fastapi import Depends, Request
from pymongo.asynchronous.database import AsyncDatabase

"""
    Specify the database details.
"""
# MONGO_DB_USERNAME: Final[str] = ""  # -> not used
# MONGO_DB_PASSWORD: Final[str] = ""  # -> not used
MONGO_DB_HOST: Final[str] = "localhost"
MONGO_DB_PORT: Final[int] = 27017  # -> default port
MONGO_DB_NAME: Final[str] = "pair-db"

# uri format -> f"mongodb://{MONGO_DB_USERNAME}:{MONGO_DB_PASSWORD}@{MONGO_DB_HOST}:{MONGO_DB_PORT}/{MONGO_DB_NAME}"
MONGO_DB_URI: Final[str] = f"mongodb://{MONGO_DB_HOST}:{MONGO_DB_PORT}/{MONGO_DB_NAME}"

"""
- the AsyncMongoClient will be called in the lifespan event stage in main.py.
- if we initialize AsyncMongoClient() here, the connection is established during imports, 
    and not when the app starts. We do not want that.
"""


# This does NOT open a new connection — it just returns a handle that borrows from the AsyncMongoClient's
# existing pool, so calling it per-request is cheap and safe.
def get_db(request: Request) -> AsyncDatabase:
    # get_database() uses the database name in URI by default.
    return request.app.state.mongo_client.get_database(name=MONGO_DB_NAME)


# routes just declare `db: db_dependency` instead of repeating `Depends(get_db)` everywhere.
db_dependency = Annotated[AsyncDatabase, Depends(get_db)]
