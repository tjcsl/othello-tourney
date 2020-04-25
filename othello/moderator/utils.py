import operator
import importlib.util
import importlib.machinery

from functools import lru_cache, partial, reduce, wraps

from .constants import *


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


bit_or = partial(reduce, operator.__or__)


def is_on(x, pos):
    return x & (1 << pos)


def bit_not(x):
    return FULL_BOARD ^ x


def binary_to_string(board):
    return "".join(['o' if is_on(board[0], 63 - i) else 'x' if is_on(board[1], 63 - i) else '.' for i in range(64)])


@lru_cache
def hamming_weight(n):
    c = 0
    while n:
        c += 1
        n ^= n & -n
    return c


def fill(current, opponent, direction):
    mask = MASKS[direction]
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
    while x:
        b = -x & x
        yield POS[b]
        x -= b
