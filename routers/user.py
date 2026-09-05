from typing import Final

from fastapi import APIRouter, HTTPException
from pymongo.asynchronous.collection import ReturnDocument
from pymongo.results import DeleteResult, UpdateResult
from starlette import status

from database.models import user_sessions_dependency
from database.req_res_models import ListPlayersResponse, NewPlayersRequest, MAX_PLAYER_COUNT, MIN_PLAYER_COUNT

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
    :param user_sessions: Injected user_sessions collections dependency.
    :return: The list of players registered under the user.
    :raises HTTPException 404: If no session exists for user.
    """
    # TODO: hardcoded for now -- will come from the discord bot.
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
            detail=f"No session found for user: '{username}'. Please register."
        )

    db_username = doc["username"]
    db_no_of_players = doc["no_of_players"]
    db_players = doc["players"]
    players_display = ", ".join(db_players)  # -> converts list[str] to str

    response = ListPlayersResponse(
        username=db_username,
        no_of_players=db_no_of_players,
        players=players_display
    )

    return response


@user_router.patch(
    "/add_player/{player_name}",
    response_description="Adds a player to the list of registered players under the user.",
    status_code=status.HTTP_200_OK
)
async def add_player(name: str, user_sessions: user_sessions_dependency) -> ListPlayersResponse:
    """
        Adds a player to the list of registered players under the user.
    :param name: Incoming path parameter that holds the player's name to be added.
    :param user_sessions: Injected user_sessions collections dependency
    :return: The updated players list for the user.
    :raises HTTPException 404: If no session exists for user.
    :raises HTTPException 400: If player already registered under user, or user has maximum number of players registered.
    """
    # TODO: hardcoded for now -- will come from the discord bot.
    username: str = FIVE_PLAYERS
    # TODO: set path parameter validation and handle this there
    name = name.capitalize()

    """
        filter_query -> find user session of 'username' where 'name' isn't already registered under user 
            and number of players is less than MAX_PLAYER_COUNT
    """
    filter_query: dict = {
        "username": username,
        "players": {
            "$ne": name  # -> no duplicates allowed
        },
        "$expr": {
            "$lt": [{"$size": "$players"}, MAX_PLAYER_COUNT]  # number of players cannot exceed MAX_PLAYER_COUNT
        }
    }

    """
        update_pipeline -> update happens as an aggregate-pipeline update because the 'no_of_players' should
            reflect the length of 'players' after the player has been added.        
    """
    update_pipeline: list[dict] = [
        {
            "$set": {
                "players": {
                    "$concatArrays": ["$players", [name]]  # -> adds the new player
                },
                # Resetting benched/lucky/seventh player on update,
                # since a new player list invalidates any previous rotation assignment.
                "benched_players": [],
                "lucky_players": [],
                "seventh_player": None
            }
        },
        {
            "$set": {
                "no_of_players": {
                    "$size": "$players"  # -> sets the size of length of the 'players'
                }
            }
        }
    ]

    doc = await user_sessions.find_one_and_update(
        filter_query,
        update_pipeline,
        return_document=ReturnDocument.AFTER
    )

    """
        doc could be None for multiple reasons
            - 1. username wasn't found
            - 2. player already registered under user
            - 3. user has max number of players registered.
    """
    if doc is None:
        existing_user_doc = await user_sessions.find_one({"username": username})

        # 1. username wasn't found
        if existing_user_doc is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No user with user: '{username}' found. Please register."
            )

        # 2. player already registered under user
        if name in existing_user_doc["players"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Player already registered under this user. No duplicate entries allowed."
            )

        # if neither 1 and 2, user has maximum players registered already.
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot add new player. User has {existing_user_doc['no_of_players']} players registered. "
                   f"Number of players allowed per user: {MIN_PLAYER_COUNT} to {MAX_PLAYER_COUNT}."
        )

    db_username = doc["username"]
    db_no_of_players = doc["no_of_players"]
    db_players = doc["players"]
    players_display = ", ".join(db_players)  # -> convert list[str] to str

    response = ListPlayersResponse(
        username=db_username,
        no_of_players=db_no_of_players,
        players=players_display
    )

    return response


@user_router.patch(
    "/update",
    response_description="Edits the registered players under user.",
    status_code=status.HTTP_200_OK
)
async def update_players(new_players: NewPlayersRequest, user_sessions: user_sessions_dependency) \
        -> ListPlayersResponse:
    """
        Edits the registered players under user.
    :param new_players: Incoming request body containing the new list of players.
    :param user_sessions: Injected user_sessions collection dependency.
    :return: The updated players list for the user.
    :raises HTTPException 404: If no session exists for user.
    """
    # TODO: hardcoded for now -- will come from the discord bot.
    username = FOUR_PLAYERS
    filter_query = {
        "username": username
    }
    fields_to_update = {
        "players": new_players.players,
        "no_of_players": len(new_players.players),
        # Resetting benched/lucky/seventh player on update,
        # since a new player list invalidates any previous rotation assignment.
        "benched_players": [],
        "lucky_players": [],
        "seventh_player": None
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
                            detail=f"No session found for user '{username}'. Please register.")

    db_username = doc["username"]
    db_no_of_players = doc["no_of_players"]
    db_players = doc["players"]
    players_display = ", ".join(db_players)  # convert list[str] -> str, kept as separate name.

    response = ListPlayersResponse(
        username=db_username,
        no_of_players=db_no_of_players,
        players=players_display
    )

    return response


@user_router.delete(
    "/delete",
    response_description="Deletes the user session.",
    status_code=status.HTTP_200_OK
)
async def delete_user(user_sessions: user_sessions_dependency):
    """
        Deletes the user session.
    :param user_sessions: Injected user_sessions collection dependency.
    :return: A dict with a confirmation message.
    :raises HTTPException 404: If no session exists for user.
    """
    # TODO: hardcoded for now -- will come from the discord bot.
    username = FOUR_PLAYERS
    filter_query = {
        "username": username
    }

    # removes the first document matching the filter.
    result: DeleteResult = await user_sessions.delete_one(filter_query)

    if result.deleted_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"No session found for user '{username}'.")

    response = {
        "message": f"User {username} session has been deleted."
    }

    return response
