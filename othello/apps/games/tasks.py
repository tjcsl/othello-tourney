import os

from celery import shared_task
from django.conf import settings
from celery.utils.log import get_task_logger

from ..games.models import Game, Player
from ...moderator import Moderator, PlayerRunner, InvalidMoveError, ServerError, UserError

task_logger = get_task_logger(__name__)


def temp_error(err):
    task_logger.error(f"SERVER ERROR {err.value}")


@shared_task
def run_game(game_id):
    game = Game.objects.get(id=game_id)
    game.playing = True
    game.save(update_fields=['playing'])

    mod, time_limit = Moderator(), game.time_limit

    with PlayerRunner(game.black.code.path, settings.JAILEDRUNNER_DRIVER, settings.DEBUG) as player_black:
        with PlayerRunner(game.white.code.path, settings.JAILEDRUNNER_DRIVER, settings.DEBUG) as player_white:
            while not mod.is_game_over():
                board, current_player = mod.get_game_state()

                task_logger.error(f"GAME STATE: {board}, {current_player}")

                try:
                    if current_player == Player.BLACK:
                        running_turn = player_black.get_move(board, current_player.value, time_limit)
                    elif current_player == Player.WHITE:
                        running_turn = player_white.get_move(board, current_player.value, time_limit)
                except BaseException as e:
                    task_logger.error(str(e))

                for log in running_turn:
                    game.logs.create(
                        player=current_player.value,
                        message=log,
                    )
                submitted_move, error = running_turn.return_value

                task_logger.error(f"SUBMITTED {submitted_move}")

                if error != 0:
                    game.errors.create(
                        player=current_player.value,
                        error_code=error[0],
                        error_msg=error[1],
                    )
                    if isinstance(error, ServerError):
                        game.forfeit = False
                        game.outcome = 'T'
                    elif isinstance(error, UserError):
                        game.forfeit = True
                        game.outcome = Player.BLACK.value if current_player == Player.WHITE else Player.WHITE.value
                    game.playing = False
                    game.save(update_fields=["forfeit", "outcome", "playing"])
                    break

                try:
                    if submitted := mod.submit_move(submitted_move):
                        flipped, possible = submitted
                    else:
                        game.forfeit, game.playing = False, False
                        game.outcome = current_player.value
                        game.save(update_fields=["forfeit", "outcome", "playing"])
                        task_logger.error("GAME OVER")
                except InvalidMoveError as e:
                    task_logger.error(e)
                    game.forfeit, game.playing = True, False
                    game.outcome = Player.BLACK.value if current_player == Player.WHITE else Player.WHITE.value
                    game.save(update_fields=["forfeit", "outcome", "playing"])
                    break

                game.moves.create(
                    player=current_player.value,
                    board=board,
                    move=submitted_move,
                    flipped=flipped,
                    possible=possible
                )
