"""
These models serve as a blueprint of the Requests and Responses.
"""
from typing import Final

from pydantic import BaseModel, ConfigDict, field_validator, Field, computed_field

from validators import normalize_and_check_duplicates

MIN_PLAYER_COUNT: Final[int] = 4
MAX_PLAYER_COUNT: Final[int] = 12
MIN_SPLIT_PLAYER_COUNT: Final[int] = 3


class NewPlayersRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "players": ["Alex_Adams", "Bob", "Chris", "Dylan"]
            }
        }
    )
    # list of names entered by the user, one per line in the Discord modal.
    # bot strips leading/trailing whitespace per name before this reaches the API
    # Field(min_length=...) -> documents the rule in the OpenAPI schema (minItems: 4, maxItems: 12)
    players: list[str] = Field(min_length=MIN_PLAYER_COUNT, max_length=MAX_PLAYER_COUNT)

    # mode="before" -> runs BEFORE Pydantic's built-in checks, including min_length, max_length
    # so our friendly message is raised first and Pydantic's generic one never appears.
    @field_validator("players", mode="before")
    @classmethod
    def validate_number_of_players(cls, value: object) -> object:
        # only supports 4 - 12 players for now.
        # the input is still raw here (could be anything), so guard before calling len()
        if isinstance(value, list) and not (MIN_PLAYER_COUNT <= len(value) <= MAX_PLAYER_COUNT):
            raise ValueError(f"Only {MIN_PLAYER_COUNT} to {MAX_PLAYER_COUNT} players are supported. "
                             f"(got {len(value)}).")

        return value

    @field_validator("players")
    @classmethod
    def validate_players(cls, value: list[str]) -> list[str]:
        # checks for all per-name rules (length, whitespace, allowed characters, capitalization) and duplicates.
        normalized_names: list[str] = normalize_and_check_duplicates(value)

        return normalized_names


class NewPlayersResponse(BaseModel):
    model_config = ConfigDict(
        validate_by_name=True,
        validate_by_alias=True,
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
                "benched_players": "Eric"
            }
        }
    )

    teams: dict[str, str]
    benched_players: str


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
    # a minimum of 3 players: 1 can't be split, 2 doesn't need this endpoint's help
    # Field(min_length=...) -> documents the rule in the OpenAPI schema (minItems: 3)
    players: list[str] = Field(min_length=MIN_SPLIT_PLAYER_COUNT)

    # mode="before" -> runs BEFORE Pydantic's built-in checks, including min_length,
    # so our friendly message is raised first and Pydantic's generic one never appears.
    @field_validator("players", mode="before")
    @classmethod
    def validate_number_of_players(cls, value: object) -> object:
        # the input is still raw here (could be anything), so guarding it before calling len()
        if isinstance(value, list) and len(value) < MIN_SPLIT_PLAYER_COUNT:
            raise ValueError(f"A minimum of {MIN_SPLIT_PLAYER_COUNT} players required. "
                             f"(got {len(value)}).")

        return value

    @field_validator("players")
    @classmethod
    def validate_players(cls, value: list[str]) -> list[str]:
        # checks for all per-name rules (length, whitespace, allowed characters, capitalization) and duplicates.
        normalized_names: list[str] = normalize_and_check_duplicates(value)

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
        return len(self.teams) * 2 + (1 if self.unpaired_player is not None else 0)

    @computed_field  # marks this as a schema field, even though it's not stored
    @property
    def no_of_teams(self) -> int:
        # always derived -- never set directly, never goes stale
        return len(self.teams)


class DeleteUserResponse(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "message": "User {username} has been deleted."
            }
        }
    )

    message: str
