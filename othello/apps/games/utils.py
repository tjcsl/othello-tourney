import json


def serialize_game_info(game):
    data = {
        "id": game.id,
        "game_over": not game.playing,
        "black": game.black.get_user_name(),
        "white": game.white.get_user_name(),
        "board": game.board,
        "outcome": game.outcome,
        "forfeit": game.forfeit
    }
    if move := game.moves.latest():
        data['new_move'] = {
            "tile": move.move,
            "player": move.player,
            "flipped": move.flipped,
            "possible": move.possible,
        }
    else:
        data['new_move'] = None

    return data


def serialize_game_log(log):
    data = {
        "player": log.player,
        "message": log.message
    }
    return json.dumps(data)


def serialize_game_error(error):
    data = {
        "player": error.player,
        "code": error.error_code,
        "message": error.error_msg
    }
    return json.dumps(data)
