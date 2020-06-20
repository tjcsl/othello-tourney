# Before trying to understand how the server uses binary to calculate moves,
# become familiar with binary numbers, bitwise operators, bit masks, bitboards, and how Python handles binary.
# The functions in Moderator are not intuitive and will be hard to understand without background knowledge.
from typing import Dict, List, Optional, Tuple, Union

from . import constants, utils


class InvalidMoveError(RuntimeError):
    """
    Exception representing an invalid move given the current game state
    """

    def __init__(self, board: str, player: str, move: int) -> None:
        self.code = utils.UserError.INVALID_MOVE.value[0]
        self.message = utils.UserError.INVALID_MOVE.value[1].format(
            move=move, player=constants.PLAYERS[player].value, board=utils.binary_to_string(board)
        )

    def __str__(self) -> str:
        return self.message


class Moderator:
    def __init__(self):
        self.board: Dict[
            int, int
        ] = constants.INITIAL  # bitboards representation of the initial othello board
        self.game_over: bool = False
        self.current_player: int = constants.BLACK  # black moves first

    def is_game_over(self) -> bool:
        return self.game_over

    def get_board(self) -> str:
        """
        Returns the string representation of the current bitboards
        """
        return utils.binary_to_string(self.board)

    def toggle_current_player(self) -> None:
        """
        Switches the current player
        1 ^ 1 = 0
        0 ^ 1 = 1
        """
        self.current_player ^= 1

    def outcome(self) -> Optional[str]:
        """
        Returns the outcome of the game(Black win, White win, Tie)
        A positive score represents a black win, a negative score a white win.
        If the score is 0 the game ended in a tie.

        Score = black_tokens - white_tokens
        """
        if self.is_game_over():
            score = self.score()
            return (
                constants.PLAYERS[constants.BLACK].value
                if score > 0
                else constants.PLAYERS[constants.WHITE].value
                if score < 0
                else "T"
            )

    def possible_moves(self, player: Optional[int] = None) -> int:
        """
        Returns a bitboard representing all the possible moves for the current game state.
        In the resultant bitboard, possible move indices will be "on" while invalid moves will be "off"

        This method and its helpers is an implementation of dumb7fill.
        Read about dumb7fill here: https://www.chessprogramming.org/Dumb7Fill

        @param player If passed, possible moves will be determined for this player instead of the current player in the game
        """
        if player is None:
            player = self.current_player
        discriminator = utils.bit_not(
            self.board[player] | self.board[1 ^ player]
        )  # A bitboard where all the empty indices are turned "on"
        # The discriminator is a bitboard that represents all the currently empty spaces on the board.
        # This bitboard is used as a "dummy check" since a player can only move to an empty tile
        moves = utils.bit_or(
            utils.fill(self.board[player], self.board[1 ^ player], d) & discriminator
            for d in constants.MASKS
        )
        # For each cardinal direction, do a fill in that direction, bitwise AND the result with the discriminator
        # Then bitwise OR all the returned values from all the fills.
        # Think of a "fill" as tracing an Othello bracket in that direction.
        # A North "fill" will shift the current player's bitboard up and compare it to the opponent's bitboard 7 times (8-1).
        # This "fill" will detect all Othello "brackets" and mark the tiles in the bracket as "on"
        # This is a "bracket" (assume current player is 'x'): 'xoo.' The '.' is a possible move according to the Othello rules.
        # Since there are 8 cardinal directions, there are 8 fills (1 in each direction).
        # Each fill will detect all brackets and mark each tile in the bracket as "on" IN ITS SPECIFIED DIRECTION.
        # Since a "bracket" includes the tiles to be flipped after the move, the result is bitwised AND'ed against the discriminator
        # The discriminator roots out all the extraneous bits and all the results are bitwise OR'ed together to get the entire set of possible moves
        return moves

    def make_move(self, move: int) -> None:
        """
        Given an integer move, updates the bitboards to show that the current player has placed a token at that tile.
        This method assumes that the passed move is valid, but will not error if the move is invalid.
        Passing in an invalid move will result in no change to the bitboards.

        @param move tile the current player move to
        """
        board = self.board.copy()
        move = constants.MOVES[move]
        board[self.current_player] |= move
        opponent = 1 ^ self.current_player

        for i in constants.MASKS:
            c = utils.fill(move, board[opponent], i)
            if c & board[self.current_player] != 0:
                c = (
                    (c & constants.MASKS[i * -1]) << i * -1
                    if i < 0
                    else (c & constants.MASKS[i * -1]) >> i
                )
                board[self.current_player] |= c
                board[opponent] &= utils.bit_not(c)
        self.board = board
        self.toggle_current_player()
        # Before reading the method, understand the above "possible_moves" method and how a "fill works"
        # This method uses the same "fill" strategy as the "possible_moves" method but instead actually fills the bracket
        # First this method marks the specified tile as "on" to show that the player has moved to that tile
        # Then it will fill in every direction until it detects that the marked move lines up with the fill (bitwise AND)
        # After it detects that a certain fill lines up with the submitted move, it will shift the fill result back one "unit"
        # This is because the fill marks the entire bracket, but we only want to get the bits that should be flipped (middle bits).
        # Afterwards is updates the current player bitboard with the flipped tile bits and removes those same bits from the opponent bitboard
        # Finally, update the class instance of board, and toggle the current player

    def check_game_over(self) -> bool:
        """
        Checks if the game is over.
        An Othello game is over if neither player can move.
        """
        return self.board[0] & self.board[1] == constants.FULL_BOARD or not (
            self.possible_moves(player=self.current_player)
            or self.possible_moves(player=1 ^ self.current_player)
        )

    def is_valid_move(self, attempted_move: int) -> int:
        """
        Takes in an integer representing a tile which the current player is trying to move to

        This integer is converted to its corresponding bitboard and bitwise AND'ed against the possible moves for the current player

        @param attempted_move tile current plays is trying to move to
        """
        return constants.MOVES.get(attempted_move, None) & self.possible_moves()

    def submit_move(self, submitted_move: int) -> Optional[List[int]]:
        """
        Submits a move for validation.
        submitted_move is an integer representing a tile the current player is trying to move to.
        If the move is valid this function will update the game state accordingly,
        otherwise it will raise a InvalidMoveError.

        If a move results in the game being over, this method will return False.
        Otherwise, it will return a list of integers representing the new set of possible moves

        @param submitted_move tile current plays is trying to move to

        """
        if not self.is_valid_move(submitted_move):
            raise InvalidMoveError(self.board, self.current_player, submitted_move)

        self.make_move(submitted_move)

        if self.check_game_over():
            self.game_over = True
            return None

        if not self.possible_moves():
            self.toggle_current_player()

        return list(utils.isolate_bits(self.possible_moves()))

    def get_game_state(self) -> Tuple[str, constants.Player]:
        """
        Returns the current board and player
        """
        return utils.binary_to_string(self.board), constants.PLAYERS[self.current_player]

    def score(self) -> int:
        """
        Returns the score of the game.
        Calculated by: black_tokens - white_tokens
        """
        return utils.hamming_weight(self.board[1]) - utils.hamming_weight(self.board[0])
