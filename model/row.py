import numpy as np

from model.config import Direction, BOARD_SIZE
from util.bit_twiddling import set_bit, uint32_from_bool_array


class Row:
    """ Represents a row (or column) of the game board.
    Rows and columns are conceptually the same thing since
    the board can be transposed and the game will still work.
    So, 'row' here refers to this row (regardless of whether
    it is oriented horizontally or vertically on the game board),
    and 'column' refers to the row orthogonal to this one"""

    def __init__(self, direction: Direction, rank: int, row_data):
        """ creates a row slice of the game board """
        self.direction = direction
        self.rank = rank
        self.hook_squares = row_data[0]
        self.word_multipliers = row_data[1]
        self.letter_multipliers = row_data[2]
        self.existing_letters = row_data[3]
        self.existing_letter_scores = row_data[4]
        self.this_row_crosschecks = row_data[5]
        self.this_row_cross_scores = row_data[6]
        self.orthogonal_column_crosschecks = row_data[7]
        self.orthogonal_column_cross_scores = row_data[8]

    def square_is_empty(self, index_of_square):
        return not self.existing_letters[index_of_square]

    def empty_squares(self, index_of_square=0):
        """ :return array with indices of empty squares in this row (starting from the given index if supplied)"""
        return np.where(self.existing_letters[index_of_square:] == 0)[0] + index_of_square

    def start_of_word(self, index_of_square):
        """ :param index_of_square the index of any letter in the word
        :return the index of the first letter in the word
        """
        if len(self.empty_squares()) == 0 or self.empty_squares()[0] >= index_of_square:  # no empty square precedes this one
            return 1
        return np.where(self.existing_letters[:index_of_square] == 0)[0][-1] + 1  # one over from index of last empty square

    def squares_in_word(self, index):
        start_square = self.start_of_word(index)
        empties = self.empty_squares(index)  # all empty squares after word
        end_square = BOARD_SIZE if len(empties) == 0 else empties[0]  # last square on board else first empty square
        return np.arange(start_square, end_square)

    def squares_in_potential_word(self, index):
        """ returns squares that would be in a word formed if a tile was placed at the given index """
        start_square = self.start_of_word(index)
        empties = self.empty_squares(index)  # all empty squares after word
        end_square = (BOARD_SIZE - 1) if len(empties) == 0 else empties[0]  # last square on board else first empty square
        if index in empties and (index + 1) not in empties and index < (BOARD_SIZE - 1):
            end_square = self.squares_in_word(index+1)[-1] + 1
        return np.arange(start_square, end_square)

    def word_at(self, index):
        return ''.join([chr(i + 64) for i in self.existing_letters[self.squares_in_word(index)]])

    def update_hooks_and_running_scores(self, index):
        """ updates the empty squares at either end of whichever word contains the letter at the supplied index.
        Calculates running scores and valid letters and caches them in these squares """

        try:
            start_square = self.squares_in_word(index)[0]
        except Exception as ex:
            print("Something exploded: " + str(ex))

        end_square = self.squares_in_word(index)[-1]

        squares_to_update = []

        if start_square > 1:  # there's only a previous empty square if we're not at the starting edge of the board
            squares_to_update.append(start_square - 1)

        if end_square < (BOARD_SIZE - 1):  # there's only a next empty square if we're not at the far edge of the board
            squares_to_update.append(end_square + 1)

        self.hook_squares[self.squares_in_word(index)] = False
        self.hook_squares[squares_to_update] = True

        self.orthogonal_column_cross_scores[squares_to_update] \
            = np.sum(self.existing_letter_scores[self.squares_in_word(index)])

    def place_tiles(self, played_squares, tiles):
        tile_ordinals = [(ord(t)-64) for t in tiles]
        np.put(self.existing_letters, played_squares, tile_ordinals)

    def remove_tiles(self, played_squares):
        self.existing_letters[played_squares] = 0

    def __str__(self):
        # DEBUG:
        return self.debug_row_string()  # DEBUG

        row_num = '  '
        if self.rank % BOARD_SIZE == 0:
            row = '+' + ('-' * (BOARD_SIZE - 1)) + '+'
        else:
            rank = self.rank if self.direction == Direction.HORIZONTAL else chr(64 + self.rank)
            row_num = ' ' * (2 - len(str(rank))) + str(rank)
            row = '|' + ('.' * (BOARD_SIZE - 1)) + '|'
            row = ''.join(np.where(self.letter_multipliers == 2, "'", list(row)))
            row = ''.join(np.where(self.letter_multipliers == 3, '"', list(row)))
            row = ''.join(np.where(self.word_multipliers == 2, '-', list(row)))
            row = ''.join(np.where(self.word_multipliers == 3, '=', list(row)))
            letters = [chr(x + 64) for x in self.existing_letters]
            row = ''.join(np.where(self.existing_letters > 0, letters, list(row)))
        return row_num + ' ' + ' '.join(row)

    def row_string_showing_hooks(self):
        row_num = '  '
        if self.rank % BOARD_SIZE == 0:
            row = '+' + ('-' * (BOARD_SIZE - 1)) + '+'
        else:
            rank = self.rank if self.direction == Direction.HORIZONTAL else chr(64 + self.rank)
            row_num = ' ' * (2 - len(str(rank))) + str(rank)
            row = '|' + ('.' * (BOARD_SIZE - 1)) + '|'
            row = ''.join(np.where(self.letter_multipliers == 2, "'", list(row)))
            row = ''.join(np.where(self.letter_multipliers == 3, '"', list(row)))
            row = ''.join(np.where(self.word_multipliers == 2, '-', list(row)))
            row = ''.join(np.where(self.word_multipliers == 3, '=', list(row)))
            row = ''.join(np.where(self.hook_squares, '*', list(row)))
            letters = [chr(x + 64) for x in self.existing_letters]
            row = ''.join(np.where(self.existing_letters > 0, letters, list(row)))
        return row_num + ' ' + ' '.join(row)

    def debug_row_string(self):
        row_num = '  '
        if self.rank % BOARD_SIZE == 0:
            row = '+' + ('-' * (BOARD_SIZE - 1)) + '+'
        else:
            rank = self.rank if self.direction == Direction.HORIZONTAL else chr(64 + self.rank)
            row_num = ' ' * (2 - len(str(rank))) + str(rank)
            row = '|' + ('.' * (BOARD_SIZE - 1)) + '|'
            row = ''.join(np.where(self.letter_multipliers == 2, "'", list(row)))
            row = ''.join(np.where(self.letter_multipliers == 3, '"', list(row)))
            row = ''.join(np.where(self.word_multipliers == 2, '-', list(row)))
            row = ''.join(np.where(self.word_multipliers == 3, '=', list(row)))
            row = ''.join(np.where(self.hook_squares, '*', list(row)))
            letters = [chr(x + 64) for x in self.existing_letters]
            row = ''.join(np.where(self.existing_letters > 0, letters, list(row)))
        return row_num + ' ' + ' '.join(row)

    def __repr__(self):
        return 'row object:\n'+str(self)

    def __eq__(self, other):
        return type(other) == type(self) \
               and str(self) \
               + str(self.this_row_crosschecks) \
               + str(self.this_row_cross_scores) \
               == str(other) \
               + str(other.this_row_crosschecks) \
               + str(other.this_row_cross_scores)

    def __hash__(self):
        return hash(str(self)
                    + str(self.this_row_crosschecks)
                    + str(self.this_row_cross_scores))
