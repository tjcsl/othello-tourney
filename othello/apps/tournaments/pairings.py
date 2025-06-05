import random
from typing import List, Tuple

from othello.apps.tournaments.models import TournamentPlayer
from othello.apps.tournaments.utils import chunks, get_updated_ranking, logger

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

    played_games = set(game for tgame in tournament.games.all() if bye_player.submission.id not in (game := (tgame.game.black.id, tgame.game.white.id)))
    players_this_round = set()

    for i in range(0, len(players)):
        if players[i] in players_this_round:
            continue
        if i + 1 >= len(players):
            break
        for j in range(i + 1, len(players)):
            if players[j] not in players_this_round and (players[i].submission.id, players[j].submission.id) not in played_games:
                matches.append((players[i], players[j]))
                matches.append((players[j], players[i]))
                if players[i] != bye_player:
                    players_this_round.add(players[i])
                if players[j] != bye_player:
                    players_this_round.add(players[j])
                break
        else:
            # matches.append((players[i], bye_player))
            # matches.append((bye_player, players[i]))
            return danish_pairing(players, bye_player)

    return matches


def danish_pairing(players: Players, bye_player: TournamentPlayer) -> Pairings:
    logger.warning("Using Danish Pairing")
    matches = []
    players = sorted(players, key=get_updated_ranking, reverse=True)

    for i in range(0, len(players), 2):
        if i + 1 >= len(players):
            players.append(bye_player)
        # black = random.choice((players[i], players[i + 1]))
        # white = players[i] if black == players[i + 1] else players[i + 1]
        matches.append((players[i], players[i+1]))
        matches.append((players[i+1], players[i]))

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
