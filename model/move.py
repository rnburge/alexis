from model.config import Direction
from model.row import Row
import numpy as np
from model.config import LETTER_VALUES, NO_CROSS_WORD, RACK_SIZE, BONUS


class Move:
    """ Represents a game move. """

    def __init__(self, row: Row, start_index: int, tiles):
        """ Creates a game move. None of the supplied parameters
        are relevant if this is a passing move, and only the list
        of tiles is relevant for a tile exchange move. 'None' should
        be passed in place of any parameters which do not apply.

        :param row: The row the move is played in
        :param start_index: The starting index in the row
        :param tiles: a list of tiles being played
        """

        self.row = row
        self.start_index = start_index
        self.tiles = tiles
        self.is_valid = None

        if not row:
            self.direction = Direction.NOT_APPLICABLE
            self.played_squares = None
        else:
            self.direction = self.row.direction
            self.played_squares = row.empty_squares(start_index)[:len(tiles)]

        # score will be None when not yet calculated:
        self.score = None

    def cross_direction(self):
        """ :return: the direction orthogonal to the move's direction of play """
        if self.direction == Direction.VERTICAL:
            return Direction.HORIZONTAL
        elif self.direction == Direction.HORIZONTAL:
            return Direction.VERTICAL
        else:
            return Direction.NOT_APPLICABLE

    def calculate_score(self):
        tile_values = [(LETTER_VALUES[(ord(t)-64)] if t.isupper() else LETTER_VALUES[0]) for t in self.tiles]
        squares_in_whole_word = self.row.squares_in_word(self.start_index)

        # store score of new tiles on board:
        np.put(self.row.existing_letter_scores, self.played_squares, tile_values)

        # total letters in word (including letter multipliers)
        self.score = np.sum((self.row.existing_letter_scores * self.row.letter_multipliers)[squares_in_whole_word])

        # multiply whole thing by cumulative word multipliers of played squares:
        self.score *= np.prod(self.row.word_multipliers[self.played_squares])
        # add scores of cross-words
        self.score += np.sum(np.where(
            self.row.this_row_cross_scores != NO_CROSS_WORD,
            ((self.row.existing_letter_scores * self.row.letter_multipliers
              + self.row.this_row_cross_scores) * self.row.word_multipliers),
            np.zeros(17))[self.played_squares])
        # add bonus if we played a full rack of tiles
        if len(self.played_squares) == RACK_SIZE:
            self.score += BONUS

        # NB: word and letter multipliers will be changed to 1,
        # the identity for multiplication, if and when this word
        # gets played and not removed.

    def __str__(self):
        if self.direction == Direction.NOT_APPLICABLE:
            return "Move: Exchange " + str(self.tiles) if self.tiles else "Move: pass"

        if self.direction == Direction.HORIZONTAL:
            row = self.row.rank
            col = self.start_index
        else:
            row = self.start_index
            col = self.row.rank

        letters = ''.join([str(t) for t in self.tiles])
        word = self.row.word_at(self.start_index)
        return "Move: " + chr(64+col) + str(row) + ", " \
               + str(self.direction) \
               + ", tiles: " + letters \
               + ", forms word: " + word \
               + ", score: " + str(self.score)

    def __repr__(self):
        return 'Move object:\n'+str(self)