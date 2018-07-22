from model.config import Direction
from model.row import Row


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

        if not row:
            self.direction = Direction.NOT_APPLICABLE
            self.played_squares = None
        else:
            self.direction = self.row.direction
            self.played_squares = row.empty_squares(start_index)[:len(tiles)]
            self.is_valid = None

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
        return "Move: " + chr(64+col) + str(row) + ", " + str(self.direction) + ", tiles: " + letters + ", forms word: " + word + ", score: " + str(self.score)
