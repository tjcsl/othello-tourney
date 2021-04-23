import logging
import random
from typing import Generator, List, Tuple, TypeVar

from .models import TournamentPlayer

T = TypeVar("T")
logger = logging.getLogger("othello")


def chunks(v: List[T], n: int) -> Generator[List[T], None, None]:
    for i in range(0, len(v), n):
        yield v[i: i + n]


def get_updated_ranking(player: TournamentPlayer) -> float:
    player.refresh_from_db()
    return player.ranking


def make_pairings(players: List[TournamentPlayer], bye_player: TournamentPlayer) -> List[Tuple[TournamentPlayer, TournamentPlayer]]:
    matches = []
    players = sorted(players, key=get_updated_ranking)

    for i in range(0, len(players), 2):
        if i + 1 >= len(players):
            players.append(bye_player)
        logger.info(f"RANK: {players[i]}({players[i].ranking}), {players[i+1]}({players[i+1].ranking})")
        black = random.choice((players[i], players[i + 1]))
        white = players[i] if black == players[i + 1] else players[i + 1]
        matches.append((black, white))

    return matches
