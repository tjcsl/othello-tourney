import logging
from typing import Iterator, List, TypeVar

from .models import TournamentPlayer

T = TypeVar("T")
logger = logging.getLogger("othello")


def chunks(v: List[T], n: int) -> Iterator[List[T]]:
    for i in range(0, len(v), n):
        yield v[i: i + n]


def get_updated_ranking(player: TournamentPlayer) -> float:
    player.refresh_from_db()
    return player.ranking
