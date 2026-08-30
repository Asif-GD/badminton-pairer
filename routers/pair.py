from typing import Final

from fastapi import APIRouter, HTTPException
from starlette import status

from database.database import db_dependency
from database.models import UserSession
from database.req_res_models import RegisterPlayersRequest, PairingsResponse, PairingsWithBenchedPlayerResponse
from pair_players import *

pair_router = APIRouter(
    prefix="/pair",
    tags=["pair"],
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


def create_session_id(username: str, player_list: list[str]) -> str:
    session_id: str = username
    player_list.sort()
    for player in player_list:
        for index in range(0, 3):
            session_id += player[index]

    return session_id


@pair_router.post(
    "/register",
    response_description="Register players",
    status_code=status.HTTP_201_CREATED
)
async def register_players(players_list_request: RegisterPlayersRequest, db: db_dependency):
    """
        Creates a record of the players under the user in the UserSession Collection.
    :param players_list_request:
    :param db:
    :return:
    """

    user_session_collection = db.get_collection("user_sessions")

    session_id = create_session_id(username="place_holder", player_list=players_list_request.players)

    new_user_session = UserSession(
        username=f"place_holder_{len(players_list_request.players)}",  # -> discord username goes here
        session_id=session_id,
        no_of_players=len(players_list_request.players),
        players=players_list_request.players,
    )

    # model_dump() converts the Pydantic model instance to a plain dict
    # insert_one() requires a dict/Mapping, not a model instance
    result = await user_session_collection.insert_one(
        new_user_session.model_dump(by_alias=True, exclude={"id"})
    )

    return {
        "_id": str(result.inserted_id),
        "status": "Players registered successfully.",
        "Players": players_list_request.players,
    }


@pair_router.patch(
    "/shuffle",
    response_description="Shuffles players and pairs them.",
    status_code=status.HTTP_200_OK
)
async def shuffle_players(db: db_dependency):
    """
        Shuffles players and pairs them into teams and returns it to user.
    :param db:
    :return:
    """

    user_session_collection = db.get_collection("user_sessions")

    # I plan to retrieve the player list using the username which we would get via the Discord bot.
    # for now, a user can have at most one registered set of players i.e. one record of players.
    discord_username = TWELVE_PLAYERS
    filter_query = {
        "username": discord_username
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

    # find_one() because user will have at most one session
    """
        doc : {
            "no_of_player" : int,
            "players" : list[str],
            "benched_players": list[str],
            "lucky_players": list[str],
            "seventh_player": str
        }
    """
    doc = await user_session_collection.find_one(filter_query, projection)

    if doc is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No session found for user '{discord_username}'"
        )

    db_player_count = doc["no_of_players"]
    db_players = doc["players"]
    db_benched_players = doc["benched_players"]
    db_lucky_players = doc["lucky_players"]
    db_seventh_player = doc["seventh_player"]

    if db_player_count == 4 or db_player_count == 6 or db_player_count == 8:
        return await handle_4_6_or_8_player_pairings(players=db_players)
    elif db_player_count == 5 or db_player_count == 9 or db_player_count == 10 or db_player_count == 11:
        return await handle_5_9_10_or_11_player_pairings(players=db_players, benched_players=db_benched_players,
                                                         db=db)
    elif db_player_count == 7:
        return await handle_7_player_pairings(players=db_players, lucky_players=db_lucky_players,
                                              seventh_player=db_seventh_player, db=db)
    elif db_player_count == 12:
        return await handle_12_player_pairings(players=db_players)
    else:
        return "I am unable to comply with this request. Too many players!"


async def handle_4_6_or_8_player_pairings(players: list[str]) -> PairingsResponse:
    """
        Wraps the pair_4_6_8_12_players() into the PairingsResponse model.
    :param players:
    :return:
    """
    pairings = pair_4_6_or_8_players(player_list=players)
    return PairingsResponse(teams=pairings)


async def handle_5_9_10_or_11_player_pairings(players: list[str], benched_players: list[str],
                                              db: db_dependency) -> PairingsWithBenchedPlayerResponse:
    """
        Wraps the handle_5_9_10_or_11_player_pairings() into the PairingsWithBenchedPlayerResponse model. Also updates db.
    :param db:
    :param benched_players:
    :param players:
    :return:
    """

    pairings, benched_players = pair_5_9_10_or_11_players(player_list=players, benched_player_list=benched_players)

    user_session_collection = db.get_collection("user_sessions")

    # I plan to retrieve the player list using the username which we would get via the Discord bot.
    # for now, a user can have at most one registered set of players i.e. one record of players.
    discord_username = ELEVEN_PLAYERS
    filter_query = {
        "username": discord_username
    }

    fields_to_update = {
        "benched_players": benched_players
    }

    # update_one() because a user can have at most one registered set of players i.e. one record of players.
    result = await user_session_collection.update_one(
        filter_query,
        update={
            "$set": fields_to_update
        },
    )

    # we only return the players benched this turn and not the entire list
    no_of_players_to_be_benched = len(players) % 4
    benched_players = benched_players[- no_of_players_to_be_benched:]
    benched_players: str = ", ".join(benched_players)  # converts the list[str] to str

    return PairingsWithBenchedPlayerResponse(teams=pairings, benched_player=benched_players)


async def handle_7_player_pairings(players: list[str], lucky_players: list[str], seventh_player: str,
                                   db: db_dependency) -> PairingsResponse:
    """
        Wraps the pair_7_players() into the PairingsResponse model. Also updates db.
    :param players:
    :param lucky_players:
    :param seventh_player:
    :param db:
    :return:
    """

    pairings, lucky_players, seventh_player = pair_7_players(player_list=players, lucky_player_list=lucky_players,
                                                             seventh_player=seventh_player)

    user_session_collection = db.get_collection("user_sessions")

    # I plan to retrieve the player list using the username which we would get via the Discord bot.
    # for now, a user can have at most one registered set of players i.e. one record of players.
    discord_username = SEVEN_PLAYERS
    filter_query = {
        "username": discord_username
    }

    fields_to_update = {
        "lucky_players": lucky_players,
        "seventh_player": seventh_player
    }

    # update_one() because a user can have at most one registered set of players i.e. one record of players.
    result = await user_session_collection.update_one(
        filter_query,
        update={
            "$set": fields_to_update
        },
    )

    return PairingsResponse(teams=pairings)


async def handle_12_player_pairings(players: list[str]) -> PairingsResponse:
    """
        Wraps the pair_12_players() into the PairingsResponse model.
    :param players:
    :return:
    """
    pairings = pair_12_players(player_list=players)
    return PairingsResponse(teams=pairings)
