WHITE, BLACK = 0, 1
INITIAL = {0: 68853694464, 1: 34628173824}

FULL_BOARD = 0xffffffffffffffff
RIGHT_MASK = 0xfefefefefefefefe
LEFT_MASK = 0x7f7f7f7f7f7f7f7f

MASKS = {
    -1: RIGHT_MASK,
    1: LEFT_MASK,
    8: FULL_BOARD,
    -8: FULL_BOARD,
    7: RIGHT_MASK,
    9: LEFT_MASK,
    -7: LEFT_MASK,
    -9: RIGHT_MASK
}

MOVES = {i: 1 << (63 ^ i) for i in range(64)}
POS = {MOVES[63 ^ i]: 63 ^ i for i in range(64)}
LOG = {MOVES[63 ^ i]: i for i in range(64)}
