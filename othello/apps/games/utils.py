def serialize_game_info(game):
    data = {
        "type": "game.update",
        "id": game.id,
        "game_over": not game.playing,
        "black": game.black.get_game_name(),
        "white": game.white.get_game_name(),
        "outcome": game.outcome,
        "forfeit": game.forfeit,
        "moves": None,
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
        data["moves"][0]["possible"] = data["moves"][0]["flipped"] = []
    return data


def serialize_game_log(log):
    data = {"type": "game.log", "player": log.player.lower(), "message": log.message}
    return data


def serialize_game_error(error):
    data = {
        "type": "game.error",
        "player": error.player.lower(),
        "code": error.error_code,
        "message": error.error_msg,
    }
    return data
