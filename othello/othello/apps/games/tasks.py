import os
import time
import shlex
import threading
import subprocess

from queue import Empty
from celery import shared_task
from django.conf import settings

from .utils import get_stream_queue
from ... import moderator, sandboxing
from ..games.models import Game, Move, Player, BlackGameLog, WhiteGameLog

JAILEDRUNNER_DRIVER = os.path.join(settings.BASE_DIR, "moderator", "wrapper.py")
OTHELLO_AI_RUN_COMMAND = f"python3 -u {JAILEDRUNNER_DRIVER} {'{path!r}'}"

GAME_STATE_INPUT = "{time_limit!r}\n{0}\n{1}\n"  # Don't use keywords after the first so we can just *Moderator.get_game_state()[1:]


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
                cwd=game.get_code_directory(Player.WHITE)
        )
    black = subprocess.Popen(
                black_cmd_args,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                bufsize=1,
                cwd=game.get_code_directory(Player.BLACK)
        )
    stop_event = threading.Event()

    players = {
        0: {"proc": white, "stdout": get_stream_queue(white.stdout, stop_event), "stderr": get_stream_queue(white.stderr, stop_event)},
        1: {"proc": black, "stdout": get_stream_queue(black.stdout, stop_event), "stderr": get_stream_queue(black.stderr, stop_event)},
    }

    while not mod.is_game_over:
        data, current_player = GAME_STATE_INPUT.format(time_limit=time_limit, *mod.get_game_state()).encode('ascii'), players[mod.current_player]
        logger, error_logger = (game.white_logs, game.white_errors) if mod.current_player == 0 else (game.black_logs, game.black_errors)

        current_player["proc"].stdin.write(data)
        move, errors = -1, ""

        try:
            move = moderator.utils.safe_int(current_player["stdout"].get(timeout=time_limit+5))
        except Empty:
            move = -1

        errors = check_for_errors(current_player["stderr"])

        logger.create(game=game, log=errors)

        try:
            game_over = mod.submit_move(move)
        except moderator.InvalidMoveError as e:
            error_logger.create(game=game, error_code=-1, message=str(e))




