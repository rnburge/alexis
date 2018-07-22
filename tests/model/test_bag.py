from model.bag import Bag
from model.config import LETTER_DISTRIBUTIONS
import copy


def test_init():
    bag = Bag()


def test_get_tiles():
    bag = Bag()
    starting_num_of_tiles = len(bag.bag_tiles)
    assert starting_num_of_tiles == sum(LETTER_DISTRIBUTIONS)
    tiles = bag.get_tiles(10)
    assert len(tiles) == 10
    assert len(bag.bag_tiles) == starting_num_of_tiles - 10


def test_remaining_tiles():
    bag = Bag()
    starting_num_of_tiles = sum(LETTER_DISTRIBUTIONS)
    assert bag.remaining_tiles() == starting_num_of_tiles
    bag.get_tiles(10)
    assert bag.remaining_tiles() == starting_num_of_tiles - 10


def test_add_tiles():
    bag = Bag()
    starting_num_of_tiles = bag.remaining_tiles()
    tiles = bag.get_tiles(10)
    assert bag.remaining_tiles() == starting_num_of_tiles - 10
    bag.add_tiles(tiles)
    assert bag.remaining_tiles() == starting_num_of_tiles


def test_fill():
    bag = Bag()
    bag.bag_tiles.clear()
    assert bag.bag_tiles == []
    bag.fill()
    assert bag.remaining_tiles() == sum(LETTER_DISTRIBUTIONS)

    temp_distributions = copy.deepcopy(LETTER_DISTRIBUTIONS)
    for i in range(bag.remaining_tiles()):
        tile = bag.get_tiles(1)[0]
        temp_distributions[ord(tile) - 64] -= 1     # check off each letter as it is drawn

    assert temp_distributions.count(0) == len(temp_distributions) # all elements should now be zero


def test_str():
    pass
