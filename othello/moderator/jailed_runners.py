# This file CANNOT import any file other than utils.py and constants.py
# This file is run in a sandboxed subprocess and is detached from the main application
# This file cannot access Django. its only I/O is through stdout/stderr
# Be careful when adding imports, because the file you are importing may import other files that import/reference
# unreachable modules themselves.
# ex. import xxx; [IN xxx.py]: import yyy; [IN yyy.py]: from django.conf import settings  => WILL BREAK
import sys
import traceback
import multiprocessing as mp
from contextlib import redirect_stdout
from typing import Any, TextIO, Union

from .utils import ServerError, import_strategy


class LocalRunner:  # Called from JailedRunner, inherits accessibility restrictions
    def __init__(self, script_path: str) -> None:
        self.path = script_path
        self.strat, self.nargs = import_strategy(script_path)
        self.logging = getattr(self.strat, "logging", False)

    def play_wrapper(self, *game_args: Any, pipe_to_parent: mp.Pipe) -> None:
        try:
            self.strat.best_strategy(*game_args)
            pipe_to_parent.send(None)
        except TypeError:
            print(
                "invalid submission"
            )  # printing to stdout from within LocalRunner will automatically give a READ_INVALID error
        except Exception:  # noqa
            pipe_to_parent.send(traceback.format_exc())

    def get_move(self, board: str, player: str, time_limit: int) -> Union[int, str]:
        best_move, is_running = mp.Value("i", -1), mp.Value("i", 1)

        to_child, to_self = mp.Pipe()
        try:
            args = (
                ("".join(board), player, best_move, is_running)
                if self.nargs == 4
                else ("".join(board), player, best_move, is_running, time_limit)
            )
            p = mp.Process(
                target=self.play_wrapper,
                args=args,
                kwargs={"pipe_to_parent": to_child},
                daemon=True,
            )
            p.start()
            p.join(time_limit)
            if p.is_alive():
                is_running.value = 0
                p.join(0.05)
                if p.is_alive():
                    p.terminate()
            return best_move.value, to_self.recv() if to_self.poll() else None
        except mp.ProcessError:
            traceback.print_exc()
            return ServerError.UNEXPECTED, "Server Error"


class JailedRunner(
    LocalRunner
):  # Called from subprocess, no access to django channels/main application
    def run(self):
        while True:
            self.handle(sys.stdin, sys.stdout, sys.stderr)

    def handle(self, stdin: TextIO, stdout: TextIO, stderr: TextIO) -> None:
        time_limit = int(stdin.readline().strip())
        player = stdin.readline().strip()
        board = stdin.readline().strip()

        with redirect_stdout(sys.stderr if self.logging else None):
            move, err = self.get_move(board, player, time_limit)

        if err is not None:
            stderr.write(f"SERVER: {err}\n")

        stdout.write(f"{move}\n")

        stdout.flush()
        stderr.flush()
