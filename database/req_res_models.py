"""
These models serve as a blueprint of the Requests and Responses.
"""
from typing import Final

from pydantic import BaseModel, ConfigDict, field_validator, Field, computed_field

from validators import validate_player_name

MIN_PLAYER_COUNT: Final[int] = 4
MAX_PLAYER_COUNT: Final[int] = 12


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
        if not (MIN_PLAYER_COUNT <= len(v) <= MAX_PLAYER_COUNT):
            raise ValueError(f"Only {MIN_PLAYER_COUNT} to {MAX_PLAYER_COUNT} players are supported. "
                             f"(got {len(v)}).")

        # checks for all per-name rules (length, whitespace, allowed characters, capitalization)
        normalized_names = [validate_player_name(name) for name in v]

        # rejects case-insensitive duplicate names
        if len(set(normalized_names)) != len(normalized_names):  # -> set() doesn't support duplicate values.
            raise ValueError("Players names must be unique (case-insensitive).")

        return normalized_names


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


class SplitPlayersRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "players": ['Alex', 'Bob', 'Chris', 'Dylan']
            }
        }
    )

    # list of names entered by the user, one per line in the Discord modal.
    # (bot strips leading/trailing whitespace per name before this reaches the API)
    players: list[str] = Field(min_length=3)  # min 3: 1 can't be split, 2 doesn't need this endpoint's help

    @field_validator("players")
    @classmethod
    def validate_players(cls, value: list[str]) -> list[str]:
        # checks for all per-name rules (length, whitespace, allowed characters, capitalization)
        normalized_names = [validate_player_name(name) for name in value]

        # rejects case-insensitive duplicate names
        if len(set(normalized_names)) != len(normalized_names):  # -> set() doesn't support duplicate values.
            raise ValueError("Players names must be unique (case-insensitive).")

        return normalized_names


class SplitPlayersResponse(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "no_of_players": 4,
                "teams": {
                    "1": "Bob, Dylan",
                    "2": "Alex, Chris"
                },
                "unpaired_player": None,
                "no_of_teams": 2
            }
        }
    )

    teams: dict[str, str]
    unpaired_player: str | None = None

    @computed_field  # marks this as a schema field, even though it's not stored
    @property
    def no_of_players(self) -> int:
        # always derived -- never set directly, never goes stale
        return len(self.teams) * 2 + (1 if self.unpaired_player else 0)

    @computed_field  # marks this as a schema field, even though it's not stored
    @property
    def no_of_teams(self) -> int:
        # always derived -- never set directly, never goes stale
        return len(self.teams)
