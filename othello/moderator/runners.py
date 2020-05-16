import os
import sys
import enum
import time
import psutil
import select
import signal
import traceback
import subprocess
import multiprocessing as mp

from ..sandboxing import get_sandbox_args
from .utils import UserError, ServerError, import_strategy, capture_generator_value


class PrintLogger:
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

        with PrintLogger(self.logging):
            move, err = self.get_move(board, player, time_limit)

        if err is not None:
            stderr.write(f"SERVER: {err}\n")

        stdout.write(f"{move}\n")

        stdout.flush()
        stderr.flush()


class PlayerRunner:

    def __init__(self, path, driver, debug):
        self.path = path
        self.process = None
        self.driver, self.debug = driver, debug

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.process is not None:
            children = psutil.Process(self.process.pid).children(recursive=True)
            try:
                os.killpg(self.process.pid, signal.SIGKILL)
            except ProcessLookupError:
                self.process.kill()
            for child in children:
                try:
                    child.kill()
                except psutil.NoSuchProcess:
                    pass
            self.process = None

    def start(self):
        cmd_args = ["python3", "-u", self.driver, self.path]
        if not self.debug:
            cmd_args = get_sandbox_args(cmd_args)

        self.process = subprocess.Popen(cmd_args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                        bufsize=0, cwd=os.path.dirname(self.path), preexec_fn=os.setpgrp,)

    @capture_generator_value
    def get_move(self, board, player, time_limit, last_move):
        self.process.stdin.write(f"{str(time_limit)}\n{player}\n{''.join(board)}\n".encode("latin-1"))
        self.process.stdin.flush()
        move = -1

        start, total_timeout = time.time(), time_limit+10
        while move == -1:
            if self.process.poll():
                return -1, ServerError.PROCESS_EXITED
            if (timeout := total_timeout - (time.time() - start)) <= 0:
                return -1, ServerError.TIMEOUT

            files_ready = select.select([self.process.stdout, self.process.stderr], [], [], timeout)[0]
            if self.process.stderr in files_ready:
                yield self.process.stderr.read(8192).decode("latin-1")
            if self.process.stdout in files_ready:
                try:
                    move = int(self.process.stdout.readline())
                    if move < 0 or move >= 64:
                        return -1, UserError.NO_MOVE_ERROR
                except ValueError:
                    return -1, UserError.READ_INVALID
        return move, 0


class YourselfRunner:

    def __init__(self, game):
        self.game = game

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    @capture_generator_value
    def get_move(self, board, player, time_limit, last_move):
        yield "Choose your move!"
        while True:
            if (m := self.game.moves.latest()) != last_move:
                return m.move, 0

