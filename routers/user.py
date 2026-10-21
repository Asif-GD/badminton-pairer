from typing import Final, Annotated, Any

from fastapi import APIRouter, HTTPException, Depends
from pymongo.asynchronous.collection import ReturnDocument
from pymongo.errors import DuplicateKeyError
from pymongo.results import DeleteResult
from starlette import status

from database.models import user_sessions_dependency
from database.req_res_models import ListPlayersResponse, NewPlayersRequest, MAX_PLAYER_COUNT, MIN_PLAYER_COUNT, \
    DeleteUserResponse
from session_utils import create_session_id
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
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(e)) from None


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
    response_description="The updated list of players registered under the user, after addition.",
    response_model=ListPlayersResponse,
    status_code=status.HTTP_200_OK,
    responses={
        400: {
            "description": (
                    "Player already registered under user, "
                    "or user has maximum number of players registered."
            )
        },
        404: {"description": "No user record exists."},
        409: {
            "description": (
                    "The user has the same set of players already registered under them, "
                    "or the players list changed between read and update (race condition)."
            )
        },
        422: {"description": "Player name fails validation."},
    }
)
async def add_player(
        name: name_validator_dependency,
        user_sessions: user_sessions_dependency,
) -> ListPlayersResponse:
    """
        Adds a player to the list of registered players under the user.\f

    :param name: Incoming path parameter that holds the player's name to be added.
    :param user_sessions: Injected user_sessions collections dependency.
    :return: The updated players list for the user wrapped in ListPlayersResponse.
    :raises HTTPException 400: If player already registered under user,
        or user has maximum number of players registered.
    :raises HTTPException 404: If no user record exists.
    :raises HTTPException 409: In case the user has the same set of players already registered under them,
        or if the players list changed between read and update (race condition)
    """
    # TODO: hardcoded for now -- will come from the discord bot.
    username: str = NINE_PLAYERS

    filter_query_for_find_one: dict[str, str] = {
        "username": username,
    }

    current_doc: dict[str, Any] | None = await user_sessions.find_one(
        filter=filter_query_for_find_one
    )

    # username wasn't found
    if current_doc is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No user with username: '{username}' found. Please register."
        )

    db_players: list[str] = current_doc["players"]
    db_no_of_players: int = current_doc["no_of_players"]

    # player already registered under user
    if name in db_players:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Player '{name}' already registered under this user. No duplicate entries allowed."
        )

    # user has maximum players registered already.
    # note: >= is not needed here, strictly speaking;
    #   because technically, the db_no_of_players can never exceed MAX_PLAYER_COUNT.
    #   Still, it's better to cover it here and this way, it's one less thing to error out.
    if db_no_of_players >= MAX_PLAYER_COUNT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot add new player. User has {db_no_of_players} players registered. "
                   f"Number of players allowed per user: {MIN_PLAYER_COUNT} to {MAX_PLAYER_COUNT}. "
                   f"Please remove another player first."
        )

    # this way db_players remains unchanged, and we need it to create a guard on update to ensure atomicity
    db_players_after_add: list[str] = db_players + [name]
    db_players_after_add.sort()  # better to store the players list in sorted order in db for uniformity

    updated_session_id: str = create_session_id(username=username, player_list=db_players_after_add)

    filter_query_for_find_one_and_update: dict[str, Any] = {
        "username": username,
        "players": {
            "$eq": db_players  # -> to ensure the value hasn't changed between read and update
        },
        # "players": db_players, # -> this works too
    }

    update_query: dict[str, Any] = {
        "$set": {
            "session_id": updated_session_id,
            "players": db_players_after_add,
            "no_of_players": len(db_players_after_add),
            # Resetting benched/lucky/seventh player on update,
            # since a new player list invalidates any previous rotation assignment.
            "benched_players": [],
            "lucky_players": [],
            "seventh_player": None
        }
    }

    try:
        updated_doc: dict[str, Any] | None = await user_sessions.find_one_and_update(
            filter=filter_query_for_find_one_and_update,
            update=update_query,
            return_document=ReturnDocument.AFTER
        )
    except DuplicateKeyError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You've already registered this exact set of players. "
                   "Use command '/list_players' to view your registered set of players. "
                   "Use command '/help' for more information."
        ) from None

    # the updated_doc could be None for multiple reasons
    #     - 1. username wasn't found
    #     - 2. players list has changed between read and update (race condition)
    if updated_doc is None:
        existing_user_doc: dict[str, Any] | None = await user_sessions.find_one({"username": username})
        # 1. username wasn't found
        if existing_user_doc is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No user with username: '{username}' found. Please register."
            )
        # 2. players list has changed between read and update (race condition)
        else:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User's list of players changed while updating. "
                       "Please use command '/list_players' to check for errors and try again."
            )

    response: ListPlayersResponse = build_list_players_response(updated_doc)

    return response


