import os
import shlex
import threading
import subprocess

from queue import Empty
from celery import shared_task
from django.conf import settings
from celery.utils.log import get_task_logger

from .utils import get_stream_queue
from ... import moderator, sandboxing
from ..games.models import Game, Player

JAILEDRUNNER_DRIVER = os.path.join(settings.BASE_DIR, "moderator", "wrapper.py")
OTHELLO_AI_RUN_COMMAND = f"python3 -u {JAILEDRUNNER_DRIVER} {'{path!r}'}"

GAME_STATE_INPUT = "{time_limit!r}\n{board!r}\n{player!r}\n"

task_logger = get_task_logger(__name__)


def check_for_errors(error_queue):
    last_err_line, errs = "", []
    while last_err_line is not None:
        errs.append(last_err_line)
        try:
            last_err_line = error_queue.get_nowait()
        except:
            last_err_line = None
    return ''.join(errs)


@shared_task
def run_game(game_id):
    game = Game.objects.get(id=game_id)
    time_limit = game.time_limit

    black_cmd_args = sandboxing.get_sandbox_args(
        shlex.split(OTHELLO_AI_RUN_COMMAND.format(
            path=game.get_code_filepath(Player.BLACK)
        ))
    )

    white_cmd_args = sandboxing.get_sandbox_args(
        shlex.split(OTHELLO_AI_RUN_COMMAND.format(
            path=game.get_code_filepath(Player.WHITE)
        ))
    )

    mod = moderator.Moderator()

    white = subprocess.Popen(
                white_cmd_args,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                bufsize=1,
                universal_newlines=True,
                cwd=settings.BASE_DIR
        )
    black = subprocess.Popen(
                black_cmd_args,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                bufsize=1,
                universal_newlines=True,
                cwd=settings.BASE_DIR
        )
    stop_event = threading.Event()

    players = {
        Player.WHITE: {"proc": white, "stderr": get_stream_queue(white.stderr, stop_event)},
        Player.BLACK: {"proc": black, "stderr": get_stream_queue(black.stderr, stop_event)},
    }

    forfeit = False

    while not mod.is_game_over:
        board, player, possible = mod.get_game_state()

        task_logger.error(f"STATE: {player}, {board}")

        data, current_player = GAME_STATE_INPUT.format(time_limit=time_limit, board=board, player=player), players[player]
        logger, error_logger = (game.white_logs, game.white_errors) if player == Player.WHITE else (game.black_logs, game.black_errors)

        task_logger.error("STARTING TO WRITE")
        current_player["proc"].stdin.write(data)
        current_player["proc"].stdin.flush()
        task_logger.error("FINISHED WRITING")

        task_logger.error(f"ERRORS 1: {current_player['proc'].stderr.readline()}")
        task_logger.error(f"ERRORS 2: {current_player['proc'].stderr.readline()}")
        move = int(current_player["proc"].stdout.readline())


        # try:
        #     move = int(current_player["proc"].stdout.readline().decode())
        # except Empty:
        #     task_logger.error("error reading from stdin")
        #     move = -1
        # except ValueError:
        #     move = -1

        task_logger.error(f"GOT MOVE: {move}")

        # errors = check_for_errors(current_player["stderr"])
        #
        # task_logger.error(f"RECEIVED LOGS: {errors}")
        #
        # logger.create(game=game, log=errors)

        try:
            game_over = mod.submit_move(move)
        except moderator.InvalidMoveError as e:
            error_logger.create(game=game, error_code=-1, message=str(e))
            forfeit, game_over = True, True
            task_logger.error(f"INVALID MOVE: {str(e)}")

        if game_over:
            game.playing = False
            if forfeit:
                pass  # TODO: FILL THIS
            game.save(update_fields=['playing'])
            break

        task_logger.error("FINISHED ROUND, MOVING ON...")
        game.moves.create(
            player=player.value,
            board=board,
            move=move,
            possible=possible,
        )

