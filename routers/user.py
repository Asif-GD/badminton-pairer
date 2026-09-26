from typing import Final, Annotated, Any

from fastapi import APIRouter, HTTPException, Depends
from pymongo.asynchronous.collection import ReturnDocument
from pymongo.results import DeleteResult
from starlette import status

from database.models import user_sessions_dependency
from database.req_res_models import ListPlayersResponse, NewPlayersRequest, MAX_PLAYER_COUNT, MIN_PLAYER_COUNT, \
    DeleteUserResponse
from validators import validate_player_name

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


# - a thin wrapper to translate validate_player_name ValueError into HTTPException.
# - this keeps the validate_player_name reusable/testable outside a request context.
def get_validated_player_name(name: str) -> str:
    """
        Translates validate_player_name ValueError into HTTPException

    :param name: The player's name.
    :return: The player's name, after validation.
    :raises HTTPException 422: If the player's name fails validation.
    """
    try:
        return validate_player_name(name)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(e))


name_validator_dependency = Annotated[str, Depends(get_validated_player_name)]


def build_list_players_response(doc: dict[str, Any]) -> ListPlayersResponse:
    """
        Builds the ListPlayersResponse using fields in document from db.

    :param doc: The document fetched from db.
    :return: ListPlayersResponse model.
    """
    db_username: str = doc["username"]
    db_no_of_players: int = doc["no_of_players"]
    db_players: list[str] = doc["players"]
    players_display: str = ", ".join(db_players)  # -> converts list[str] to str

    return ListPlayersResponse(
        username=db_username,
        no_of_players=db_no_of_players,
        players=players_display
    )


@user_router.get(
    "/list_players",
    description="Lists the players registered under user.",
    response_model=ListPlayersResponse,
    status_code=status.HTTP_200_OK
)
async def list_players(user_sessions: user_sessions_dependency) -> ListPlayersResponse:
    """
        Lists the players registered under the user.

    :param user_sessions: Injected user_sessions collections dependency.
    :return: The list of players registered under the user wrapped in ListPlayersResponse.
    :raises HTTPException 404: If no user record exists.
    """
    # TODO: hardcoded for now -- will come from the discord bot.
    username: str = FOUR_PLAYERS
    filter_query: dict[str, Any] = {
        "username": username
    }
    projection: dict[str, int] = {
        "username": 1,
        "no_of_players": 1,
        "players": 1,
        "_id": 0
    }

    doc: dict[str, Any] | None = await user_sessions.find_one(filter_query, projection)

    if doc is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No user with username: '{username}' found. Please register."
        )

    response = build_list_players_response(doc)

    return response


@user_router.patch(
    "/add_player/{name}",
    response_description="Adds a player to the list of registered players under the user.",
    response_model=ListPlayersResponse,
    status_code=status.HTTP_200_OK
)
async def add_player(name: name_validator_dependency, user_sessions: user_sessions_dependency) \
        -> ListPlayersResponse:
    """
        Adds a player to the list of registered players under the user.

    :param name: Incoming path parameter that holds the player's name to be added.
    :param user_sessions: Injected user_sessions collections dependency.
    :return: The updated players list for the user wrapped in ListPlayersResponse.
    :raises HTTPException 404: If no user record exists.
    :raises HTTPException 400: If player already registered under user,
        or user has maximum number of players registered.
    """
    # TODO: hardcoded for now -- will come from the discord bot.
    username: str = NINE_PLAYERS

    # filter_query -> find user session of 'username' where 'name' isn't already registered under user
    #     and number of players is less than MAX_PLAYER_COUNT
    filter_query: dict[str, Any] = {
        "username": username,
        "players": {
            "$ne": name  # -> no duplicates allowed
        },
        "$expr": {
            "$lt": [{"$size": "$players"}, MAX_PLAYER_COUNT]  # number of players cannot exceed MAX_PLAYER_COUNT
        }
    }

    # update_pipeline -> update happens as an aggregate-pipeline update because the 'no_of_players' should
    #     reflect the length of 'players' after the player has been added.
    update_pipeline: list[dict[str, Any]] = [
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

    doc: dict[str, Any] | None = await user_sessions.find_one_and_update(
        filter_query,
        update_pipeline,
        return_document=ReturnDocument.AFTER
    )

    # doc could be None for multiple reasons
    #     - 1. username wasn't found
    #     - 2. player already registered under user
    #     - 3. user has maximum number of players registered.
    if doc is None:
        existing_user_doc: dict[str, Any] | None = await user_sessions.find_one({"username": username})

        # 1. username wasn't found
        if existing_user_doc is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No user with username: '{username}' found. Please register."
            )

        # 2. player already registered under user
        if name in existing_user_doc["players"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Player '{name}' already registered under this user. No duplicate entries allowed."
            )

        # if neither 1 and 2, user has maximum players registered already.
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot add new player. User has {existing_user_doc['no_of_players']} players registered. "
                   f"Number of players allowed per user: {MIN_PLAYER_COUNT} to {MAX_PLAYER_COUNT}. "
                   f"Please remove another player first."
        )

    response = build_list_players_response(doc)

    return response


