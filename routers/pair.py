from typing import Final, Any

from fastapi import APIRouter, HTTPException
from pymongo.errors import DuplicateKeyError
from starlette import status

from database.models import UserSession, user_sessions_dependency
from database.req_res_models import NewPlayersResponse, NewPlayersRequest, PairingsResponse, \
    PairingsWithBenchedPlayerResponse, SplitPlayersRequest, SplitPlayersResponse
from pair_players import *

pair_router = APIRouter(
    prefix="/pair",
    tags=["pair"],
)

# test accounts -> placeholders
FOUR_PLAYERS: Final[str] = "place_holder_4"
FIVE_PLAYERS: Final[str] = "place_holder_5"
SIX_PLAYERS: Final[str] = "place_holder_6"
SEVEN_PLAYERS: Final[str] = "place_holder_7"
EIGHT_PLAYERS: Final[str] = "place_holder_8"
NINE_PLAYERS: Final[str] = "place_holder_9"
TEN_PLAYERS: Final[str] = "place_holder_10"
ELEVEN_PLAYERS: Final[str] = "place_holder_11"
TWELVE_PLAYERS: Final[str] = "place_holder_12"


def create_session_id(username: str, player_list: list[str]) -> str:
    """
        Creates a session_id to be stored as part of the user record in the db.
        IMPLEMENTATION:
            - combines the username, and the first 3 characters of all players
                from the user's list of registered players.
            - a session_id is unique, so the player_list is always sorted to prevent duplicates.

    :param username: The username of the user registering retrieved using the discord bot.
    :param player_list: The list of players being registered under user.
    :return: A string of size N.
    """
    session_id: str = username
    # sorted independently of the caller,
    # so session_id stays correct even if a future caller passes an unsorted list.
    sorted_player_list: list[str] = sorted(player_list)

    for player in sorted_player_list:
        session_id += player[:3]

    return session_id


@pair_router.post(
    "/register",
    response_model=NewPlayersResponse,
    response_description="Create a new user record and registers the players under the user.",
    status_code=status.HTTP_201_CREATED
)
async def register_players(new_players: NewPlayersRequest,
                           user_sessions: user_sessions_dependency) -> NewPlayersResponse:
    """
        Creates a new user record with the list of players under the user in the 'user_sessions' Collection.

    :param new_players: Incoming request body containing the new list of players.
    :param user_sessions: Injected user_sessions collection dependency.
    :return: A response model of type NewPlayersResponse containing the '_id' from the db, the list of players,
        and a status message 'Players registered successfully.'.
    :raises HTTPException 409: In case the user has the same set of players already registered under them.
    """
    # TODO: hardcoded for now -- will come from the discord bot.
    username: str = f"place_holder_{len(new_players.players)}"
    sorted_player_list: list[str] = sorted(new_players.players)

    session_id: str = create_session_id(username=username, player_list=sorted_player_list)

    new_user_session: UserSession = UserSession(
        username=username,
        session_id=session_id,
        no_of_players=len(new_players.players),
        players=sorted_player_list,
    )

    # we insert only when the user hasn't already registered the same set of players.
    try:
        # model_dump() converts the Pydantic model instance to a plain dict
        # insert_one() requires a dict/Mapping, not a model instance
        result = await user_sessions.insert_one(
            new_user_session.model_dump(by_alias=True, exclude={"id"})
        )
    except DuplicateKeyError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You've already registered this exact set of players. "
                   "Use command '/list_players' to view your registered set of players. "
                   "Use command '/help' for more information."
        )

    registered_players: str = ", ".join(new_players.players)  # -> converts list[str] to str

    response: NewPlayersResponse = NewPlayersResponse(
        id=str(result.inserted_id),
        players=registered_players,
        status="Players registered successfully."
    )

    return response


