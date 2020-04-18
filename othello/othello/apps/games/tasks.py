import os
import shlex
import subprocess

from celery import shared_task
from django.conf import settings

from ... import moderator, sandboxing
from ..games.models import Game, Move, Player, BlackGameLog, WhiteGameLog

JAILEDRUNNER_DRIVER = os.path.join(settings.BASE_DIR, "moderator", "wrapper.py")
OTHELLO_AI_RUN_COMMAND = f"python3 -u {JAILEDRUNNER_DRIVER} {'{path!}'}"

GAME_STATE_INPUT = "{time_limit!r}\n{0}\n{1}\n"  # Don't use keywords after the first so we can just *Moderator.get_game_state()[1:]


@shared_task
def run_game(game_id):
    game = Game.objects.safe_get(id=game_id)

    retcode = None

    output, errors = "", ""

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

    black_proc = subprocess.Popen(
        black_cmd_args,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        bufsize=1,
        cwd=game.get_code_filepath(Player.BLACK)
    )

    white_proc = subprocess.Popen(
        white_cmd_args,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        bufsize=1,
        cwd=game.get_code_filepath(Player.WHITE)
    )
