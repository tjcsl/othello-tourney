from typing import Any

from .models import Game, GameError, GameLog


def serialize_game_info(game: Game) -> dict[str, Any]:
    data = {
        "type": "game.update",
        "id": game.id,
        "game_over": not game.playing,
        "black": game.black.get_game_name(),
        "white": game.white.get_game_name(),
        "outcome": game.outcome,
        "forfeit": game.forfeit,
        "moves": None,
        "time_limit": game.time_limit,
        "runoff": game.runoff,
    }
    if moves := game.moves.order_by("-created_at"):
        data["moves"] = [
            {
                "id": move.id,
                "tile": move.move,
                "player": move.player.lower(),
                "board": move.board,
                "possible": move.possible,
            }
            for move in moves
        ]
    if not game.playing:
        data["moves"][0]["possible"] = []
    return data


def serialize_game_log(log: GameLog) -> dict[str, Any]:
    data = {"type": "game.log", "player": log.player.lower(), "message": log.message}
    return data


def serialize_game_error(error: GameError) -> dict[str, Any]:
    data = {
        "type": "game.error",
        "player": error.player.lower(),
        "code": error.error_code,
        "message": error.error_msg,
    }
    return data
