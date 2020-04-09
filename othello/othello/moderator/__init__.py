import io, sys
import multiprocessing as mp

from . import utils
from ..apps.games.utils import import_strategy
from ..apps.games.models import Game


PLAYERS = {
    0: "O",
    1: "X"
}


def binary_to_string(board):
    return "".join(['O' if utils.is_on(board[0], 63 - i) else 'X' if utils.is_on(board[1], 63 - i) else '.' for i in range(64)])


logs = []


class LogPrints:
    def __init__(self, logging, callback):
        self.logging = logging

    def __enter__(self):
        self._stdout = sys.stdout
        sys.stdout = self._stringio = io.StringIO()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.logging:
            sys.stdout = self._stdout
            logs.extend(self._stringio.getvalue().splitlines())
            del self._stringio


class Moderator:
    def __init__(self, game: Game):
        self.black = game.black
        self.white = game.white
        self.board = utils.INITIAL
        self.current_player = utils.BLACK
        self.time_limit = game.time_limit
        self.logs = []
        self.strats = {
            utils.BLACK: {
                'strat': import_strategy(self.black.code.path),
            },
            utils.WHITE: {
                'strat': import_strategy(self.white.code.path),
            }
        }
        self.strats[utils.BLACK]['log'] = LogPrints(getattr(self.strats[utils.BLACK]['strat'], 'logging', False), self.log_callback)
        self.strats[utils.WHITE]['log'] = LogPrints(getattr(self.strats[utils.WHITE]['strat'], 'logging', False), self.log_callback)

    def possible_moves(self):
        discriminator = utils.FULL_BOARD ^ (self.board[self.current_player] | self.board[1 ^ self.current_player])
        moves = utils.bit_or(utils.fill(self.board[self.current_player], self.board[1 ^ self.current_player], d) & discriminator for d in utils.MASKS)
        return moves

    def make_move(self, move):
        board = self.board.copy()
        move = utils.MOVES[move]
        board[self.current_player] |= move
        opponent = 1 ^ self.current_player

        for i in utils.MASKS:
            c = utils.fill(move, board[opponent], i)
            if c & board[self.current_player] != 0:
                c = (c & utils.MASKS[i*-1]) << i*-1 if i < 0 else (c & utils.MASKS[i*-1]) >> i
                board[self.current_player] |= c
                board[opponent] &= utils.bit_not(c)
        self.board = board

    def is_valid_move(self, attempted_move):
        return utils.MOVES[attempted_move] & self.possible_moves()

    def play_wrapper(self, *args):
        with self.strats[self.current_player]['log']:
            self.strats[self.current_player]['strat'].best_strategy(
                binary_to_string(self.board),
                PLAYERS[self.current_player],
                *args
            )

    def log_callback(self, x):
        self.logs.extend(x)

    def play(self):
        best_value = mp.Value("i", -1)
        is_running = mp.Value("i", 1)
        p = mp.Process(target=self.play_wrapper, args=(best_value, is_running))
        p.start()
        p.join(self.time_limit)
        print(best_value.value)

