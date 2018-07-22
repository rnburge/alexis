import pytest

from model.bag import Bag
from model.rack import RACK_SIZE, Rack


def test_create_rack():
    rack = Rack(Bag())

def test_rack_size():
    rack = Rack(Bag())
    assert len(rack.rack_tiles) == RACK_SIZE

def test_add_too_many_tiles():
    rack = Rack(Bag())
    with pytest.raises(IndexError) as e_info:
        rack.add_tile('A') # adds tile to a new (hence full) rack

def test_get_a_tile_in_rack():
    rack = Rack(Bag())
    letter = rack.rack_tiles[0]
    assert len(rack.rack_tiles) == RACK_SIZE
    tile = rack.get_tile(letter)
    assert len(rack.rack_tiles) == (RACK_SIZE - 1)
    assert tile is not None
    assert tile == letter

def test_overflow_rack():
    rack = Rack(Bag())
    with pytest.raises(ValueError) as e_info:
        rack.add_tiles(['A', 'B'])
    assert len(rack.rack_tiles) == RACK_SIZE

def test_contents():
    rack = Rack(Bag())
    rack.rack_tiles = ['A','A','B','B','C','D','E']
    assert 'ABC' in rack
    assert 'AAB' in rack
    assert 'AAABBB' not in rack
    assert ['D', 'A', 'B'] in rack
    assert ['D', 'A','B', 'D'] not in rack

def test_replenish():
    rack = Rack(Bag())
    for i in range(13):
        rack.get_tiles(str(rack))
        assert len(rack.rack_tiles) == 0
        rack.replenish_tiles()
        assert len(rack.rack_tiles) == RACK_SIZE
    rack.get_tiles(str(rack))
    assert len(rack.rack_tiles) == 0
    rack.replenish_tiles()
    assert len(rack.rack_tiles) < RACK_SIZE

