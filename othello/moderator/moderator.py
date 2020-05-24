import enum

from . import utils


class Player(enum.Enum):
    BLACK = 'x'
    WHITE = 'o'


PLAYERS = {
    0: Player.WHITE,
    1: Player.BLACK,
}

INITIAL_BOARD = "...........................ox......xo..........................."


class InvalidMoveError(RuntimeError):
    def __init__(self, board, player, move):
        self.code = utils.UserError.INVALID_MOVE.value[0]
        self.message = utils.UserError.INVALID_MOVE.value[1].format(move=move, player=PLAYERS[player].value, board=utils.binary_to_string(board))

    def __str__(self):
        return self.message


class Moderator:
    def __init__(self):
        self.board = utils.INITIAL
        self.game_over = False
        self.current_player = utils.BLACK

    def is_game_over(self):
        return self.game_over

    def get_board(self):
        return utils.binary_to_string(self.board)

    def outcome(self):
        if self.is_game_over():
            score = self.score()
            return PLAYERS[utils.BLACK].value if score > 0 else PLAYERS[utils.WHITE].value if score < 0 else 'T'
        return False

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
        self.board, self.current_player = board, opponent

    def check_game_over(self):
        current_moves = self.possible_moves()
        self.current_player ^= 1
        opponent_moves = self.possible_moves()
        self.current_player ^= 1
        return self.board[0] & self.board[1] == utils.FULL_BOARD or not (current_moves or opponent_moves)

    def is_valid_move(self, attempted_move):
        return utils.MOVES.get(attempted_move, False) & self.possible_moves()

    def submit_move(self, submitted_move):
        if not self.is_valid_move(submitted_move):
            raise InvalidMoveError(self.board, self.current_player, submitted_move)

        self.make_move(submitted_move)

        if self.check_game_over():
            self.game_over = True
            return False

        if not self.possible_moves():
            self.current_player = 1 ^ self.current_player

        return list(utils.isolate_bits(self.possible_moves()))

    def get_game_state(self):
        return utils.binary_to_string(self.board), PLAYERS[self.current_player]

    def score(self):
        return utils.hamming_weight(self.board[1]) - utils.hamming_weight(self.board[0])
