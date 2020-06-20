import os
import select
import signal
import subprocess
import time
from typing import Generator, Tuple, Union

import psutil

from django.conf import settings

from ..apps.games.models import Move, Submission
from ..sandboxing import get_sandbox_args
from .constants import Player
from .utils import ServerError, UserError, capture_generator_value

# Legacy moves have a padding of "#"s around all four sides of the grid.
LEGACY_MOVES = {(i + 11 + 2 * (i // 8)): i for i in range(64)}


def legacy_board_convert(board: str) -> str:
    table = {ord(Player.WHITE.value): "o", ord(Player.BLACK.value): "@"}
    return (
        "?" * 11 + "??".join(board[i: i + 8].translate(table) for i in range(0, 64, 8)) + "?" * 11
    )


class PlayerRunner:
    def __init__(self, submission: Submission, driver: str) -> None:
        if not os.path.isfile(submission.code.path):
            raise OSError("file not found")
        self.path = submission.code.path
        self.is_legacy = submission.is_legacy
        self.process = None
        self.driver = driver

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

    def start(self):
        cmd_args = ["python3", "-u", self.driver, self.path]
        if not settings.DEBUG:
            cmd_args = get_sandbox_args(
                cmd_args,
                whitelist=[os.path.dirname(self.path)],
                readonly=[
                    os.path.dirname(self.path)
                ],  # WARNING: Making the submission directory writable creates potential for extremely dangerous symlink attacks
            )

        self.process = subprocess.Popen(
            cmd_args,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            bufsize=0,
            cwd=os.path.dirname(self.path),
            preexec_fn=os.setpgrp,
        )

    def stop(self):
        if self.process is not None:
            try:
                children = psutil.Process(self.process.pid).children(recursive=True)
                os.killpg(self.process.pid, signal.SIGKILL)
            except psutil.NoSuchProcess:
                self.process = None
                return
            except ProcessLookupError:
                self.process.kill()
            for child in children:
                try:
                    child.kill()
                except psutil.NoSuchProcess:
                    pass
            self.process = None

    @capture_generator_value
    def get_move(
        self, board: str, player: Player, time_limit: int, last_move: Move
    ) -> Generator[
        str, None, Union[Tuple[int, int], Tuple[int, ServerError], Tuple[int, UserError]]
    ]:
        if self.process.poll():
            print(self.process.communicate())
            return -1, ServerError.PROCESS_EXITED

        if self.is_legacy:
            board = legacy_board_convert(board)
            player = player.to_legacy()

        self.process.stdin.write(
            f"{str(time_limit)}\n{player.value}\n{''.join(board)}\n".encode("latin-1")
        )
        self.process.stdin.flush()
        move = -1

        start, total_timeout = time.time(), time_limit + 10
        while move == -1:
            if self.process.poll():
                print(self.process.communicate())
                return -1, ServerError.PROCESS_EXITED
            if (timeout := total_timeout - (time.time() - start)) <= 0:
                return -1, ServerError.TIMEOUT

            files_ready = select.select(
                [self.process.stdout, self.process.stderr], [], [], timeout
            )[0]
            if self.process.stderr in files_ready:
                yield self.process.stderr.read(8192).decode("latin-1")
            if self.process.stdout in files_ready:
                try:
                    move = int(self.process.stdout.readline())
                    print(f"GOT MOVE {move}")
                    if self.is_legacy:
                        if move not in LEGACY_MOVES:
                            return -1, UserError.READ_INVALID
                    else:
                        if move < 0 or move >= 64:
                            return -1, UserError.READ_INVALID
                except ValueError:
                    return -1, UserError.READ_INVALID
        return (move, 0) if not self.is_legacy else (LEGACY_MOVES[move], 0)


class YourselfRunner:
    def __init__(self, game, timeout):
        self.timeout = timeout
        self.game = game

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def stop(self):
        pass

    @capture_generator_value
    def get_move(
        self, board: str, player: Player, time_limit: int, last_move: Move
    ) -> Generator[
        str, None, Union[Tuple[int, int], Tuple[int, ServerError], Tuple[int, UserError]]
    ]:
        yield "Choose your move!"
        start = time.time()
        while True:
            self.game.refresh_from_db()
            if not self.game.playing:
                return -1, ServerError.DISCONNECT
            if (time.time() - start) > self.timeout:
                return -1, UserError.NO_MOVE_ERROR
            if (m := self.game.moves.latest()) != last_move:
                if m is not None:
                    m.delete()
                    return m.move, 0
                else:
                    return -1, ServerError.DISCONNECT