@pair_router.patch(
    "/shuffle",
    response_description="Shuffles players and pairs them.",
    status_code=status.HTTP_200_OK
)
async def shuffle_players(user_sessions: user_sessions_dependency) \
        -> PairingsResponse | PairingsWithBenchedPlayerResponse:
    """
        Shuffles players and pairs them into teams and returns it to user.

    :param user_sessions: Injected user_sessions collection dependency.
    :return: The players paired into teams in a PairingsResponse or PairingsWithBenchedPlayerResponse model.
    :raises HTTPException 404: If user has no registered players under them.
    :raises HTTPException 500: If the stored player count is outside the supported range (data-integrity issue).
    """
    # TODO: hardcoded for now -- will come from the discord bot.
    username = FIVE_PLAYERS
    filter_query = {
        "username": username
    }
    # fields to include, '_id' is always included by default (can't combine include & exclude, except for '_id')
    projection = {
        "no_of_players": 1,
        "players": 1,
        "benched_players": 1,
        "lucky_players": 1,
        "seventh_player": 1,
        "_id": 0
    }

    # find_one() because user will have at most one session (for now)

    # doc : {
    #     "no_of_players" : int,
    #     "players" : list[str],
    #     "benched_players": list[str],
    #     "lucky_players": list[str],
    #     "seventh_player": str
    # }

    doc: dict[str, Any] | None = await user_sessions.find_one(filter_query, projection)

    if doc is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No session found for user '{username}'. Please register."
        )

    db_player_count = doc["no_of_players"]
    db_players = doc["players"]
    db_benched_players = doc["benched_players"]
    db_lucky_players = doc["lucky_players"]
    db_seventh_player = doc["seventh_player"]

    if db_player_count in {4, 6, 8}:
        return await handle_4_6_or_8_player_pairings(players=db_players)
    elif db_player_count in {5, 9, 10, 11}:
        return await handle_5_9_10_or_11_player_pairings(players=db_players, benched_players=db_benched_players,
                                                         user_sessions=user_sessions)
    elif db_player_count == 7:
        return await handle_7_player_pairings(players=db_players, lucky_players=db_lucky_players,
                                              seventh_player=db_seventh_player, user_sessions=user_sessions)
    elif db_player_count == 12:
        return await handle_12_player_pairings(players=db_players)
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to process this request. Please try again. "
                   "Use command '/help' for more information."
        )


async def handle_4_6_or_8_player_pairings(players: list[str]) -> PairingsResponse:
    """
        Wraps the pair_4_6_8_players() into the PairingsResponse model.
    :param players:
    :return:
    """
    pairings = pair_4_6_or_8_players(player_list=players)

    response = PairingsResponse(
        teams=pairings
    )

    return response


async def handle_5_9_10_or_11_player_pairings(players: list[str], benched_players: list[str],
                                              user_sessions: user_sessions_dependency) \
        -> PairingsWithBenchedPlayerResponse:
    """
        Wraps the handle_5_9_10_or_11_player_pairings() into the PairingsWithBenchedPlayerResponse model. Also updates db.
    :param user_sessions:
    :param benched_players:
    :param players:
    :return:
    """

    pairings, benched_players = pair_5_9_10_or_11_players(player_list=players, benched_player_list=benched_players)

    # TODO: hardcoded for now -- will come from the discord bot.
    username = FIVE_PLAYERS
    filter_query = {
        "username": username
    }
    fields_to_update = {
        "benched_players": benched_players
    }

    # update_one() because a user can have at most one registered set of players i.e. one record of players.
    result = await user_sessions.update_one(
        filter_query,
        update={
            "$set": fields_to_update
        },
    )

    # we only return the players benched this turn and not the entire list
    no_of_players_to_be_benched = len(players) % 4
    benched_players = benched_players[- no_of_players_to_be_benched:]
    players_display: str = ", ".join(benched_players)  # converts the list[str] to str

    response = PairingsWithBenchedPlayerResponse(
        teams=pairings,
        benched_player=players_display
    )

    return response


async def handle_7_player_pairings(players: list[str], lucky_players: list[str], seventh_player: str,
                                   user_sessions: user_sessions_dependency) -> PairingsResponse:
    """
        Wraps the pair_7_players() into the PairingsResponse model. Also updates db.
    :param user_sessions:
    :param players:
    :param lucky_players:
    :param seventh_player:
    :return:
    """

    pairings, lucky_players, seventh_player = pair_7_players(player_list=players, lucky_player_list=lucky_players,
                                                             seventh_player=seventh_player)

    # TODO: hardcoded for now -- will come from the discord bot.
    username = SEVEN_PLAYERS
    filter_query = {
        "username": username
    }
    fields_to_update = {
        "lucky_players": lucky_players,
        "seventh_player": seventh_player
    }

    # update_one() because a user can have at most one registered set of players i.e. one record of players.
    result = await user_sessions.update_one(
        filter_query,
        update={
            "$set": fields_to_update
        },
    )

    response = PairingsResponse(
        teams=pairings
    )

    return response


async def handle_12_player_pairings(players: list[str]) -> PairingsResponse:
    """
        Wraps the pair_12_players() into the PairingsResponse model.
    :param players:
    :return:
    """
    pairings = pair_12_players(player_list=players)

    response = PairingsResponse(
        teams=pairings
    )

    return response


@pair_router.post(
    "/split",
    response_description="Split the players in pairs of two given by the user, randomly.",
    status_code=status.HTTP_200_OK
)
async def split_players(players: SplitPlayersRequest) -> SplitPlayersResponse:
    """
        Split the players in pairs of two given by the user, randomly.
    :param players:
    :return: The pairings of players and unpaired player if any.
    """

    pairings, unpaired_player = split(player_list=players.players)

    response: SplitPlayersResponse = SplitPlayersResponse(
        no_of_players=len(players.players),
        teams=pairings,
        unpaired_player=unpaired_player
    )

    return response
