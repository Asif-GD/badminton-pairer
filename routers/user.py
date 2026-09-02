from typing import Final

from fastapi import APIRouter, HTTPException
from pymongo.asynchronous.collection import ReturnDocument
from starlette import status

from database.models import user_sessions_dependency
from database.req_res_models import ListPlayersResponse, NewPlayersRequest

user_router = APIRouter(
    prefix="/user",
    tags=["user"],
)

# test accounts
FOUR_PLAYERS: Final[str] = "place_holder_4"
FIVE_PLAYERS: Final[str] = "place_holder_5"
SIX_PLAYERS: Final[str] = "place_holder_6"
SEVEN_PLAYERS: Final[str] = "place_holder_7"
EIGHT_PLAYERS: Final[str] = "place_holder_8"
NINE_PLAYERS: Final[str] = "place_holder_9"
TEN_PLAYERS: Final[str] = "place_holder_10"
ELEVEN_PLAYERS: Final[str] = "place_holder_11"
TWELVE_PLAYERS: Final[str] = "place_holder_12"


@user_router.get(
    "/list",
    response_model=ListPlayersResponse,
    description="Lists the players registered under user.",
    status_code=status.HTTP_200_OK
)
async def list_players(user_sessions: user_sessions_dependency) -> ListPlayersResponse:
    """
        Lists players registered under the user.
    :param user_sessions:
    :return:
    """

    username = FOUR_PLAYERS

    filter_query = {
        "username": username
    }

    projection = {
        "username": 1,
        "no_of_players": 1,
        "players": 1,
        "_id": 0
    }

    doc = await user_sessions.find_one(filter_query, projection)

    if doc is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No players registered under user '{username}'"
        )

    db_username = doc["username"]
    db_no_of_players = doc["no_of_players"]
    db_players = doc["players"]
    db_players = ", ".join(db_players)  # -> converts list[str] to str

    response = ListPlayersResponse(
        username=db_username,
        no_of_players=db_no_of_players,
        players=db_players
    )

    return response


@user_router.patch(
    "/update",
    response_description="Edits the registered players under user.",
    status_code=status.HTTP_200_OK
)
async def update_players(request: NewPlayersRequest, user_sessions: user_sessions_dependency) \
        -> ListPlayersResponse:
    """
        Edits the registered players under user.
    :param request:
    :param user_sessions: 
    :return:
    """
    username = FOUR_PLAYERS
    filter_query = {
        "username": username
    }
    fields_to_update = {
        "players": request.players
    }

    doc = await user_sessions.find_one_and_update(
        filter_query,
        update={
            "$set": fields_to_update
        },
        return_document=ReturnDocument.AFTER,  # return document after update.
    )

    if doc is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="User session not found. Please register.")

    db_username = doc["username"]
    db_no_of_players = doc["no_of_players"]
    db_players = doc["players"]
    db_players = ", ".join(db_players)  # convert list[str] -> str

    response = ListPlayersResponse(
        username=db_username,
        no_of_players=db_no_of_players,
        players=db_players
    )

    return response
# delete