@user_router.patch(
    "/remove_player/{name}",
    response_description="The updated list of players registered under the user, after removal.",
    response_model=ListPlayersResponse,
    status_code=status.HTTP_200_OK,
    responses={
        400: {
            "description": (
                    "Player is not found registered under user, "
                    "or user is at minimum number of players registered."
            )
        },
        404: {"description": "No user record exists."},
        409: {
            "description": (
                    "The user has the same set of players already registered under them, "
                    "or the players list changed between read and update (race condition)."
            )
        },
        422: {"description": "Player name fails validation."},
    }
)
async def remove_player(
        name: name_validator_dependency,
        user_sessions: user_sessions_dependency,
) -> ListPlayersResponse:
    """
        Removes a player from the list of registered players under the user.\f

    :param name: Incoming path parameter that holds the player's name to be removed.
    :param user_sessions: Injected user_sessions collections dependency.
    :return: The updated players list for the user wrapped in ListPlayersResponse.
    :raises HTTPException 400: If player is not found registered under user,
        or user is at minimum number of players registered.
    :raises HTTPException 404: If no user record exists.
    :raises HTTPException 409: In case the user has the same set of players already registered under them,
        or if the players list changed between read and update (race condition)
    """
    # TODO: hardcoded for now -- will come from the discord bot.
    username: str = NINE_PLAYERS

    # filter_query -> find user session of 'username' where player == 'name'
    filter_query_find_one: dict[str, str] = {
        "username": username
    }

    current_doc: dict[str, Any] | None = await user_sessions.find_one(
        filter=filter_query_find_one
    )

    # a record under username wasn't found
    if current_doc is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No user with username: '{username}' found. Please register."
        )

    db_players: list[str] = current_doc["players"]
    db_no_of_players: int = current_doc["no_of_players"]

    # if the player is not found registered under user
    if name not in db_players:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Player '{name}' not found registered under this user. "
                   f"Please use command '/list_players' to check and try again."
        )

    # user has minimum players registered
    # note: <= is not needed here, strictly speaking;
    #   because technically, the db_no_of_players can never go below MIN_PLAYER_COUNT.
    #   Still, it's better to cover it here and this way, it's one less thing to error out.
    if db_no_of_players <= MIN_PLAYER_COUNT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot remove player. User has {db_no_of_players} players registered. "
                   f"Number of players allowed per user: {MIN_PLAYER_COUNT} to {MAX_PLAYER_COUNT}. "
                   f"Please add another player first."
        )

    # this way db_players remains unchanged, and we need it to create a guard on update to ensure atomicity
    db_players_after_remove: list[str] = [player for player in db_players if player != name]
    db_players_after_remove.sort()  # -> sort isn't necessary here unlike adding but doing so as a preventive measure.

    updated_session_id: str = create_session_id(username=username, player_list=db_players_after_remove)

    filter_query_for_find_one_and_update: dict[str, Any] = {
        "username": username,
        "players": {
            "$eq": db_players  # -> to ensure the value hasn't changed between read and update
        },
        # "players": db_players # -> this works too
    }

    update_query: dict[str, Any] = {
        "$set": {
            "session_id": updated_session_id,
            "no_of_players": len(db_players_after_remove),
            "players": db_players_after_remove,
            # resetting benched/lucky/seventh player on update,
            # since an updated player list invalidates any previous rotation assignment.
            "benched_players": [],
            "lucky_players": [],
            "seventh_player": None
        }
    }

    try:
        updated_doc: dict[str, Any] | None = await user_sessions.find_one_and_update(
            filter=filter_query_for_find_one_and_update,
            update=update_query,
            return_document=ReturnDocument.AFTER
        )
    except DuplicateKeyError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You've already registered this exact set of players. "
                   "Use command '/list_players' to view your registered set of players. "
                   "Use command '/help' for more information."
        ) from None

    # updated_doc could be None for multiple reasons because something changed in db between read and update (race)
    #     - 1. username wasn't found
    #     - 2. players list has changed
    if updated_doc is None:
        existing_user_doc: dict[str, Any] | None = await user_sessions.find_one({"username": username})

        # 1. username wasn't found
        if existing_user_doc is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No user with username: '{username}' found. Please register."
            )

        # 2. players list has changed
        else:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User's list of players changed while updating. "
                       "Please use command '/list_players' to check for errors and try again."
            )

    response: ListPlayersResponse = build_list_players_response(updated_doc)

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
