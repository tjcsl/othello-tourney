# This file CANNOT import any file other than utils.py and constants.py
# This file is run in a sandboxed subprocess and is detached from the main application
# This file cannot access Django. its only I/O is through stdout/stderr
# Be careful when adding imports, because the file you are importing may import other files that import/reference
# unreachable modules themselves.
# ex. import xxx; [IN xxx.py]: import yyy; [IN yyy.py]: from django.conf import settings  => WILL BREAK
import multiprocessing as mp
import sys
import traceback
from contextlib import redirect_stdout
from time import perf_counter
from typing import Any, TextIO, Tuple, Union

from .utils import ServerError, import_strategy

MOVES_10x10 = {(i + 11 + 2 * (i // 8)): i for i in range(64)}


class LocalRunner:  # Called from JailedRunner, inherits accessibility restrictions
    def __init__(self, script_path: str) -> None:
        self.path = script_path
        self.strat, self.nargs = import_strategy(script_path)
        self.logging = getattr(self.strat, "logging", False)
        self.board_10x10 = getattr(self.strat, "use_10x10_board", False)
        self.moves_10x10 = getattr(self.strat, "use_10x10_moves", False)

    def play_wrapper(self, *game_args: Any, pipe_to_parent: mp.Pipe) -> None:
        try:
            self.strat.best_strategy(*game_args)
            pipe_to_parent.send(None)
        except Exception:  # noqa
            pipe_to_parent.send(traceback.format_exc())

    def get_move(self, board: str, player: str, time_limit: int) -> Union[Tuple[int, str, int], Tuple[ServerError, str, int]]:
        best_move, is_running = mp.Value("i", -1), mp.Value("i", 1)

        to_child, to_self = mp.Pipe()
        try:
            board = "".join(board)
            if self.board_10x10:
                board = "?" * 11 + "??".join(board[i : i + 8] for i in range(0, 64, 8)) + "?" * 11
            args = (board, player, best_move, is_running) if self.nargs == 4 else (board, player, best_move, is_running, time_limit)
            p = mp.Process(
                target=self.play_wrapper,
                args=args,
                kwargs={"pipe_to_parent": to_child},
                daemon=True,
            )
            p.start()
            s = perf_counter()
            p.join(time_limit)
            extra_time = round(time_limit - (perf_counter() - s))
            if p.is_alive():
                is_running.value = 0
                p.join(0.05)
                if p.is_alive():
                    p.terminate()
                extra_time = 0
            if self.moves_10x10:
                best_move.value = MOVES_10x10.get(best_move.value, best_move.value)
            return best_move.value, to_self.recv() if to_self.poll() else None, max(0, extra_time)
        except mp.ProcessError:
            traceback.print_exc()
            return ServerError.UNEXPECTED, "Server Error", -1


class JailedRunner(LocalRunner):  # Called from subprocess, no access to django channels/main application
    def run(self):
        while True:
            self.handle(sys.stdin, sys.stdout, sys.stderr)

    def handle(self, stdin: TextIO, stdout: TextIO, stderr: TextIO) -> None:
        time_limit = int(stdin.readline().strip())
        player = stdin.readline().strip()
        board = stdin.readline().strip()

        with redirect_stdout(sys.stderr if self.logging else None):
            move, err, time_limit = self.get_move(board, player, time_limit)

        if err is not None:
            stderr.write(f"SERVER: {err}\n")

        stdout.write(f"{move};{time_limit}\n")

        stdout.flush()
        stderr.flush()
