import logging
from collections.abc import Iterator
from typing import TypeVar

from .models import TournamentPlayer

T = TypeVar("T")
logger = logging.getLogger("othello")


def chunks(v: list[T], n: int) -> Iterator[tuple[T]]:
    for i in range(0, len(v), n):
        yield tuple(v[i : i + n])


def get_updated_ranking(player: TournamentPlayer) -> float:
    player.refresh_from_db()
    return player.ranking
