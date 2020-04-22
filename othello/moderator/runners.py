import os
import sys
import enum
import time
import select
import traceback
import subprocess
import multiprocessing as mp

from ..sandboxing import get_sandbox_args
from .utils import import_strategy, capture_generator_value


class UserError(enum.Enum):

    NO_MOVE_ERROR = -1#(-1, "No move submitted")
    READ_INVALID = -2#(-2, "Submitted move is not an integer")


class ServerError(enum.Enum):

    TIMEOUT = -3#(-3, "Timed out reading from subprocess")
    UNEXPECTED = -4#(-4, "Unexpected error")


class HiddenPrints:
    def __init__(self, logging=False):
        self.logging = logging

    def __enter__(self):
        self._original_stdout = sys.stdout
        if self.logging:
            sys.stdout = sys.stderr
        else:
            sys.stdout = open(os.devnull, 'w')
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout = self._original_stdout


class LocalRunner:  # Called from JailedRunner, inherits accessibility restrictions
    def __init__(self, script_path):
        self.path = script_path
        self.strat = import_strategy(script_path)
        self.logging = getattr(self.strat, "logging", False)

    def play_wrapper(self, *game_args, pipe_to_parent):
        with HiddenPrints(self.logging):
            try:
                self.strat.best_strategy(*game_args)
                pipe_to_parent.send(None)
            except:
                pipe_to_parent.send(traceback.format_exc())

    def get_move(self, board, player, time_limit):
        best_move, is_running = mp.Value("i", -1), mp.Value("i", 1)

        to_child, to_self = mp.Pipe()
        try:
            p = mp.Process(target=self.play_wrapper, args=("".join(board), player, best_move, is_running), kwargs={"pipe_to_parent": to_child})
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


class JailedRunner(LocalRunner):  # Called from subprocess, no access to django channels/main application

    def run(self):
        while True:
            self.handle(sys.stdin, sys.stdout, sys.stderr)

    def handle(self, stdin, stdout, stderr):
        time_limit = int(stdin.readline().strip())
        player = stdin.readline().strip()
        board = stdin.readline().strip()

        move, err = self.get_move(board, player, time_limit)

        if err is not None:
            stderr.write(f"SERVER: {err}\n")

        stdout.write(f"{move}\n")

        stdout.flush()
        stderr.flush()


class PlayerRunner:

    def __init__(self, path, settings):
        self.path = path
        self.settings = settings
        self.process = None

        self.start()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

    def start(self):
        cmd_args = ["python3", "-u", self.settings.JAILEDRUNNER_DRIVER, self.path]
        if not self.settings.DEBUG:
            cmd_args = get_sandbox_args(cmd_args)

        self.process = subprocess.Popen(cmd_args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                        bufsize=0, universal_newlines=True, cwd=os.path.dirname(self.path), preexec_fn=os.setpgrp,)

    def stop(self):
        if self.process is not None:
            self.process.kill()
            self.process = None

    @capture_generator_value
    def get_move(self, board, player, time_limit):
        self.process.stdin.write(f"{str(time_limit)}\n{player}\n{''.join(board)}\n")
        self.process.stdin.flush()
        move = -1

        start, total_timeout = time.time(), time_limit+5
        while move == -1:
            if (timeout := total_timeout - (time.time() - start)) <= 0:
                return -1, ServerError.TIMEOUT

            files_ready = select.select([self.process.stdout, self.process.stderr], [], [], timeout)[0]
            print(files_ready, self.process.stderr in files_ready, self.process.stdout in files_ready)
            if self.process.stderr in files_ready:
                log = self.process.stderr.read(8192)
                print(log)
                yield log
            if self.process.stdout in files_ready:
                try:
                    move = int(self.process.stdout.readline())
                    if move < 0 or move >= 64:
                        return -1, UserError.NO_MOVE_ERROR
                except ValueError:
                    return -1, UserError.READ_INVALID
        return move, 0
