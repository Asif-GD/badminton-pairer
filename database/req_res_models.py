"""
These models serve as a blueprint of the Requests and Responses.
"""
from pydantic import BaseModel, ConfigDict, field_validator


class RegisterPlayersRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "players": ["Alex_Adams", "Bob", "Chris", "Dylan"]
            }
        }
    )

    players: list[str]  # list of names entered by the user, one per line in the Discord modal

    @field_validator("players")
    @classmethod
    def validate_players(cls, v):
        # rejects an empty list -- if user submits with no names, or blank lines
        if not v:
            raise ValueError("Players field cannot be empty.")

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