@user_router.patch(
    "/remove_player/{name}",
    response_description="Removes a player from the list of registered players under the user.",
    response_model=ListPlayersResponse,
    status_code=status.HTTP_200_OK
)
async def remove_player(name: name_validator_dependency, user_sessions: user_sessions_dependency) \
        -> ListPlayersResponse:
    """
        Removes a player from the list of registered players under the user.

    :param name: Incoming path parameter that holds the player's name to be removed.
    :param user_sessions: Injected user_sessions collections dependency
    :return: The updated players list for the user wrapped in ListPlayersResponse.
    :raises HTTPException 404: If no user record exists.
    :raises HTTPException 400: If player is not found registered under user,
        or user is at minimum number of players registered.
    """
    # TODO: hardcoded for now -- will come from the discord bot.
    username: str = NINE_PLAYERS

    # filter_query -> find user session of 'username' where player == 'name' and
    #     the number of players registered is greater than MIN_PLAYER_COUNT.
    filter_query: dict[str, Any] = {
        "username": username,
        "players": name,  # checks if 'name' is in the players[] list in db
        "$expr": {
            "$gt": [{"$size": "$players"}, MIN_PLAYER_COUNT]  # number of players cannot go below MIN_PLAYER_COUNT
        }
    }

    # update_pipeline -> update happens as an aggregate-pipeline update because the 'no_of_players' should
    #     reflect the length of 'players' after the player has been removed.
    update_pipeline: list[dict[str, Any]] = [
        {
            "$set": {
                "players": {
                    # filters the name out of players and updates players.
                    "$filter": {
                        "input": "$players",
                        "as": "p",
                        "cond": {
                            "$ne": ["$$p", name]  # keep everyone except 'name'
                        }
                    }
                },
                # resetting benched/lucky/seventh player on update,
                # since an updated player list invalidates any previous rotation assignment.
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

    doc: dict[str, Any] | None = await user_sessions.find_one_and_update(
        filter_query,
        update_pipeline,
        return_document=ReturnDocument.AFTER
    )

    # doc could be None for multiple reasons
    #     - 1. username wasn't found
    #     - 2. player NOT registered under user
    #     - 3. user has the minimum number of players registered, and cannot remove more.
    if doc is None:
        existing_user_doc: dict[str, Any] | None = await user_sessions.find_one({"username": username})

        # 1. username wasn't found
        if existing_user_doc is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No user with username: '{username}' found. Please register."
            )

        # 2. player NOT registered under user
        if name not in existing_user_doc["players"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Player '{name}' not found registered under user."
            )

        # if neither 1 and 2, user has minimum players registered and no more players can be removed.
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot remove player. User has {existing_user_doc['no_of_players']} players registered. "
                   f"Number of players allowed per user: {MIN_PLAYER_COUNT} to {MAX_PLAYER_COUNT}. "
                   f"Please add another player first."
        )

    response = build_list_players_response(doc)

    return response


@user_router.patch(
    "/update_players",
    response_description="Updates (replaces) the entire list of registered players under user.",
    response_model=ListPlayersResponse,
    status_code=status.HTTP_200_OK
)
async def update_players(new_players: NewPlayersRequest, user_sessions: user_sessions_dependency) \
        -> ListPlayersResponse:
    """
        Updates (replaces) the entire list of registered players under user.

    :param new_players: Incoming request body containing the new list of players.
    :param user_sessions: Injected user_sessions collection dependency.
    :return: The updated players list for the user wrapped in ListPlayersResponse.
    :raises HTTPException 404: If no user record exists.
    """
    # TODO: hardcoded for now -- will come from the discord bot.
    username: str = FOUR_PLAYERS
    filter_query: dict[str, Any] = {
        "username": username
    }
    fields_to_update: dict[str, Any] = {
        "players": new_players.players,
        "no_of_players": len(new_players.players),
        # Resetting benched/lucky/seventh player on update,
        # since a new player list invalidates any previous rotation assignment.
        "benched_players": [],
        "lucky_players": [],
        "seventh_player": None
    }

    doc: dict[str, Any] | None = await user_sessions.find_one_and_update(
        filter_query,
        update={
            "$set": fields_to_update
        },
        return_document=ReturnDocument.AFTER,  # return document after update.
    )

    if doc is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No user with username: '{username}' found. Please register."
        )

    response = build_list_players_response(doc)

    return response


@user_router.delete(
    "/delete_user",
    response_model=DeleteUserResponse,
    response_description="Deletes the user.",
    status_code=status.HTTP_200_OK
)
async def delete_user(user_sessions: user_sessions_dependency) -> DeleteUserResponse:
    """
        Deletes the user.

    :param user_sessions: Injected user_sessions collection dependency.
    :return: A confirmation message with username being deleted wrapped in DeleteUserResponse.
    :raises HTTPException 404: If no user record exists.
    """
    # TODO: hardcoded for now -- will come from the discord bot.
    username: str = FOUR_PLAYERS
    filter_query: dict[str, Any] = {
        "username": username
    }

    # removes the first document matching the filter.
    result: DeleteResult = await user_sessions.delete_one(filter_query)

    if result.deleted_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"No user with '{username}' found.")

    response: DeleteUserResponse = DeleteUserResponse(
        message=f"User {username} has been deleted."
    )

    return response
