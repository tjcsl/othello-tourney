import enum
import importlib.machinery
import operator
from functools import partial, reduce, wraps

from . import constants


class UserError(enum.Enum):

    NO_MOVE_ERROR = (-1, "No move submitted")
    READ_INVALID = (-2, "Submitted move is not an integer or within range")
    INVALID_MOVE = (-3, "{move} is invalid for {player} on {board}")


class ServerError(enum.Enum):

    TIMEOUT = (-4, "Timed out reading from subprocess")
    UNEXPECTED = (-5, "Unexpected error")
    PROCESS_EXITED = (-6, "Process exited unexpectedly")
    FILE_DELETED = (-7, "Player script cannot be found on the server")
    DISCONNECT = (-8, "Unexpectedly disconnected from socket")


class Generator:
    def __init__(self, gen):
        self.gen = gen
        self.return_value = None

    def __iter__(self):
        self.return_value = yield from self.gen


def capture_generator_value(f):
    @wraps(f)
    def g(*args, **kwargs):
        return Generator(f(*args, **kwargs))

    return g


def import_strategy(path):
    return importlib.machinery.SourceFileLoader("strategy", path).load_module().Strategy()


bit_or = partial(reduce, operator.__or__)  # mimic builtin "sum" function except with bitwise or


def is_on(x, pos):
    """
    Checks if an index on a 8x8 bitboard is "on"(1)

    @param x 8x8 bitboard
    @param pos index on bitboard
    """
    return x & (1 << pos)


def bit_not(x):
    """
    Returns the bitwise NOT value of a 8x8 bitboard
    """
    return constants.FULL_BOARD ^ x


def binary_to_string(board):
    """
    Converts a 8x8 othello bitboard to its string representation

    @param board 8x8 othello bitboard
    """
    return "".join(
        [
            constants.Player.WHITE.value
            if is_on(board[0], 63 - i)
            else constants.Player.BLACK.value
            if is_on(board[1], 63 - i)
            else constants.Player.EMPTY.value
            for i in range(64)
        ]
    )


def hamming_weight(n):
    """
    Calculates the hamming weight of a binary number (number of "on"(1) bits)

    @param n binary number
    """
    c = 0
    while n:
        c += 1
        n ^= n & -n
    return c


def fill(current, opponent, direction):
    """
    Does a binary dumb7fill in one cardinal direction (N, E, S, W, NE, NW, SE, SW)
    Read https://www.chessprogramming.org/Dumb7Fill for the strategy and how it relates to Chess

    This is a helper method for calculating the possible moves for a board and player using binary.
    Calculating possible moves for a board runs a fill in each cardinal direction

    @param current 8x8 othello bitboard for the current player
    @param opponent 8x8 othello bitboard for the opponent player
    @param direction value in constants.MASK that represents the direction to fill in.

    """
    mask = constants.MASKS[direction]
    if direction > 0:
        w = ((current & mask) << direction) & opponent
        w |= ((w & mask) << direction) & opponent
        w |= ((w & mask) << direction) & opponent
        w |= ((w & mask) << direction) & opponent
        w |= ((w & mask) << direction) & opponent
        w |= ((w & mask) << direction) & opponent
        return (w & mask) << direction
    direction *= -1
    w = ((current & mask) >> direction) & opponent
    w |= ((w & mask) >> direction) & opponent
    w |= ((w & mask) >> direction) & opponent
    w |= ((w & mask) >> direction) & opponent
    w |= ((w & mask) >> direction) & opponent
    w |= ((w & mask) >> direction) & opponent
    return (w & mask) >> direction


def isolate_bits(x):
    """
    Generator that returns the indices of all the "on"(1) bits in a 8x8 bitboard

    @param x 8x8 bitboard
    """
    while x:
        b = -x & x
        yield constants.POS[b]
        x -= b
