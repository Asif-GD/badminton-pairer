"""
Models serve as a blueprint of the table in the database.
"""
from typing import Annotated

from fastapi import Depends
from pydantic import BaseModel, BeforeValidator, ConfigDict, Field
from pymongo.asynchronous.collection import AsyncCollection

from database.database import db_dependency

# PyObjectId — bridges MongoDB's ObjectId and Pydantic/JSON's str
"""
- MongoDB stores "_id" as a BSON ObjectId, and isn't JSON-serializable. 
- `BeforeValidator(str)` runs str() on the incoming value BEFORE Pydantic validates it as a plain string. 
- This means a raw Mongo doc can be unpacked directly into a model (e.g. Model(**doc)) 
    with no manual reshaping step required.
"""
PyObjectId = Annotated[str, BeforeValidator(str)]


class UserSession(BaseModel):
    """
        Container for a single record, as stored in / returned from MongoDB.
    """
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "_id": "507f1f77bcf86cd799439011",
                "username": "discord_username",
                "session_id": "abc123",
                "no_of_players": 3,
                "players": ["Alex", "Bob", "Chris", "Dylan", "Eric"],
                "benched_players": ["Eric"],
                "lucky_players": ["Bob"],
                "seventh_player": "Fred",
            }
        }
    )

    id: PyObjectId | None = Field(alias="_id", default=None)
    username: str  # retrieved via discord bot
    session_id: str  # generated using get_session_id()

    no_of_players: int  # required
    players: list[str]  # required -- every session must have players

    """
        - better to use 'default_factory=list' and not use '[]' at class level;
        - because there is a possibility that a '[]' will become a single shared mutable object, 
        - reused across all instance of this class;
        - a default_factory avoids that by creating a fresh empty list per instance.
    """
    # empty list default -- not every session has a benched_player
    benched_players: list[str] = Field(default_factory=list)
    # empty list default -- not every session has a lucky_player
    lucky_players: list[str] = Field(default_factory=list)

    seventh_player: str | None = None  # optional, single value -- only one seventh player every rotation


def get_user_sessions_collection(db: db_dependency) -> AsyncCollection:
    return db.get_collection("user_sessions")


user_sessions_dependency = Annotated[AsyncCollection, Depends(get_user_sessions_collection)]
