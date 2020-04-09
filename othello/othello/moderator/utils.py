import operator
from functools import lru_cache, partial, reduce

from .constants import *

bit_or = partial(reduce, operator.__or__)


def is_on(x, pos):
    return x & (1 << pos)


def bit_not(x):
    return FULL_BOARD ^ x


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
