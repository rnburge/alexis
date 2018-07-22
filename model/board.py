import numpy as np
from model.config import Direction, BOARD_SIZE, NO_CROSS_WORD
from model.row import Row
from util.bit_twiddling import *


class GameBoard:
    """ Represents a game board. """

    def __init__(self):
        """ creates a new game board """

        # Array representing valid game starting locations
        self.hook_squares = np.array([
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        ], dtype='bool')  # numpy booleans

        # Array representing word multiplier for each board square
        self.word_multipliers = np.array([
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 3, 1, 1, 1, 1, 1, 1, 3, 1, 1, 1, 1, 1, 1, 3, 0],
            [0, 1, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 1, 0],
            [0, 1, 1, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 1, 1, 0],
            [0, 1, 1, 1, 2, 1, 1, 1, 1, 1, 1, 1, 2, 1, 1, 1, 0],
            [0, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1, 2, 1, 1, 1, 1, 0],
            [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
            [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
            [0, 3, 1, 1, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1, 1, 3, 0],
            [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
            [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
            [0, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1, 2, 1, 1, 1, 1, 0],
            [0, 1, 1, 1, 2, 1, 1, 1, 1, 1, 1, 1, 2, 1, 1, 1, 0],
            [0, 1, 1, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 1, 1, 0],
            [0, 1, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 1, 0],
            [0, 3, 1, 1, 1, 1, 1, 1, 3, 1, 1, 1, 1, 1, 1, 3, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        ], dtype='int8')

        # Array representing initial letter multiplier for each
        # board square (multipliers only used when first played,
        # then they are changed to 1, the multiplication identity
        self.letter_multipliers = np.array([
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 1, 1, 1, 2, 1, 1, 1, 1, 1, 1, 1, 1, 2, 1, 1, 0],
            [0, 1, 1, 1, 1, 1, 3, 1, 1, 1, 3, 1, 1, 1, 1, 1, 0],
            [0, 1, 1, 1, 1, 1, 1, 2, 1, 2, 1, 1, 1, 1, 1, 1, 0],
            [0, 2, 1, 1, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1, 1, 2, 0],
            [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
            [0, 1, 3, 1, 1, 1, 3, 1, 1, 1, 3, 1, 1, 1, 3, 1, 0],
            [0, 1, 1, 2, 1, 1, 1, 2, 1, 2, 1, 1, 1, 2, 1, 1, 0],
            [0, 1, 1, 1, 2, 1, 1, 1, 1, 1, 1, 1, 2, 1, 1, 1, 0],
            [0, 1, 1, 2, 1, 1, 1, 2, 1, 2, 1, 1, 1, 2, 1, 1, 0],
            [0, 1, 3, 1, 1, 1, 3, 1, 1, 1, 3, 1, 1, 1, 3, 1, 0],
            [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
            [0, 2, 1, 1, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1, 1, 2, 0],
            [0, 1, 1, 1, 1, 1, 1, 2, 1, 2, 1, 1, 1, 1, 1, 1, 0],
            [0, 1, 1, 1, 1, 1, 3, 1, 1, 1, 3, 1, 1, 1, 1, 1, 0],
            [0, 1, 1, 1, 2, 1, 1, 1, 1, 1, 1, 1, 1, 2, 1, 1, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        ], dtype='int8')

        # letters already on board (A=1, B=2, etc)
        self.existing_letters = np.array([
            [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
            [-1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1],
            [-1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1],
            [-1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1],
            [-1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1],
            [-1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1],
            [-1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1],
            [-1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1],
            [-1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1],
            [-1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1],
            [-1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1],
            [-1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1],
            [-1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1],
            [-1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1],
            [-1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1],
            [-1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1],
            [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1]
        ], dtype='int8')

        # score of letters already on board (blank will be zero)
        self.existing_letter_scores = np.zeros([17, 17], dtype='int8')

        t = (1 << 32) - 1  # valid letters, all 26 letters are True, padded to uint32

        # Array representing letters blocked from play
        # when playing across a row due to this forming an invalid
        # word in the orthogonal column. Effectively a bitarray
        # per square with letters 1(A) to 26(Z) either valid(1) or
        # blocked from play(0).
        self.row_crosschecks = np.array([
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, t, t, t, t, t, t, t, t, t, t, t, t, t, t, t, 0],
            [0, t, t, t, t, t, t, t, t, t, t, t, t, t, t, t, 0],
            [0, t, t, t, t, t, t, t, t, t, t, t, t, t, t, t, 0],
            [0, t, t, t, t, t, t, t, t, t, t, t, t, t, t, t, 0],
            [0, t, t, t, t, t, t, t, t, t, t, t, t, t, t, t, 0],
            [0, t, t, t, t, t, t, t, t, t, t, t, t, t, t, t, 0],
            [0, t, t, t, t, t, t, t, t, t, t, t, t, t, t, t, 0],
            [0, t, t, t, t, t, t, t, t, t, t, t, t, t, t, t, 0],
            [0, t, t, t, t, t, t, t, t, t, t, t, t, t, t, t, 0],
            [0, t, t, t, t, t, t, t, t, t, t, t, t, t, t, t, 0],
            [0, t, t, t, t, t, t, t, t, t, t, t, t, t, t, t, 0],
            [0, t, t, t, t, t, t, t, t, t, t, t, t, t, t, t, 0],
            [0, t, t, t, t, t, t, t, t, t, t, t, t, t, t, t, 0],
            [0, t, t, t, t, t, t, t, t, t, t, t, t, t, t, t, 0],
            [0, t, t, t, t, t, t, t, t, t, t, t, t, t, t, t, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        ], dtype='uint32')

        # Array representing current total score of other squares
        # in this word that are in same column when playing across a row
        # (no score registered is indicated as '-1' since there is no
        # 'None' in numpy integer arrays, and zero could be a legitimate
        # score for a played blank
        self.row_cross_scores = np.full([17, 17], NO_CROSS_WORD, dtype='int32')

        # Array representing letters blocked from play
        # when playing down a column, due to this forming an invalid
        # word in the orthogonal row. Effectively a bitarray
        # per column with letters at bit 1(A) to 26(Z) either valid(1) or
        # blocked from play(0).
        self.column_crosschecks = np.copy(self.row_crosschecks)

        # Array representing current total score of other squares
        # in this word that are in same row when playing across a column
        self.column_cross_scores = np.copy(self.row_cross_scores)

    def get_row(self, rank: int, direction: Direction):
        """returns a given row of the board. This is a copy of the underlying
        game board and any changes to this row object will not be reflected in the board.

        :param rank: the rank index of the row (1 is the first row, 2 is the second row, etc)
        :param direction: Optional. If vertical, a column is returned (transposed to a row)

        :return: a Row object
        """

        if direction == Direction.HORIZONTAL:
            row_data = (self.hook_squares[:, rank],
                        self.word_multipliers[:, rank],
                        self.letter_multipliers[:, rank],
                        self.existing_letters[:, rank],
                        self.existing_letter_scores[:, rank],
                        self.row_crosschecks[:, rank],
                        self.row_cross_scores[:, rank],
                        self.column_crosschecks[:, rank],
                        self.column_cross_scores[:, rank])

        elif direction == Direction.VERTICAL:
            row_data = (self.hook_squares[rank, :],
                        self.word_multipliers[rank, :],
                        self.letter_multipliers[rank, :],
                        self.existing_letters[rank, :],
                        self.existing_letter_scores[rank, :],
                        self.column_crosschecks[rank, :],
                        self.column_cross_scores[rank, :],
                        self.row_crosschecks[rank, :],
                        self.row_cross_scores[rank, :])
        else:
            row_data = None

        return Row(direction, rank, row_data)

    def __str__(self):
        board = '     ' + ' '.join([chr(64 + x) for x in range(1, BOARD_SIZE)]) + '\n'
        for i in range(BOARD_SIZE + 1):
            board += str(self.get_row(i, Direction.HORIZONTAL)) + '\n'
        board += '     ' + ' '.join([chr(64 + x) for x in range(1, BOARD_SIZE)])
        return board

    def board_string_with_hooks(self):
        board = '     ' + ' '.join([chr(64 + x) for x in range(1, BOARD_SIZE)]) + '\n'
        for i in range(BOARD_SIZE + 1):
            row = self.get_row(i, Direction.HORIZONTAL)
            board += row.row_string_showing_hooks() + '\n'
        board += '     ' + ' '.join([chr(64 + x) for x in range(1, BOARD_SIZE)])
        return board

    def __repr__(self):
        return 'GameBoard object:\n' + str(self)
