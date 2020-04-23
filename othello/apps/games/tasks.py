import os

from celery import shared_task
from django.conf import settings
from celery.utils.log import get_task_logger

from ..games.models import Game, Player
from ...moderator import Moderator, PlayerRunner, InvalidMoveError

task_logger = get_task_logger(__name__)


def temp_error(err):
    task_logger.error(f"SERVER ERROR {err.value}")


@shared_task
def run_game(game_id):
    game = Game.objects.get(id=game_id)
    game.playing = True
    game.save(update_fields=['playing'])

    mod, time_limit = Moderator(), game.time_limit

    with PlayerRunner(game.black.code.path, settings) as player_black:
        with PlayerRunner(game.white.code.path, settings) as player_white:
            while not mod.is_game_over:
                board, current_player = mod.get_game_state()

                try:
                    if current_player == Player.BLACK:
                        running_turn = player_black.get_move(board, current_player.value, time_limit)
                    elif current_player == Player.WHITE:
                        running_turn = player_white.get_move(board, current_player.value, time_limit)
                except BaseException as e:
                    task_logger.error(str(e))

                task_logger.error(running_turn)
                for log in running_turn:
                    task_logger.error(f"LOGGGG : {log}")
                submitted_move, error = running_turn.return_value

                task_logger.error(f"SUBMITTED {submitted_move}")

                if error != 0:
                    temp_error(error)
                    break

                try:
                    mod.submit_move(submitted_move)
                except InvalidMoveError as e:
                    task_logger.error(e)
                    break
