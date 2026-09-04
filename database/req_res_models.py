"""
These models serve as a blueprint of the Requests and Responses.
"""

from pydantic import BaseModel, ConfigDict, field_validator, Field


class NewPlayersRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "players": ["Alex_Adams", "Bob", "Chris", "Dylan"]
            }
        }
    )
    # list of names entered by the user, one per line in the Discord modal.
    players: list[str]  # (bot strips leading/trailing whitespace per name before this reaches the API)

    @field_validator("players")
    @classmethod
    def validate_players(cls, v):
        # rejects an empty list -- if user submits with no names, or blank lines
        if not v:
            raise ValueError("Players field cannot be empty.")

        # only supports 4 - 12 players for now.
        if not (4 <= len(v) <= 12):
            raise ValueError(f"Only 4 to 12 players are supported. (got {len(v)}).")

        # rejects case-insensitive duplicate names -- "Alex" and "alex" are treated as same player.
        typed_names = {name.lower() for name in v}  # -> set() doesn't support duplicate values.
        if len(typed_names) != len(v):
            raise ValueError("Players names must be unique (case-insensitive).")

        for name in v:
            # rejects any name containing whitespace -- error message tells the user exactly what format is expected
            # instead of just saying "no whitespace", so they know how to fix it
            if any(ch.isspace() for ch in name):
                raise ValueError(
                    f"Name '{name}' must not contain any whitespace. Please use a player's first name or "
                    f"use the format of 'first-name'_'last-name'."
                )

            # enforces a minimum length so single-character or two-character junk entries are rejected
            if len(name) < 3:
                raise ValueError(f"Name '{name}' must be at least 3 characters long.")

        return v


class NewPlayersResponse(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "_id": "random_string",
                "players": "Alex, Bob, Chris, Dylan",
                "status": "Players registered successfully.",
            }
        }
    )
    id: str = Field(alias="_id")
    players: str
    status: str


class PairingsResponse(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "teams": {
                    "1": "Alex, Ben",
                    "2": "Chris, Dylan"
                },
            }
        }
    )

    teams: dict[str, str]


class PairingsWithBenchedPlayerResponse(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "teams": {
                    "1": "Alex, Ben",
                    "2": "Chris, Dylan"
                },
                "benched_player": "Eric"
            }
        }
    )

    teams: dict[str, str]
    benched_player: str


class ListPlayersResponse(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "username": "username",
                "no_of_players": 4,
                "players": "Alex, Bob, Chris, Dylan"
            }
        }
    )

    username: str
    no_of_players: int
    players: str
