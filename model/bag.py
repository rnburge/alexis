import random
from model.config import LETTER_DISTRIBUTIONS


class Bag:
    """ Represents a bag of game tiles. """

    def __init__(self):
        """ Create a new bag """
        self.bag_tiles = []
        self.fill()

    def get_tiles(self, tiles_to_draw):
        """ Get the specified number of tiles from the bag if enough remain
         (otherwise get all remaining tiles) """
        drawn_tiles = []
        tiles_to_draw = min(self.remaining_tiles(), tiles_to_draw)
        for i in range(0, tiles_to_draw):
            drawn_tiles.append(self.bag_tiles.pop(0))
        return drawn_tiles

    def remaining_tiles(self):
        """ returns the number of tiles remaining in the bag """
        return len(self.bag_tiles)

    def add_tiles(self, returned_tiles):
        """ returns the specified list of tiles to the bag """
        self.bag_tiles.extend(returned_tiles)
        random.shuffle(self.bag_tiles)

    def fill(self):
        """ fills the bag with its initial complement of tiles """
        self.bag_tiles.clear()

        # note blank tile is 'A'-1 or '@'
        for letter_ordinal in range(len(LETTER_DISTRIBUTIONS)):
            num_tiles = LETTER_DISTRIBUTIONS[letter_ordinal]
            for j in range(num_tiles):
                self.bag_tiles.append(chr(64 + letter_ordinal))
        random.shuffle(self.bag_tiles)

    def __str__(self):
        return ''.join([str(t) for t in self.bag_tiles])

    def __repr__(self):
        return 'Bag object containing the following tiles:\n' + str(self)