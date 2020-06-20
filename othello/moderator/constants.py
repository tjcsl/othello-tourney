import enum


class Player(enum.Enum):
    BLACK = "x"
    WHITE = "o"
    EMPTY = "."

    @classmethod
    def opposite_player(cls, current_player):
        return cls.BLACK if current_player == cls.WHITE else cls.WHITE

    @classmethod
    def to_legacy(cls, player):
        return "@" if player == cls.BLACK else cls(player).value

    @classmethod
    def from_legacy(cls, player):
        return cls.BLACK.value if player == "@" else cls(player).value


PLAYERS = {
    0: Player.WHITE,
    1: Player.BLACK,
}

INITIAL_BOARD = "...........................ox......xo..........................."

WHITE, BLACK = 0, 1
INITIAL = {0: 68853694464, 1: 34628173824}  # Binary representation of INITIAL_BOARD
# Since a single tile can be one of three values at any given time ('x', 'o', '.') we must use ...
# two binary numbers(bitboards) to represent the full state of an othello board.
# The binary number with key "0" represents the white bitboard, while the binary number with key "1" represents the black bitboard.
# For the white bitboard, if a tile is 'o' the corresponding binary number is 1 otherwise it is 0
# For the black bitboard, if a tile is 'x' the corresponding binary number is 1 otherwise it is 0


FULL_BOARD = 0xFFFFFFFFFFFFFFFF
RIGHT_MASK = 0xFEFEFEFEFEFEFEFE
LEFT_MASK = 0x7F7F7F7F7F7F7F7F
# These are bit masks, used to prevent bit overflow when shifting a bitboard
# Read more about bit masking here: https://stackoverflow.com/questions/10493411/what-is-bit-masking

MASKS = {  # All the masks for Othello fills are just combinations of the above three masks
    -1: RIGHT_MASK,
    1: LEFT_MASK,
    8: FULL_BOARD,
    -8: FULL_BOARD,
    7: RIGHT_MASK,
    9: LEFT_MASK,
    -7: LEFT_MASK,
    -9: RIGHT_MASK,
}


# These are helper dictionaries that convert a bitboard with only 1 "on" bit to an integer representing the index of the "on" bit
MOVES = {i: 1 << (63 ^ i) for i in range(64)}
POS = {MOVES[63 ^ i]: 63 ^ i for i in range(64)}
LOG = {MOVES[63 ^ i]: i for i in range(64)}

# What are these dictionaries used for
#
# MOVES: binary numbers are 0 indexed from the right, not the left.
# This dictionary takes in an integer representing an index of a string(i.e left-indexed) and points it to a bitboard with
# the corresponding (right-indexed) bit set.
#
# POS: The opposite of MOVES. Takes in a 64-bit number and points it to an integer representing the index of a string
#
# LOG: This is the equivalent of taking the log2 of the binary number.
# Takes in a 64-bit binary number and points it to the log2 of that number.
#
# HIGHLY, HIGHLY recommend playing around with these dictionaries and bitboards in general to gain a better understanding
