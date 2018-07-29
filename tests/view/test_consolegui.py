from model.config import Direction
from view.consolegui import ConsoleGui
from model.humanplayer import HumanPlayer
from model.bag import Bag
from controller.game import GameController


def test_create_gui():
    players = [None, None]
    bag = Bag()
    game = GameController(players, bag)
    gui = ConsoleGui(game)


def test_parse_move_string():
    bag = Bag()
    game = GameController([None, None], bag)
    gui = ConsoleGui(game)
    player1 = HumanPlayer(bag, gui, "Player 1")
    player2 = HumanPlayer(bag, gui, "Player 2")
    game.players = [player1, player2]
    game.active_player = player1
    player1.rack.rack_tiles[0] = 'A'
    player1.rack.rack_tiles[1] = 'C'
    player1.rack.rack_tiles[2] = 'T'
    move = gui.parse_move_string('F8HCAT')
    assert move.row.direction == Direction.HORIZONTAL
    assert move.row.rank == 8
    assert len(move.played_squares) == 3
    assert all([a == b for a, b in zip(move.played_squares, [6,7,8])])
    assert len(move.tiles) == 3
    assert all([a == b for a, b in zip(move.tiles, ['C', 'A', 'T'])])
