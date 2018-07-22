from model.board import GameBoard, uint32_from_bool_array
from model.config import Direction, RACK_SIZE, BOARD_SIZE, LETTER_DISTRIBUTIONS
from model.lexicon import Lexicon
from model.move import Move
from model.row import Row
from model.tile import Tile
from util.bit_twiddling import read_bit, set_bit, clear_bit
import numpy as np


class MoveValidationError(ValueError):
    """ Raised when a move is invalid """


class MoveValidator:
    """ Validates game moves. """

    def __init__(self, lexicon: Lexicon, board: GameBoard):
        self.lexicon = lexicon
        self.board = board

    def is_valid(self, move: Move):
        """ Validate a move.
        :param move: The move to be validated.
        :return: boolean True if move is valid, otherwise a MoveValidationError is raised
        giving the reason for the move being invalid.
        """
        pass

        if move.direction == Direction.NOT_APPLICABLE:  # we must be passing or swapping letters
            return True  # Player must have passed or exchanged

        num_tiles = len(move.tiles)
        start_index = move.start_index

        # check we are playing a sensible number of tiles:
        if num_tiles < 1 or num_tiles > RACK_SIZE:
            raise MoveValidationError('move has invalid number of tiles')

        # get row or column as appropriate (columns come back transposed to a row):
        row = move.row

        # check we're not on a sentinel square
        if start_index < 1 or start_index >= BOARD_SIZE:
            raise MoveValidationError("starting square is off the board")

        if not row.square_is_empty(start_index):
            raise MoveValidationError("starting square is not free")

        if len(move.played_squares) < num_tiles:
            raise MoveValidationError("not enough free spaces")

        if not self.has_valid_hook(row, move.played_squares):
            raise MoveValidationError("word must join an existing word or start square")

        row.place_tiles(move.played_squares, move.tiles)

        if not self.crosswords_valid(row):
            row.remove_tiles(move.played_squares)
            raise MoveValidationError("invalid cross-word formed")

        word_formed = row.word_at(start_index)
        if word_formed not in self.lexicon:
            row.remove_tiles(move.played_squares)
            raise MoveValidationError("'" + word_formed + "'is not a valid word")

        move.calculate_score()

        return True

    def is_valid_move(self, move: Move):
        """ returns true if a move is valid and false if not.
        This is distinct from is_valid() which throws a descriptive exception where a move
        is not valid. This exception-swallowing version allows broadcasting validity
        across a list of moves, for example """
        try:
            return self.is_valid(move)
        except MoveValidationError:
            return False

    def crosswords_valid(self, row: Row):
        # ensure that for every letter now on the board in this row,
        # the bit in valid_letters for that particular letter is not set to False
        # (slice removes sentinel squares)
        return all([read_bit(letter_check[0],letter_check[1])
                    for letter_check in np.column_stack(
                (row.valid_letters[1:-1],row.existing_letters[1:-1]))])

    def update_affected_squares(self, move: Move):
        """ Updates cached running totals and valid letters to play when making cross-words
        """
        filled_squares = move.row.squares_in_word(move.start_index)
        move.row.update_hooks_and_running_scores(move.start_index)
        self.update_valid_letters(move.row, move.start_index)

        for i in filled_squares:
            column = self.board.get_row(i, move.cross_direction())
            column.update_hooks_and_running_scores(move.row.rank)
            self.update_valid_letters(column, move.row.rank)

    @staticmethod
    def has_valid_hook(row, played_squares):
        return any(row.hook_squares[played_squares])

    def update_valid_letters(self, row: Row, index: int):
        square_before = row.squares_in_word(index)[0] - 1
        if square_before > 0:
            row.orthogonal_row_crosschecks[square_before] = self.valid_letters_for_square(row, square_before)

        square_after = row.squares_in_word(index)[-1] + 1
        if square_after < BOARD_SIZE:
            row.valid_letters[square_after] = self.valid_letters_for_square(row, square_after)

    def valid_letters_for_square(self, row: Row, index: int):
        valid_letters = (1 << 32) - 1
        for i in range(1,len(LETTER_DISTRIBUTIONS)):
            row.existing_lettrs[index] = i
            if row.word_at(index) not in self.lexicon:
                valid_letters = clear_bit(valid_letters, i)
        row.existing_letters[index] = 0
        return valid_letters
