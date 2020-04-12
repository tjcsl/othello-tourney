import sys
import shlex
import logging
import traceback
import subprocess
import threading
import multiprocessing as mp

from queue import Queue, Empty

from .utils import import_strategy, safe_int
from .settings import *

log = logging.getLogger(__name__)


def enqueue_stream_helper(stream, q, event):
    """
    Continuously reads from stream and puts any results into
    the queue `q`
    """
    for line in iter(stream.readline, b''):
        if event.is_set():
            break
        q.put(line)
    stream.close()


def get_stream_queue(stream, event):
    """
    Takes in a stream, and returns a Queue that will return the output from that stream. Starts a background thread as a side effect.
    """
    threading.Thread(target=enqueue_stream_helper, args=(stream, q := Queue(), event), daemon=True).start()

    return q


class HiddenPrints:
    """
    Surpresses all stdout from a subprocess so we
    can only send what we need to to our parent
    """

    def __enter__(self):
        self._original_stdout = sys.stdout
        sys.stdout = sys.stderr

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout = self._original_stdout


class LocalRunner:
    def __init__(self, script_path):
        self.path = script_path
        self.strat = import_strategy(script_path)
        self.logging = getattr(self.strat, "logging", False)

    def play_wrapper(self, *game_args, pipe_to_parent):
        with HiddenPrints():
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
        except:
            traceback.print_exc()
            return -1, "Server Error"


class JailedRunner(LocalRunner):

    def run(self):
        while True:
            self.handle(sys.stdin, sys.stdout, sys.stderr)

    def handle(self, stdin, stdout, stderr):
        time_limit = int(stdin.readline().strip())
        player = stdin.readline().strip()
        board = stdin.readline().strip()

        data = (time_limit, player, board)

        move, err = self.get_move(board, player, time_limit)

        if err is not None:
            stderr.write(err)

        stdout.write(f"{move}\n")

        stdout.flush()
        stderr.flush()


class JailedRunnerCommunicator:

    def __init__(self, path):
        self.path = path
        self.process = None

    def start(self):
        cmd_args = shlex.split(OTHELLO_AI_RUN_COMMAND.format(self.path), posix=False)
        self.process = subprocess.Popen(cmd_args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                        bufsize=1, universal_newlines=True, cwd=os.path.dirname(self.path))
        self.stop_event = threading.Event()
        self.stdout_stream = get_stream_queue(self.process.stdout, self.stop_event)
        self.stderr_stream = get_stream_queue(self.process.stderr, self.stop_event)

    def check_for_errors(self):
        last_err_line, errs = "", []
        while last_err_line is not None:
            errs.append(last_err_line)
            try:
                last_err_line = self.stderr_stream.get_nowait()
            except:
                last_err_line = None
        return ''.join(errs)

    def get_move(self, board, player, time_limit):
        data = f"{str(time_limit)}\n{player}\n{''.join(board)}\n"

        if errs := self.check_for_errors():
            log.error(errs)
        self.process.stdin.write(data)
        self.process.stdin.flush()
        log.debug("wrote data to subprocess")

        output = ""
        try:
            output = self.stdout_stream.get(timeout=time_limit+10)
        except Empty:
            log.warning("Timeout reading from subprocess")

        if errs2 := self.check_for_errors():
            errs += errs2
            log.error(errs)

        return safe_int(output.split("\n")[0]), errs

    def stop(self):
        if self.process is not None:
            self.process.kill()
            self.stop_event.set()
            self.process = None

    def __del__(self):
        self.stop()
