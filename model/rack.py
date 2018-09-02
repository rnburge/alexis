from model.config import RACK_SIZE, LETTER_VALUES
from model.bag import Bag
from collections import Counter
import numpy as np


class Rack:
    """ Represents a rack of game tiles. """

    def __init__(self, bag: Bag):
        """ Create a new rack with tiles from the argument bag """
        self.rack_tiles = []
        self.bag = bag
        self.replenish_tiles()

    def add_tiles(self, new_tiles):
        """ Add the supplied list of tiles to the rack """
        if (len(self.rack_tiles) + len(new_tiles)) > RACK_SIZE:
            raise ValueError("Too many tiles supplied")
        self.rack_tiles.extend(new_tiles)

    def add_tile(self, new_tile):
        """ Add the supplied tile to the rack """
        self.rack_tiles.append(new_tile)
        if len(self.rack_tiles) > RACK_SIZE:
            raise IndexError("Too many tiles in rack")

    def __str__(self):
        return ''.join([str(tile) for tile in self.rack_tiles])

    def get_tile(self, letter: str):
        """ Removes and returns the specified letter from the rack, raises a ValueError if not present """
        if letter in self.rack_tiles:
            return self.rack_tiles.pop(str(self).index(letter))
        elif letter.lower() in self.rack_tiles:
            return self.rack_tiles.pop(str(self).index(letter.lower()))
        elif '@' in self:
            self.rack_tiles.pop(str(self).index('@'))
            tile = letter.lower()
            return tile
        else:
            raise ValueError("No such letter as " + str(letter) + " in rack. Rack = " + str(self))

    def reset_blanks(self):
        for i in range(len(self)):
            if self.rack_tiles[i].islower():
                self.rack_tiles[i] = '@'

    def assign_blanks(self):
        while '@' in self:
            self.get_tile('@')
            vowels = 'EAOIU'
            consonants = 'SRTNLDGBMPHWFYCVKXJZQ'
            num_vowels = len([tile for tile in self.rack_tiles if tile in vowels])
            num_consonants = len([tile for tile in self.rack_tiles if tile in consonants])

            if num_consonants <= num_vowels:
                letter = [letter for letter in consonants if letter not in self][0].lower()
            else:
                letter = [letter for letter in vowels if letter not in self][0].lower()

            self.add_tile(letter)

    def __len__(self):
        return len(self.rack_tiles)

    def get_tiles(self, letters):
        """ Removes and returns the specified letters from the rack, raises a ValueError if not all present """
        found_tiles = []
        for letter in letters:
            found_tiles.append(self.get_tile(letter))
        if len(found_tiles) == len(letters):
            return found_tiles
        else:
            raise ValueError("Rack doesn't contain all those tiles")

    def replenish_tiles(self):
        tiles_needed = RACK_SIZE - len(self.rack_tiles)
        self.add_tiles(self.bag.get_tiles(tiles_needed))

    def contains(self, possible_contents: str, tiles_in_rack: str):
        if 1 == len(possible_contents):
            return possible_contents.upper() in tiles_in_rack.upper()
        elif '@' not in tiles_in_rack:
            if not set(possible_contents.upper()).issubset(set(str(self).upper())):
                return False
            else:
                return not Counter(possible_contents.upper()) - Counter(str(self).upper())
        else:
            # we have a blank
            # ditch a blank from hand we're checking:
            tiles_in_rack = tiles_in_rack.replace('@', '', 1)

            # convert string we're trying to match to numpy array:
            contents = np.array(list(possible_contents))

            # list comprehension creates all versions of the word we're looking for,
            # but missing one letter, then we see if any of them are contained
            # in remaining tiles (having two blanks is handled recursively):
            return any(
                [self.contains(''.join(contents[np.arange(len(contents)) != i]).upper(), tiles_in_rack)
                 for i in range(len(contents))]
            )

    def score_of_remaining_tiles(self):
        return np.sum([LETTER_VALUES[ord(tile) - 64] for tile in self.rack_tiles])

    def __contains__(self, possible_contents):
        if isinstance(possible_contents, str):
            return self.contains(possible_contents, str(self))

        if isinstance(possible_contents, list) and all(isinstance(t, str) for t in possible_contents):
            return ''.join([str(t) for t in possible_contents]) in self

        return False

    def __repr__(self):
        return 'Rack object containing the following tiles:\n' + ''.join(sorted(str(self)))

    def __eq__(self, other):
        return type(other) == type(self) and repr(other) == repr(self)

    def __hash__(self):
        return hash(repr(self))

