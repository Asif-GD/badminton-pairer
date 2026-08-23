"""
Models serve as a blueprint of the table in the database.
"""
from typing import Annotated, Optional

from pydantic import BaseModel, BeforeValidator, ConfigDict, Field

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
                "username": "username",
                "session_id": "abc123",
                "no_of_players": 3,
                "players": ["Alex", "Bob", "Chris"],
                "benched_player": ["Dylan"],
                "lucky_player": ["Eric"],
                "seventh_player": "Fred",
            }
        }
    )

    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    username: str = Field(default="username")  # retrieved via discord bot
    session_id: str  # generated using get_session_id()

    no_of_players: int  # required
    players: list[str]  # required -- every session must have players

    benched_player: list[str] | None = None  # optional -- not every session has a benched_player
    lucky_player: list[str] | None = None  # optional -- not every session has a lucky_player
    seventh_player: str | None = None  # optional, single value -- only one seventh player every rotation
