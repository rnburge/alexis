from model.tile import Tile, BlankTile


def test_create_tile():
    tile_a = Tile('A')
    tile_1 = Tile(1)
    assert tile_a == tile_1

def test_tile_get_index():
    tile = Tile('A')
    assert tile.indexInAlphabet == 1

def test_tile_get_letter():
    tile = Tile('A')
    assert tile.letter == 'A'

def test_tile_get_value():
    tile = Tile('A')
    assert tile.value == 1

def test_create_blank_tile():
    tile = BlankTile()

def test_assign_letter_to_blank():
    tile = BlankTile()
    tile.set_letter('F')
    assert tile.value == 0  # should still score zero
    assert tile.indexInAlphabet == 6
    assert tile.letter == 'f'