import logging
from typing import Iterable, Iterator, Tuple, TypeVar

from .models import TournamentPlayer

T = TypeVar("T")
logger = logging.getLogger("othello")


def chunks(v: Iterable[T], n: int) -> Iterator[Tuple[T, ...]]:
    # From https://stackoverflow.com/a/1625023
    return zip(*(iter(v),) * n)


def get_updated_ranking(player: TournamentPlayer) -> float:
    player.refresh_from_db()
    return player.ranking
