from typing import Annotated

from fastapi import APIRouter, Query
from pair_players import *

pair_router = APIRouter(
    prefix="/pair",
    tags=["pair"],
)


@pair_router.get("/")
async def read_pairs(
        player: Annotated[list[str],
        Query(
            title="Player's Name",
            description="Input the players' names that are to be paired."
        )]
):
    return pair_players(player)
