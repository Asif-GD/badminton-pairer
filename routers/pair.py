from fastapi import APIRouter
from starlette import status

from database.database import db_dependency
from database.models import UserSession
from database.req_res_models import RegisterPlayersRequest

pair_router = APIRouter(
    prefix="/pair",
    tags=["pair"],
)


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
        username="place_holder",
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
