from . import utils
from ..apps.games.models import Game


PLAYERS = {
    0: "O",
    1: "X"
}


class Moderator:
    def __init__(self, game: Game):
        self.black = game.black
        self.white = game.white
        self.board = utils.INITIAL
        self.current_player = utils.BLACK
        self.time_limit = game.time_limit

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

