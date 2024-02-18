import random
from typing import List, Tuple

from othello.apps.tournaments.models import TournamentPlayer
from othello.apps.tournaments.utils import get_updated_ranking, logger, chunks

Players = List[TournamentPlayer]
Pairings = List[Tuple[TournamentPlayer, ...]]


def random_pairing(players: Players, bye_player: TournamentPlayer) -> Pairings:
    randomized: Players = random.sample(players, len(players))
    if len(randomized) % 2 == 1:
        randomized.append(bye_player)

    return list(chunks(randomized, 2))


def swiss_pairing(players: Players, bye_player: TournamentPlayer) -> Pairings:
    tournament = players[0].tournament

    # Default to danish pairing if there are enough rounds
    if tournament.num_rounds >= len(players) - 1:
        return danish_pairing(players, bye_player)

    matches: Pairings = []
    players = sorted(players, key=get_updated_ranking, reverse=True)
    if len(players) % 2 == 1:
        players.append(bye_player)

    logger.info(players)

    tournament_matches = set()
    for game in tournament.games.all():
        tournament_matches.add((game.black.id, game.white.id))
        tournament_matches.add((game.white.id, game.black.id))

    for i in range(0, len(players)):
        if i + 1 >= len(players):
            break
        for j in range(i + 1, len(players)):
            if (players[i].id, players[j].id) not in tournament_matches:
                black = random.choice((players[i], players[j]))
                white = players[i] if black == players[j] else players[j]
                logger.info(f"RANK: {black}({black.ranking}), {white}({white.ranking})")
                matches.append((black, white))
                break
        else:
            return danish_pairing(players, bye_player)

    return matches


def danish_pairing(players: Players, bye_player: TournamentPlayer) -> Pairings:
    matches = []
    players = sorted(players, key=get_updated_ranking, reverse=True)

    for i in range(0, len(players), 2):
        if i + 1 >= len(players):
            players.append(bye_player)
        black = random.choice((players[i], players[i + 1]))
        white = players[i] if black == players[i + 1] else players[i + 1]
        logger.info(f"RANK: {black}({black.ranking}), {white}({white.ranking})")
        matches.append((black, white))

    return matches


algorithms = {
    "random": random_pairing,
    "swiss": swiss_pairing,
    "danish": danish_pairing,
}


def pair(players: Players, bye_player: TournamentPlayer, algorithm: str = "swiss") -> Pairings:
    if algorithm not in algorithms:
        raise ValueError(f"Invalid pairing algorithm: {algorithm}")
    return algorithms[algorithm](players, bye_player)
